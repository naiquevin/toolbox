#!/usr/bin/env python

import os
import sys
import subprocess

"""Python script to create nightly package builds from a git repo

It takes a url to a git repository, clones the repo, fetches all
submodules (even submodules of the submodules) and packages them
into a tar archive

The primary reason for writing this was that the github's download
button doesn't yet support including the submodule files but instead
keeps the submodule directories empty. This script attempts to fix
this.
"""

CLONE_DIR = '/tmp'


def clone_repo(url, into=CLONE_DIR):
    # clone the git repo
    run_command('git clone %s' % url, cwd=into)

    # return the path to the cloned repo on the system
    return os.path.join(into, os.path.basename(url).rstrip('.git'))


def find_submodules(repopath):
    # change dir to the cloned repo
    os.chdir(repopath)
    submodule_dirs = []
    # search recursively for .gitmodules files
    for root, dirnames, filenames in os.walk(repopath):
        for filename in filenames:
            if filename == '.gitmodules':
                submodule_dirs.append(root)
    return submodule_dirs


def fetch_submodules(submodule_dirs):
    # loop through each submodule dir, cd into it and issue the
    # submodule init and update commands
    for smdir in submodule_dirs:
        run_command('git submodule update --init', smdir)

    # return the list of submodules fetched successfully.
    return submodule_dirs


def package(repopath, archivepath):
    # create an archive of all files in the repo now
    # at the location specified by the archivepath
    basename = os.path.basename(repopath)
    dirname = os.path.dirname(repopath)
    archivename = '%s.tar.gz' % basename
    run_command('tar czf %s %s/' % (archivename, basename),
                dirname)
    
    # return the location of the archive
    return os.path.join(dirname, archivename)


def run_command(command, cwd):
    proc = subprocess.Popen(command,
                            cwd=cwd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True) # can be safely assumed to be safe!
    print 'Executing command: %s' % command
    (output, error) = proc.communicate()
    if output:
        print 'Command output: %s' % output
    if error:
        print 'Command error: %s' % error
    return output


if __name__ == '__main__':
    script, repourl = sys.argv
    archivepath = CLONE_DIR # same for now
    repopath = clone_repo(repourl)
    fetched = []
    unfetched = find_submodules(repopath)
    while unfetched:
        fetched.extend(fetch_submodules(unfetched))

        # run find_submodules again for the new dir tree filtering out
        # those which are already fetched
        unfetched = [x for x in find_submodules(repopath) if x not in fetched]
        
    archived_at = package(repopath, archivepath)
    print 'Nightly Package created at %s' % archived_at
    print 'Thanks!'
    

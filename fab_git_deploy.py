"""fabfile template for git based deployment workflows

It assumes that a remote with post_receive hook is configured on the
server(s) and public key ssh access for the user is set. Similarly a
local tracking branch is set from which code will be pushed to the
remotes on the servers to be deployed to

To deploy to staging , run::

    $ fab staging:develop prepare_deploy

This will start deployment and will merge develop branch in the
tracking branch for staging env (configured in the fab file itself)
and push code.
"""

from functools import wraps
from fabric.api import local, env, task, settings, cd, prefix, run
from fabric.colors import yellow, red, green


env.use_ssh_config = True


@task
def staging(branch):
    """Setup the deployment env to be staging.

    This command needs to be run before any other command that depends
    on the env.

    :usage: $ fab staging:develop
    """
    env.hosts = [] # add hosts here
    env.from_branch = branch # branch from which to upload code
    env.tracking_branch = 'to-staging' # this tracking branch is assumed to be set
    env.remote = 'staging' # git remote for this env
    env.remote_dir = '/path/to/dir/on/remote'
    env.venv_name = 'myproject'
    env.deploy_log_file = '/path/to/deploys.log'
    env.committer = committer_signature()
    local('git checkout %s' % env.from_branch)


@task
def production():
    """Setup the deployment env to be production.

    This command needs to be run before any other command that depends
    on the env
    """
    print(red('Production deployment isn\'t configured yet'))
    # configure prod env similar to staging above with one change that
    # instead of allowing the user to specify the `from_branch` hard
    # code your "always-stable" branch here


def env_required(func):
    """Decorator to stop a function from running if the deployment
    environment is not set. Decorate all such functions with this
    """
    @wraps(func)
    def dec(*args, **kwargs):
        if len(env.hosts) == 0:
            print(red("Error: Command '%s' needs env to be specified."))
            print(yellow("Run the command as $ fab <env_name> %s" % (func.__name__,)))
            exit(1)
        return func(*args, **kwargs)
    return dec


@task
@env_required
def prepare_deploy():
    """Set of tasks to be done before deployment.

    eg. running tests, minifying assets etc.
    """
    test()
    prompt_next(deploy)


@task
@env_required
def deploy():
    """Deploy the code"""
    local("git checkout %s" % env.tracking_branch)
    local("git pull")
    old_commit = current_commit_hash()
    local("git merge %s" % env.from_branch)
    new_commit = current_commit_hash()
    local("git push %s" % env.remote)
    local("git checkout %s" % env.from_branch)
    prompt_next(post_deploy, old_commit=old_commit, new_commit=new_commit)


@task
@env_required
def post_deploy(old_commit=None, new_commit=None):
    """Set of tasks to be done post deployment

    eg. Running db migrations etc.
    """
    print(green('Executing post deployment tasks'))
    with cd(env.remote_dir), prefix('. /usr/local/bin/virtualenvwrapper.sh; workon {}'.format(env.venv_name)):
        # run commands such as django's migrations, collectstatic or
        # any other commands depending upon the framework here. Also,
        # don't forget to touch the uwsgi.ini (uwsgi+nginx) or wsgi.py
        # (apache2+mod_wsgi) file add code as applicable

        # finally update the deploy logs ie. append a line to the
        # deploy log file with info such as when and by whom the code
        # was deployed as well as the old and new commit hashes (can
        # be helpful in case code needs to be rolled back to previous
        # stable state)
        if old_commit != new_commit:
            run((
                'echo "{old_commit} -> {new_commit}'
                ' by {committer}'
                ' at `date`"'
                ' >> {deploy_log}'
            ).format(old_commit=old_commit,
                     new_commit=new_commit,
                     committer=env.committer,
                     deploy_log=env.deploy_log_file))


@task
def test():
    """Run tests"""
    print(yellow('Running tests'))
    # call the test command here appropriately


def is_work_tree_dirty():
    with settings(warn_only=True):
        result = local('git diff --quiet')
        return result.return_code == 1


def current_commit_hash():
    return local("git rev-parse --short HEAD", capture=True)


def committer_signature():
    name = local("git config user.name", capture=True)
    email = local("git config user.email", capture=True)
    return '{} <{}>'.format(name, email)


def prompt_next(func, **kwargs):
    """Function to chain together various tasks. The user is prompted
    whether to execute the next task in line
    """
    func_name = func.__name__
    print
    ques = "Proceed to the next step (%s)? [y/n] " % (func_name,)
    ans = raw_input(ques)
    if ans in ('y', 'Y'):
        func(**kwargs)
    else:
        print(red('You chose to stop! Please run the next steps manually to complete deployment'))

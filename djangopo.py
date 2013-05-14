import os
import re
from fnmatch import fnmatch
from itertools import groupby
from functools import wraps

import polib

# global, expected to be specified in sys.argv
basedir = None


def find_pofile_paths(basedir):
    pofiles = []
    for root, dirs, files in os.walk(basedir):
        pofiles.extend(os.path.join(root, f) for f in files if fnmatch(f, '*.po'))
    return pofiles


def write(grouped_entries):
    for lang, entries in grouped_entries:
        print
        print('=== %s ===' % lang)
        print
        for entry in entries:
            print entry
            print


def groupby_lang(func):
    @wraps(func)
    def dec(*args, **kwargs):
        f = lambda e: e.lang_code
        return groupby(sorted(func(*args, **kwargs), key=f), f)
    return dec


def list_command(func):
    @wraps(func)
    def dec():
        global basedir
        pofiles = (polib.pofile(f) for f in find_pofile_paths(basedir))
        write(get_entries(pofiles, func));
    return dec


class WrappedPOEntry(object):

    lang_code_pattern = re.compile(r'locale/([a-z_A-Z]+)/LC_MESSAGES')

    def __init__(self, po_entry, fpath):
        self._po_entry = po_entry
        self.fpath = fpath

    @property
    def lang_code(self):
        m = self.lang_code_pattern.search(self.fpath)
        if m is not None:
            return m.groups()[0]
        else:
            raise Exception('Not a locale path')

    def __getattr__(self, attr):
        return getattr(self._po_entry, attr)

    def __unicode__(self):
        values = {'flags': ','.join(self.flags),
                  'fpath': self.fpath,
                  'msgid': self.msgid,
                  'msgstr': self.msgstr if self.msgstr else '<???>'}
        return '\n'.join(['[%(flags)s]',
                          '[File]: %(fpath)s',
                          '[Orig]: %(msgid)s',
                          '[Trans]: %(msgstr)s']) % values

    def __str__(self):
        return self.__unicode__().encode('utf-8')


@groupby_lang
def get_entries(pofiles, pred=None):
    for po in pofiles:
        for e in po:
            if pred is not None and pred(e):
                yield WrappedPOEntry(e, po.fpath)


def by_fext(entry, fext):
    return any(os.path.splitext(o[0])[1] == '.py' for o in entry.occurrences)


@list_command
def list_non_translated(entry):
    return not entry.translated() and entry.obsolete != 1


@list_command
def list_obsolete(entry):
    return entry.obsolete == 1


@list_command
def list_py_text(entry):
    return by_fext(entry, '.py')


@list_command
def list_js_text(entry):
    return by_fext(entry, '.js')


@list_command
def list_html_text(entry):
    return by_fext(entry, '.js')


if __name__ == '__main__':
    import sys
    script, subcommand, basedir = sys.argv
    if locals().get(subcommand) is not None:
        locals().get(subcommand)()
    else:
        print('Command %s not defined' % subcommand)

"""A tool to work with language trans files (.po) in a django project

Author: Vineet Naik <naikvin@gmail.com>, <vineet.naik@kodeplay.com>

This script is a utility for working with .po files in a django
project in which many languages are to be supported and so for any new
text introduced the translation files for all languages are to be
updated.

To get translated strings, it uses the mymemory api, more info about
the same can be obtained from here -
http://mymemory.translated.net/doc/spec.php

"""

import os
import re
from fnmatch import fnmatch
from itertools import groupby
from functools import wraps

import requests
import polib


# global, expected to be specified in sys.argv
basedir = None

# edit this before running the code
mymemory_email = None

_commands = set()

lang_code_pattern = re.compile(r'locale/([a-z_A-Z]+)/LC_MESSAGES')


def find_pofile_paths(basedir):
    pofiles = []
    for root, dirs, files in os.walk(basedir):
        pofiles.extend(os.path.join(root, f) for f in files if fnmatch(f, '*.po'))
    return pofiles


def lang_code_from_path(fpath):
    m = lang_code_pattern.search(fpath)
    if m is not None:
        return m.groups()[0].lower().replace('_', '-')
    else:
        raise Exception('Not a locale path')


### Code for listing various types of po entries to stdout

def write(grouped_entries):
    for lang, entries in grouped_entries:
        if lang != 'en':
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


def entries(func):
    @wraps(func)
    def dec():
        global basedir
        pofiles = (polib.pofile(f) for f in find_pofile_paths(basedir))
        return get_entries(pofiles, func);
    return dec


def command(func):
    global _commands
    _commands.add((func.__name__, func.__doc__))
    return func


class WrappedPOEntry(object):

    def __init__(self, po_entry, fpath):
        self._po_entry = po_entry
        self.fpath = fpath

    @property
    def lang_code(self):
        return lang_code_from_path(self.fpath)

    def __getattr__(self, attr):
        return getattr(self._po_entry, attr)

    def set_trans(self, trans):
        self._po_entry.msgstr = trans

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
    return (WrappedPOEntry(e, po.fpath)
            for po in pofiles
            for e in po
            if pred is not None and pred(e))


def by_fext(entry, fext):
    return any(os.path.splitext(o[0])[1] == fext for o in entry.occurrences)


@entries
def get_non_translated(entry):
    return not entry.translated() and entry.obsolete != 1


@entries
def get_non_translated_non_fuzzy(entry):
    return not entry.translated() and entry.obsolete != 1 and 'fuzzy' not in entry.flags


@entries
def get_obsolete(entry):
    return entry.obsolete == 1


@entries
def get_py_text(entry):
    return by_fext(entry, '.py')


@entries
def get_js_text(entry):
    return by_fext(entry, '.js')


@entries
def get_html_text(entry):
    return by_fext(entry, '.js')


@command
def list_non_translated():
    write(get_non_translated())


@command
def list_non_translated_non_fuzzy():
    write(get_non_translated_non_fuzzy())


@command
def list_obsolete():
    write(get_obsolete())


### Code for getting translations for text from MyMemory
### http://mymemory.translated.net/doc/spec.php

class MyMemoryTransError(Exception):
    pass


def mymemory_translate(msgid, to_lang, from_lang='en'):
    assert mymemory_email is not None, 'Please provide an email to use mymemory api'
    req = requests.get('http://api.mymemory.translated.net/get',
                       params={'q': msgid,
                               'langpair': '%s|%s' % (from_lang, to_lang),
                               'de': mymemory_email})
    if req.status_code == 200:
        return req.json['responseData']['translatedText']
    else:
        raise MyMemoryTransError('Request to translate %r failed with status code %d' % (msgid, req.status_code))


@command
def translate_non_translated_non_fuzzy():
    entries = get_non_translated_non_fuzzy()
    for lang, entries in entries:
        if lang != 'en':
            print
            print('=== %s ===' % lang)
            print
            for entry in entries:
                try:
                    trans = mymemory_translate(entry.msgid, to_lang=lang)
                    entry.set_trans(trans)
                except (MyMemoryTransError, requests.exceptions.RequestException) as e:
                    print e
                finally:
                    print entry
                    print


### Code for writing to the po files. To be used with care.

@command
def remove_fuzzy_flags():
    pofiles = (polib.pofile(f) for f in find_pofile_paths(basedir))
    for po in pofiles:
        num_fuzzy = 0
        for entry in po.fuzzy_entries():
            num_fuzzy += 1
            entry.flags.remove('fuzzy')
        po.save()
        if num_fuzzy > 0:
            print '%d fuzzy flags removed from %s' % (num_fuzzy, po.fpath)
    print 'DONE!'


@command
def translate_new_and_save():
    pofiles = (polib.pofile(f) for f in find_pofile_paths(basedir))
    for po in pofiles:
        num = 0
        lang = lang_code_from_path(po.fpath)
        if lang == 'en':
            continue
        for entry in po.untranslated_entries():
            try:
                trans = mymemory_translate(entry.msgid, to_lang=lang)
            except (MyMemoryTransError, requests.exceptions.RequestException) as e:
                print e
            else:
                num += 1
                entry.msgstr = trans
        po.save()
        if num > 0:
            print '%d new translations added to %s' % (num, po.fpath)
    print 'DONE!'


def remove_obsolete():
    pass # how to do this using polib?


if __name__ == '__main__':
    import sys
    script, subcommand, basedir, email = sys.argv
    mymemory_email = email
    if locals().get(subcommand) is not None:
        locals().get(subcommand)()
    else:
        print('Command %s not defined' % subcommand)

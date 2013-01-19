#!/usr/bin/env python

import sys
import os
import re


def usage():
    return """
======================================================================
Command line tool to split a huge apache2 log file into smaller chunks
by date
======================================================================

Author: Vineet Naik <naikvin@gmail.com> @naiquevin

Usage
=====

For splitting log file

    $ python splitlogs.py <filepath> <date_criteria>

      filepath: absolute path to the log file
      date_criteria: of format */*/* (eg. 06/Nov/*, */Nov/*)      

For running tests

    $ python splitlogs.py test

For help

    $ python splitlogs.py help

"""


def parse_criteria(criteria):
    day, month, year = criteria.split('/')
    return dict((('day', '\d{2}' if day == '*' else day),
                ('month', '[A-Za-z]' if month == '*' else month.title()),
                ('year', '\d{4}' if year == '*' else year)))


def get_criteria_pattern(crt, logtype='access'):
    if logtype == 'error':
        pattern = re.compile(r'^\[.+\s%s\s%s\s.+\s%s\]\s.+' % (crt['month'], crt['day'], crt['year']))
    else:
        pattern = re.compile(r'^.*\[%s\/%s\/%s.+$' % (crt['day'], crt['month'], crt['year']))
    return pattern


def test():
    c = parse_criteria('*/nov/*')
    assert c['day'] == '\d{2}'
    assert c['month'] == 'Nov'
    assert c['year'] == '\d{4}'

    cp = get_criteria_pattern(c)
    log = '183.82.25.178 - - [08/Nov/2012:13:15:05 +0000] "GET /favicon.ico HTTP/1.1" 404 503 "-" "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:16.0) Gecko/20100101 Firefox/16.0"'
    assert cp.match(log) is not None

    print 'tests: ok'


def handle_subcommand(argv):
    try:
        subcommand = argv[1]
    except IndexError:
        subcommand = 'help'
    if subcommand == 'test':
        test()
    else:
        print usage()
    exit(0)


if __name__ == '__main__':
    try:
        logfile, criteria = sys.argv[1:3]
        try:
            logtype = sys.argv[3]
        except IndexError:
            logtype = 'access'
    except ValueError:
        handle_subcommand(sys.argv)

    pattern = get_criteria_pattern(parse_criteria(criteria), logtype)
    with open(os.path.abspath(logfile)) as f:
        lines = f
        lines = (line for line in lines if pattern.match(line) is not None)
        print ''.join(list(lines))


#!/usr/bin/env python

import sys
import re
import os

__doc__ = """
SqlDiff Tool

Simple command line tool for finding the difference 
between two mysql databases w.r.t no. of tables in each 
using their respective sql dump files.

Usage: $ python sqldiff.py db1.sql db2.sql

"""

TABLE_MATCH_PATTERN = re.compile(r'^CREATE TABLE IF NOT EXISTS `(.+)`.*$')

dash = '-' * 72

def tablenames(lines):
    for line in lines:
        m = TABLE_MATCH_PATTERN.search(line)
        if m is not None:
            yield m.group(1)
        

def tables(db):
    lines = (line for line in open(db) if line.startswith('CREATE TABLE'))
    tables = tablenames(lines)
    return tables


def diff_tables(db1, db2):
    t1 = set(tables(db1))

    t2 = set(tables(db2))

    if t1.isdisjoint(t2):
       raise NothingToCompare

    def dbname(filename):
        return os.path.splitext(os.path.basename(filename))[0]

    db1_name, db2_name = map(dbname, [db1, db2])

    print dash
    print 'SqlDiff Results'
    print dash

    print 'Table counts: '
    print_table_counts(db1_name, len(t1))
    print_table_counts(db2_name, len(t2))

    print dash

    db1_extra = t1 - t2
    db2_extra = t2 - t1

    print 'Diff:'
    print_diff_counts(db1_name, db2_name, len(db1_extra))
    print_diff_tables(db1_extra)
    print_diff_counts(db2_name, db1_name, len(db2_extra))
    print_diff_tables(db2_extra)

    print '\n'    


def print_table_counts(db, c):
    print "%s* %d tables found in %s" % (' '*4, c, db)


def print_diff_counts(db1, db2, c):
    print '%s* %s has %d tables more than %s' % (' '*4, db1, c, db2)


def print_diff_tables(tbls):
    if len(tbls) > 0:
        print '\n'.join([' '*8 + str(n) + ' ' + s 
                         for s, n in 
                         zip(tbls, range(1, len(tbls)+1))])

        
class NothingToCompare(Exception):
    pass


if __name__ == '__main__':
    try:
        script, db1, db2 = sys.argv
        diff_tables(db1, db2)
        print dash
        print 'Hope it helped you :-) Bye!'
        print dash
    except NothingToCompare:
        print 'Two databases are totally dissimilar. Wrong tool for the job?'
    except IOError, e:
        print 'Error opening one of the files', e
    except Exception:
        print __doc__


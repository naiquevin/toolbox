"""A simple CSV to JSON converter

Usage: dopt.py (-i | FILE) [-q QUOTECHAR -d DELIMITER]
       dopt.py -h | --help | --version

Options:
    -h --help     Show help
    -d DELIMITER  specify csv delimiter [default: ,]
    -q QUOTECHAR  specify csv quotechar [default: |]

"""

#! Important: The docstring format is significant as it's being used
#! to parse command line args using docopt

import sys
import csv
import json

from docopt import docopt


def read_csv(f, delimiter, quotechar):
    reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
    rows = [r for r in reader]
    columns = rows.pop(0)
    return [dict(zip(columns, row)) for row in rows]


if __name__ == '__main__':
    args = docopt(__doc__, version='1.0')

    if args['FILE']:
        with open(args['FILE'], 'rb') as f:
            data = read_csv(f, args['-d'], args['-q'])
    elif args['-i']:
        data = read_csv(sys.stdin.readlines(), args['-d'], args['-q'])

    print json.dumps(data)


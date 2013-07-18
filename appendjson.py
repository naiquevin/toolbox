"""Script to append multiple json files into a single json string

Usage: python appendjson.py <f1> <f2> <f3> ... <fn>

The resulting string may then be piped to json.tool for indenting for
directly redirected to a file for writing to it.

"""

import sys
import json
from functools import reduce


def appendjson(filepaths):
    """List of filepaths -> list of data from all files as json string"""
    lof = map(open, filepaths)
    loj = (json.load(f) for f in lof)
    data = json.dumps(reduce(lambda x, y: x + y, loj, []))
    for f in lof:
        f.close()
    return data


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) == 0 or (len(args) == 1 and args[0] in ['-h', '--help']):
        sys.stdout.write(__doc__)
    else:
        filepaths = args
        sys.stdout.write(appendjson(filepaths))


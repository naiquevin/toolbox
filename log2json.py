"""A command line script to convert log files to json

For help, run following command in terminal::

    $ python log2json -h

"""


import argparse
import re
import sys
from contextlib import contextmanager
import json


LOG_PATTERNS = {
    'apache2_access': re.compile(
        r'^(?P<ip>[0-9.]+)\s'
        r'-\s-\s'
        r'\[(?P<datetime>.+)\]\s'
        r'"(?P<method>(GET|POST|PUT|UPDATE|HEAD))\s'
        r'(?P<path>.+)\s'
        r'HTTP/1.1"\s'
        r'(?P<status_code>\d{3})\s'
        r'(?P<content_size>\d+)\s'
        r'"(?P<referrer>.+)"\s'
        r'"(?P<user_agent>.+)"$'
    ),
}


@contextmanager
def source(filepath, stdin):
    """Contextmanager that gets a file like object as source

    If filepath is not None, then it will open the file and return the
    file object. In the end, takes care of closing it. Reads standard
    input if stdin is True Raises an exception if both above cases
    fail

    """
    if filepath is not None:
        f = open(filepath)
        yield f
        f.close()
    elif stdin:
        yield sys.stdin.readlines()
    else:
        raise argparse.ArgumentError(args.filepath, (
            'At least one of log file path or'
            'input from stdin is required'
        ))


def get_pattern(pattern_arg):
    """Get a predefined or a newly compiled re pattern

    If the `pattern_arg` exists as a key in the predefined patterns,
    will return it, otherwise considers the pattern_arg argument as
    the string pattern and returns the compiled SRE_Pattern object

    :param pattern_arg: str
    :rtype: SRE_Pattern object

    """
    if pattern_arg in LOG_PATTERNS:
        return LOG_PATTERNS[pattern_arg]
    else:
        return re.compile(pattern_arg)


def parse_line(line, pattern):
    """Parses a single line using pattern

    :param line: str
    :param pattern: SRE_Pattern object
    :rtype: dict
    """
    match = pattern.match(line)
    if match is not None:
        return match.groupdict()
    else:
        pass # do logging here


def convert(args):
    """The `convert` subcommand"""
    pattern = get_pattern(args.pattern)
    with source(args.filepath, args.stdin) as lines:
        sys.stdout.write(json.dumps([parse_line(line, pattern)
                                     for line in lines
                                     if line.strip() != '']))


def list_patterns(args):
    """The `list_patterns` subcommand"""
    title = 'List patterns'
    print title
    print '=' * len(title)
    print
    for k, v in LOG_PATTERNS.iteritems():
        print('{key}: {value}'.format(key=k, value=v.pattern))
        print


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('subcommand', help='subcommand',
                        nargs='?', default='convert')
    parser.add_argument('-f', '--filepath',
                        help='path to the log file')
    parser.add_argument('-i', '--stdin',
                        help='Use standard input', action='store_true')
    parser.add_argument('-p', '--pattern',
                        help=(
                            'Regex pattern or name of a '
                            'predefined pattern for parsing logs'
                        ), default='apache2_access')
    args = parser.parse_args()

    if args.subcommand == 'convert':
        convert(args)

    if args.subcommand == 'list_patterns':
        list_patterns(args)


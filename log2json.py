"""A command line script to convert log files to json

For help, run following command in terminal::

    $ python log2json -h

"""

import datetime
import argparse
import re
import sys
import json

import cli
from dateutil import tz, parser as dateparser


LOG_PATTERNS = {
    'apache2_access': re.compile(
        r'^(?P<ip>[0-9.]+)\s'
        r'-\s-\s'
        r'\[(?P<datetime>.+)\]\s'
        r'"(?P<method>(GET|POST|PUT|UPDATE|HEAD))\s'
        r'(?P<path>.+)\s'
        r'HTTP/(?P<http_ver>(1.1|1.0))"\s'
        r'(?P<status_code>\d{3})\s'
        r'(?P<content_size>\d+)\s'
        r'"(?P<referrer>.+)"\s'
        r'"(?P<user_agent>.+)"$'
    ),
}


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


def datetime_to_timestamp(dt):
    """Converts a utc timezone aware datetime object to utc timestamp"""
    epoch = datetime.datetime(1970, 1, 1).replace(tzinfo=tz.tzutc())
    return (dt - epoch).total_seconds()


def parse_line(line, pattern):
    """Parses a single line using pattern

    :param line: str
    :param pattern: SRE_Pattern object
    :rtype: dict
    """
    match = pattern.match(line)
    if match is not None:
        log = match.groupdict()
        # convert status_code to int
        log['status_code'] = int(log['status_code'])
        # convert log time to utc timestamp and add to dict
        dt = dateparser.parse(log['datetime'], fuzzy=True)
        log['timestamp'] = datetime_to_timestamp(dt)
        return log
    else:
        return None # throw some warning here may be


def convert(args):
    """The `convert` subcommand"""
    pattern = get_pattern(args.pattern)
    try:
        with cli.read_input(args.filepath, args.stdin) as lines:
            logs = (parse_line(line, pattern)
                    for line in lines
                    if line.strip() != '')
            sys.stdout.write(json.dumps([log for log in logs if log is
                                         not None]))
    except cli.CliError as e:
        raise argparse.ArgumentError(args.filepath, str(e))


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
    parser.add_argument('subcommand', help='subcommand ( convert | list_patterns )',
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


"""A command line script to split large log files by date

   Author: Vineet Naik <naikvin@gmail.com>

"""

import re
import argparse
import cli


LOG_PATTERN_FORMATS = {
    'apache2_access': r'^.*\[{day}\/{month}\/{year}.+',
    'apache2_error': r'^\[.+\s{month}\s{day}\s.+\s{year}\]\s.+'
}


def parse_date(date):
    """Extract out day/month/year from the date wildcard pattern as a dict

    :param date: str of type */*/* eg. */Jun/*

    :rtype: dict

    """
    day, month, year = date.split('/')
    return dict((('day', '\d{2}' if day == '*' else day),
                ('month', '[A-Za-z]' if month == '*' else month.title()),
                ('year', '\d{4}' if year == '*' else year)))


def get_date_pattern(date_pattern, log_type='apache2_access'):
    """Get the correct regex pattern to match date from the logs

    :param date_pattern: dict

    :param log_type: type of logs

    :rtype: SRE_Pattern object

    """
    return re.compile(LOG_PATTERN_FORMATS[log_type].format(**date_pattern))


def split(f, pattern):
    return (line for line in f  if pattern.match(line) is not None)


def main(args):
    pattern = get_date_pattern(parse_date(args.date), args.log_type)

    try:
        with cli.read_input(args.filepath, args.stdin) as f:
            print ''.join(split(f, pattern))
    except cli.CliError as e:
        raise argparse.ArgumentError(args.filepath, str(e))


def test():
    """Tests (Use nosetests to run them)"""
    c = parse_date('*/nov/*')
    assert c['day'] == '\d{2}'
    assert c['month'] == 'Nov'
    assert c['year'] == '\d{4}'

    cp = get_date_pattern(c)
    log = '183.82.25.178 - - [08/Nov/2012:13:15:05 +0000] "GET /favicon.ico HTTP/1.1" 404 503 "-" "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:16.0) Gecko/20100101 Firefox/16.0"'
    assert cp.match(log) is not None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('date', help='Wild card pattern for date eg. 06/Nov/*, */Nov/*')
    parser.add_argument('-f', '--filepath',
                        help='path to the log file')
    parser.add_argument('-i', '--stdin',
                        help='Use standard input', action='store_true')
    parser.add_argument('-t', '--log-type',
                        help=(
                            'Regex pattern or name of a '
                            'predefined log pattern format for parsing logs'
                        ), default='apache2_access',
                        choices=LOG_PATTERN_FORMATS.keys())

    args = parser.parse_args()
    main(args)


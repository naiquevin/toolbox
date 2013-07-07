"""Analyse the urls in log files

Usage: logan.py ( -i | FILE ) [ -p PATTERN_FILE ]
       logan.py ( -h | --help | --version )

Options:
  -h --help
  -i --stdin
  -p PATTERN_FILE --pattern_file=PATTERN_FILE

"""

## Important: This script uses docopt for argument parsing and hence
## is __doc__ sensitive!

import re
import json
from collections import Counter
from urlparse import urlparse
from docopt import docopt

import cli


def path_pattern(path, pattern):
    """Finds a pattern of the path and returns it if found else returns
    the path

    :param path: string
    :param pattern: compile regex pattern
    :rtype: str

    """
    # stip out query string if it exists
    path = urlparse(path).path
    match = pattern.match(path)
    if match is not None:
        for k, v in match.groupdict().iteritems():
            path = path.replace(v, '<%s>' % (k,))
    return path


def dynamic_urls(logs, patterns=None):
    """Extract dynamic urls from the logs using the urlconf and print them

    :param logs: list of dicts
    :param patterns: list of strings [default: None]
    :rtype: collections.Counter

    """
    patterns = [] if patterns is None else map(re.compile, patterns)
    paths = []
    for log in logs:
        path = log['path']
        for p in patterns:
            path = path_pattern(path, p)
        paths.append((log['method'], path))
    return Counter(paths)


def print_to_stdout(url_counts):
    """Prints the url anaylsis to stdout

    :param url_counts: collections.Counter
    :rtype: None

    """
    print 'Total hits: %d' % (sum(url_counts.values()),)
    print '====' * 20
    sortedkeys = sorted(url_counts, key=lambda x: url_counts[x],
                        reverse=True)
    for k in sortedkeys:
        print('[%s] - %s: %d' % (k[0], k[1], url_counts[k]))


def test():
    u1 = '/feedapi/19fa3dce8a68667ef47214c18579b59fad174470/products/?page=1'
    p1 = re.compile('/feedapi/(?P<appid>\\w+)/products/')
    assert path_pattern(u1, p1) == '/feedapi/<appid>/products/'
    assert path_pattern('/shopper/widget-init/', p1) == '/shopper/widget-init/'


if __name__ == '__main__':
    args = docopt(__doc__)

    if args['--pattern_file']:
        with open(args['--pattern_file']) as f:
            patterns = json.load(f)
    else:
        patterns = None

    with cli.read_input(args['FILE'], args['--stdin']) as f:
        url_counts = dynamic_urls(json.load(f), patterns)
        print_to_stdout(url_counts)


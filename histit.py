"""A script to quickly create histograms from data in text files

Usage: histit.py ( show | save ) ( -i | FILE ) -t TITLE -x XLABEL [ -d DTYPE -b BINS ]
       histit.py -h | --help | --version

Options:
    -t --title TITLE      Title of the histogram
    -x --xlabel XLABEL    The x-axis label
    -d --datatype DTYPE   Datatype [default: int]
    -b --bins BINS        No. of bins [default: 10]
    -h --help             Show help
    --version             Show version

"""

import os
import sys

from docopt import docopt
import matplotlib.pyplot as plt

from cli import read_input


def plot_hist(data, title, xlabel, bins):
    n, bins, patches = plt.hist(list(data), bins, facecolor="g")
    plt.xlabel(xlabel)
    plt.ylabel('frequency')
    plt.title(title)
    return plt


def coerce_lines(lines, datatype):
    f = {'int': int, 'float': float}[datatype]
    return (f(x) for x in lines)


def main(args):
    with read_input(args['FILE'], args['-i']) as f:
        data = coerce_lines(f, args['--datatype'])
        plt = plot_hist(data, args['--title'], args['--xlabel'], int(args['--bins']))
        if args['show']:
            plt.show()
        elif args['save']:
            target = '{0}.png'.format(os.path.splitext(args['FILE'])[0])
            plt.savefig(target)
            print('Saved to {target}'.format(target=target))
        return 0


if __name__ == '__main__':
    args = docopt(__doc__, version=1.0)
    sys.exit(main(args))

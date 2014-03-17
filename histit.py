"""A script to quickly create histograms from data in text files

usage: histit.py [-h] [-d DATAFILE] [-a {show,save}] [-t {int,float}]
                 [-b BINS]
                 title xlabel

positional arguments:
  title                 The title of the histogram
  xlabel                The label on the X-axis

optional arguments:
  -h, --help            show this help message and exit
  -d DATAFILE, --datafile DATAFILE
                        Path to the input datafile
  -a {show,save}, --action {show,save}
                        The action to carry out
  -t {int,float}, --type {int,float}
                        Type of input on each line expected
  -b BINS, --bins BINS  No. of bins

"""

import os
import sys
import select
import argparse

import matplotlib.pyplot as plt


def plot_hist(data, title, xlabel, bins):
    n, bins, patches = plt.hist(list(data), bins, facecolor="g")
    plt.xlabel(xlabel)
    plt.ylabel('frequency')
    plt.title(title)
    return plt


def cast_to_type(lines, datatype):
    f = {'int': int, 'float': float}[datatype]
    return (f(x) for x in lines)


def stdin_has_data():
    return select.select([sys.stdin,],[],[],0.0)[0]


def DataError(Exception):
    pass


def main(args):
    if args.datafile:
        with open(os.path.abspath(args.datafile)) as f:
            lines = [x.strip() for x in f]
    elif stdin_has_data():
        lines = [x.strip() for x in sys.stdin]
    else:
        raise DataError('No data/data source specified. Either datafile or stdin is required')

    data = cast_to_type(lines, args.type)
    plt = plot_hist(data, args.title, args.xlabel, int(args.bins))
    if args.action == 'show':
        plt.show()
    elif args.action == 'save':
        target = '{0}.png'.format(args.title)
        plt.savefig(target)
        print('Saved to {target}'.format(target=target))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("title", help="The title of the histogram")
    parser.add_argument("xlabel", help="The label on the X-axis")
    parser.add_argument("-d", "--datafile", help="Path to the input datafile")
    parser.add_argument("-a", "--action", choices=['show', 'save'], help="The action to carry out", default="show")
    parser.add_argument("-t", "--type", choices=['int', 'float'], default='int', help="Type of input on each line expected")
    parser.add_argument("-b", "--bins", type=int, default=10, help="No. of bins")
    args = parser.parse_args()
    sys.exit(main(args))

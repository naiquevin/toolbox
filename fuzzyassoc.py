"""Dictionary-key association with fuzzy matching

Usage: fuzzyassoc.py match DATAFILE KEYSFILE [-r FUZZYRATIO]
       fuzzyassoc.py assoc DATAFILE MATCHFILE
       fuzzyassoc.py -h | --help | --version

Options:
    -r FUZZYRATIO  fuzzy matching ratio threshold [default: 80]
    -h --help      Show help
    --version      Show version
"""

from itertools import chain

import os
import json
import yaml

from fuzzywuzzy import process
from docopt import docopt


def getext(fp):
    return os.path.splitext(fp)[1]


def read_data(fp):
    ext = getext(fp)
    if ext == '.json':
        return json.load(open(fp))
    elif ext in ['.yaml', '.yml']:
        return yaml.load(open(fp))
    else:
        raise Exception('Unsupported format: "{}"'.format(ext))


def write_data(data, ext):
    if ext == '.json':
        return json.dumps(data, indent=4)
    elif ext in ['.yaml', '.yml']:
        return yaml.dump(data, default_flow_style=False)
    else:
        raise Exception('Unsupported format: "{}"'.format(ext))


def fuzzy_match_keys(newkeys, keys, ratio_threshold):
    keys_set = set(keys)
    newkeys_set = set(newkeys)
    samekeys = keys_set.intersection(newkeys_set)
    diffkeys = newkeys_set.difference(keys_set)
    keymap = ((nk, process.extract(nk, keys)) for nk in diffkeys)
    keymap1 = ((nk, [k for k,r in m if r > ratio_threshold])
               for nk, m in keymap)
    keymap2 = ((nk, m) for nk, m in keymap1 if len(m) > 0)
    return samekeys, keymap2


def cmd_match(datafile, keysfile, ratio_threshold=80):
    data = read_data(datafile)
    keys = [line.strip() for line in open(keysfile)]
    samekeys, diffkeymap = fuzzy_match_keys(data.keys(), keys, ratio_threshold)
    result = {k: [k] for k in samekeys}
    result.update({str(k): map(str, v) for k, v in diffkeymap})
    print(write_data(result, getext(datafile)))


def assoc_by_matches(data, matches):
    keymap = chain.from_iterable([(x, k) for x in v] for k, v in matches.iteritems())
    return {k: data[v] for k, v in keymap if data[v] is not None}


def cmd_assoc(datafile, matchfile):
    print(write_data(assoc_by_matches(read_data(datafile),
                                      read_data(matchfile)),
                     getext(datafile)))


def main(args):
    try:
        if args['match']:
            cmd_match(args['DATAFILE'], args['KEYSFILE'], int(args['-r']))
        elif args['assoc']:
            cmd_assoc(args['DATAFILE'], args['MATCHFILE'])
    except:
        return 1
    else:
        return 0


if __name__ == '__main__':
    exit(main(docopt(__doc__)))

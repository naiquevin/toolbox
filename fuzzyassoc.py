"""Dictionary-key association with fuzzy matching

Usage: fuzzyassoc.py match DATAFILE KEYSFILE [-r FUZZYRATIO]
       fuzzyassoc.py assoc DATAFILE KEYSFILE
       fuzzyassoc.py -h | --help | --version

Options:
    -r FUZZYRATIO  specify csv delimiter [default: 80]
    -h --help      Show help
    --version      Show version
"""

import json

from fuzzywuzzy import process
from docopt import docopt


def fuzzy_match_keys(data, keys, ratio_threshold):
    newkeys = data.keys()
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
    data = json.load(open(datafile))
    keys = [line.strip() for line in open(keysfile)]
    samekeys, diffkeymap = fuzzy_match_keys(data, keys, ratio_threshold)
    for k in samekeys:
        print(k)
    print('---')
    for nk, matches in diffkeymap:
        print(nk)
        for m in matches:
            print(' '*4 + m)


def lines_to_keymap(lines):
    def loop(acc, line):
        if line.startswith('---'):
            acc['current'] = None
            return acc
        if line.startswith(' '*4):
            line = line.strip()
            current = acc['current']
            if current is not None:
                acc['keymap'].pop(current, None)
                acc['keymap'][line] = current
                return acc
            else:
                raise Exception('Bad format: {}'.format(line))
        else:
            line = line.strip()
            acc['keymap'][line] = line
            acc['current'] = line
            return acc
    return reduce(loop, lines, {'keymap': {}, 'current': None})['keymap']


def assoc_by_matches(data, keymap):
    return {k: data[v] for k, v in keymap.iteritems() if data[v] is not None}


def cmd_assoc(datafile, keymapfile):
    print(json.dumps(assoc_by_matches(json.load(open(datafile)),
                                      lines_to_keymap(open(keymapfile))),
                     indent=4))


def main(args):
    try:
        if args['match']:
            cmd_match(args['DATAFILE'], args['KEYSFILE'], int(args['-r']))
        elif args['assoc']:
            cmd_assoc(args['DATAFILE'], args['KEYSFILE'])
    except:
        return 1
    else:
        return 0


if __name__ == '__main__':
    exit(main(docopt(__doc__)))

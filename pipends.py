import sys
from itertools import chain

import pip


def name_version(name, version):
    return '{name} [{version}]'.format(name=name, version=version)


def req_version(dist):
    try:
        return ''.join(dist.specs[0])
    except IndexError:
        return ''


def get_installed():
    return pip.get_installed_distributions()


def get_deps_set(pkgs):
    return set(chain.from_iterable((x.key for x in p.requires()) for p in pkgs))


def render_tree(pkgs):
    key_pkg_map = {p.key: p for p in pkgs}
    deps = get_deps_set(pkgs)
    top_pkgs = [p for p in pkgs if p.key not in deps]
    def aux(pkg, indent=0):
        if pkg.key in deps:
            result = [' '*indent + '- ' + name_version(pkg.key, req_version(pkg))]
        else:
            result = [name_version(pkg.key, pkg.version)]
        if pkg.key in key_pkg_map:
            pkg_deps = key_pkg_map[pkg.key].requires()
            if pkg_deps:
                result += list(chain.from_iterable([aux(d, indent=indent+2)
                                                    for d in pkg_deps]))
        return result
    return '\n'.join(chain.from_iterable([aux(p) for p in top_pkgs]))


def main():
    print(render_tree(get_installed()))
    return 0


if __name__ == '__main__':
    sys.exit(main())

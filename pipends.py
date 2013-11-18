import pip


def name_version(name, version):
    return '{name} [{version}]'.format(name=name, version=version)


def req_version(dist):
    try:
        return ''.join(dist.specs[0])
    except IndexError:
        return ''


def get_dependencies():
    return {name_version(p.key, p.version): [name_version(d.key, req_version(d))
                                             for d in p.requires()]
            for p in pip.get_installed_distributions()}


if __name__ == '__main__':
    for pkg, reqs in get_dependencies().iteritems():
        print(pkg)
        for r in reqs:
            print(' - {}'.format(r))

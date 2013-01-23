#!/usr/bin/env python

import sys
import re
from collections import Counter


requests_pattern = re.compile(r'^.+\s-\s-\s\[.+\]\s"(GET|POST|PUT|UPDATE|HEAD)\s(.+)\sHTTP/1.1"\s200.+$')


def regexp_match_urls(line, pattern):
    m = pattern.match(line)
    if m is not None:
        return m.groups()
    else:
        return None


def strip_query(url):
    return url.split('?')[0]


def build_dynamic_pattern(url, pattern):
    match = pattern.match(url)
    if match is not None:
        for k, v in match.groupdict().iteritems():
            newurl = url.replace(v, '<%s>' % (k,))
        return newurl
    return url


def extract_request_urls(lines, dynamic_patterns=None, ignore_qs=True):
    groups = (regexp_match_urls(x, requests_pattern) for x in lines)
    groups = (g for g in groups if g is not None)
    if ignore_qs:
        groups = ((g[0], strip_query(g[1])) for g in groups)
    if dynamic_patterns:
        for pattern in dynamic_patterns:
            groups = [(g[0], build_dynamic_pattern(g[1], pattern)) for g in groups]
    return Counter(groups)


def request_urls(logfile):
    dynamic_patterns = map(re.compile, ['/shopper/(?P<appid>\w+)/chat/',
                                        '/feedapi/(?P<appid>\w+)/products/'])
    with open(logfile) as f:
        url_counter = extract_request_urls(f, dynamic_patterns=dynamic_patterns, ignore_qs=True)
        print 'Total hits: %d' % (sum(url_counter.values()),)
        sortedkeys = sorted(url_counter, key=lambda x: url_counter[x], reverse=True)
        for k in sortedkeys:
            print('(%s) -> %s: %d' % (k[0], k[1], url_counter[k]))
    

def test():
    print 'Running tests ..'
    samplelogs = """66.91.244.220 - - [21/Jan/2013:00:00:00 +0000] "GET /jsi18n/ HTTP/1.1" 200 2456 "http://kodecrm.com/shopper/bdd396b42cf50ddd2ab4672336ef8724cf2ef4e1/chat/" "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0_1 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A523 Safari/8536.25"
98.243.111.46 - - [21/Jan/2013:00:00:00 +0000] "GET /static/vendor/blitzer/jquery-ui-1.8.11.custom.css HTTP/1.1" 200 6457 "http://kodecrm.com/shopper/423f4c9ab67508506faca353e235c412604d1b57/chat/" "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"
98.243.111.46 - - [21/Jan/2013:00:00:00 +0000] "GET /static/vendor/bootstrap/img/glyphicons-halflings-white.png HTTP/1.1" 200 9071 "http://www.edressme.com/" "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"
94.164.60.230 - - [21/Jan/2013:00:00:00 +0000] "GET /shopper/ad50a99b5d9c827cca4a1eaf8d66549556582304/chat/ HTTP/1.1" 200 4583 "http://www.carnevaleveneziano.it/Costume-Carnevale-5-adulto/collezione-uomo/Costume-Carnevale-5123-pirata-lusso" "Mozilla/5.0 (iPad; CPU OS 6_0_1 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A523 Safari/8536.25"
66.91.244.220 - - [21/Jan/2013:00:00:00 +0000] "GET /jsi18n/ HTTP/1.1" 200 2456 "http://kodecrm.com/shopper/bdd396b42cf50ddd2ab4672336ef8724cf2ef4e1/chat/" "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0_1 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A523 Safari/8536.25"
88.15.75.5 - - [21/Jan/2013:23:59:54 +0000] "GET /shopper/widget-init/?callback=_kcrm_jsonp&app_id=065a48e0db5e3894bc4605db4dad8ea658f5a904&siteurl=http%3A%2F%2Fwww.monanimal.net%2Findex.php%2Fanimales%2Fcachorros HTTP/1.1" 200 653 "http://www.monanimal.net/index.php/animales/cachorros" "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17"
70.193.4.3 - - [21/Jan/2013:23:59:48 +0000] "GET /shopper/widget-init/?callback=_kcrm_jsonp&app_id=edc8a4104902f3e1fc1b197c63673ffeb83399a9&siteurl=http%3A%2F%2Fwww.motionsavers.com%2Fvestil%2Fergonomic-worker-chairs-7647.html HTTP/1.1" 200 650 "http://www.motionsavers.com/vestil/ergonomic-worker-chairs-7647.html" "Mozilla/5.0 (Windows NT 5.1; rv:18.0) Gecko/20100101 Firefox/18.0"
94.164.60.230 - - [21/Jan/2013:00:00:00 +0000] "GET /shopper/11111a99b5d9c827cca4a1eaf8d66549556582304/chat/ HTTP/1.1" 200 4583 "http://www.carnevaleveneziano.it/Costume-Carnevale-5-adulto/collezione-uomo/Costume-Carnevale-5123-pirata-lusso" "Mozilla/5.0 (iPad; CPU OS 6_0_1 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A523 Safari/8536.25"
"""
    lines = samplelogs.split('\n')
    dynamic_patterns = map(re.compile, ['/shopper/(?P<appid>\w+)/chat/'])
    url_counter = extract_request_urls(lines, dynamic_patterns=dynamic_patterns)
    assert len(url_counter) == 5
    assert url_counter[('GET', '/jsi18n/')] == 2
    assert url_counter[('GET', '/static/vendor/blitzer/jquery-ui-1.8.11.custom.css')] == 1
    print 'All tests pass.'


if __name__ == '__main__':
    subcommand = sys.argv[1]
    if subcommand == 'test':
        test()
    elif subcommand == 'request_urls':
        try:
            logfile = sys.argv[2]
        except IndexError:
            print 'Help!'
        request_urls(logfile)
    else:
        print 'Help!'

import re
from collections import defaultdict
import datetime

pattern = re.compile(r'(?i).+(query\t(select|update|insert|delete).+)\n')


def match_query(line):
    m = pattern.match(line) 
    if m is not None:
        return m.groups()[0]
    return None


def format_query(line):
    return line.lower().replace('query\t', '').replace('\t', ' ')


def aggregate(queries):
    agg = defaultdict(int)
    for q in queries:
        agg[q] += 1
    qs, counts = agg.keys(), agg.values()
    new_agg = sorted(zip(counts, qs), reverse=True)
    return new_agg


def as_html(queries):
    return """<!DOCTYPE html>
<html>
  <head>
    <style type="text/css">
      {css}
    </style>
  </head>
  <body>
    <div class="container">
      <h1>Mysql General log analysis at {date}</h1>
      <table>
         {rows}
      </table>
    </div>
  </body>
</html>
""".format(css='.container { width: 1200px; } table { width: 100%; border: 1px solid #ddd; table-layout: fixed; word-wrap: break-word; } td { width: 90%; border: 1px solid #ddd; border-collapse: collapse; } td+td { width: 9%; }',
           date=str(datetime.datetime.now()),
           rows='\n'.join(['<tr><td>%s</td><td>%s</td></tr>' % (q, c) for c, q in queries]))


def as_txt(queries):
    return ['%s -> %d' % (q, c) for q, c in queries]


if __name__ == '__main__':
    with open('/home/vineet/errorlogs/mysql/mysql.log') as f:
        queries = (format_query(q) for 
                   q in (match_query(line) for line in f)
                   if q is not None)
        agg = aggregate(queries)
    print as_html(agg)
    
        


import csv
import json


def read_csv(filename):
    rows = []
    with open(filename, 'rb') as f:
        reader = csv.reader(f, delimiter=',', quotechar='|')
        for row in reader:
            rows.append(row)
    columns = rows.pop(0)
    return [dict(zip(columns, row)) for row in rows]


if __name__ == '__main__':
    import sys
    script, input_file = sys.argv
    data = read_csv(input_file)
    print json.dumps(data)


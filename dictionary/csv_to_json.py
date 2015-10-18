# Run with: python -m dictionary.init_fixture

import sys
import json

from json_to_csv import FIELDS, MODEL
from alutiiq import get_pos, get_root, normalize

# sources_fixture should already exist.
sources_fixture = 'dictionary/fixtures/sources.json'


def convert_null(value):
    if value == '<NULL>':
        return None
    else:
        return value

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        print 'Usage: csv_to_json.py [sources_fixture] < input.csv > output.json'
        print 'Default values:'
        print '    sources_fixture = %s' % (sources_fixture,)
        sys.exit(2)

    if len(sys.argv) >= 2:
        sources_fixture = sys.argv[2]

    fixture = []
    for line in sys.stdin:
        line = line[:-1]
        tabs = line.count('\t')
        if tabs > len(FIELDS):
            print 'Malformed line:'
            print repr(line)
            continue
        elif tabs < len(FIELDS):
            line += '\t' * (len(FIELDS) - tabs)

        values = line.split('\t')
        fields = {field: convert_null(value) for field, value in zip(FIELDS, values)}

        fixture.append({
            'model': MODEL,
            'pk': None,
            'fields': fields,
        })

    json.dump(fixture, sys.stdout, indent=4, separators=(',', ': '))

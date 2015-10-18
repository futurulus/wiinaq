# Run with: python -m dictionary.init_fixture

import sys
import json

MODEL = 'dictionary.chunk'
FIELDS = [
    'entry',
    'pos_auto',
    'pos_final',
    'root_auto',
    'root_final',
    'defn',
    'source',
    'source_info',
    'search_text',
]


def convert_null(val):
    if val is None:
        return '<NULL>'
    else:
        return unicode(val)


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        print 'Usage: json_to_csv.py < input.json > output.csv'
        sys.exit(2)

    fixture = json.load(sys.stdin)

    for chunk in fixture:
        if chunk['model'].lower() != MODEL:
            continue

        fields = chunk['fields']
        print('\t'.join([convert_null(fields[f]) for f in FIELDS]).encode('utf-8'))

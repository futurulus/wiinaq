"""
Run as: python postbases.py < pb.mdf > pb.csv
"""
import csv
import sys

FIELD_TAGS = {
    'src': 'name',
    'lx': 'formula',
    'se': 'formula',
    'sse': 'formula',
    'ssse': 'formula',
    'sssse': 'formula',
    'xr': 'formula',
    'ro': 'formula',
    'att': 'pos',
    'fnc': 'term',
    'de': 'definition',
}
FIELDS = ['name', 'formula', 'pos', 'term', 'definition']

def compile_postbases():
    row = {f: [] for f in FIELDS}

    writer = csv.DictWriter(sys.stdout, fieldnames=FIELDS, quoting=csv.QUOTE_ALL)
    writer.writeheader()

    past_src = False
    past_att = False

    while True:
        try:
            line = input()
        except (EOFError, IOError, KeyboardInterrupt):
            break

        cols = line.split(None, 1)
        if len(cols) != 2:
            continue

        tag, value = cols
        tag = tag.lstrip('\\')
        if tag in FIELD_TAGS:
            if row['name'] and tag != 'src':
                past_src = True
            elif tag == 'src' and past_src:
                writer.writerow({f: '\n'.join(vals) for f, vals in row.items()})
                past_src = False
                past_att = False
                row = {f: [] for f in FIELDS}
            if row['pos'] and tag != 'att':
                past_att = True
            elif tag == 'att' and past_att:
                writer.writerow({f: '\n'.join(vals) for f, vals in row.items()})
                past_att = False
                row['definition'] = []
                row['pos'] = []

            row[FIELD_TAGS[tag]].append(value)

    if past_src or row['name']:
        writer.writerow({f: '\n'.join(vals) for f, vals in row.items()})


if __name__ == '__main__':
    compile_postbases()

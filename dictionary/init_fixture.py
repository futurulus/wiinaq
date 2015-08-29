#!/usr/bin/env python
import sys
import json

from alutiiq import get_pos, get_root

words_file = 'dict_sources/words.csv'
output_fixture = 'dictionary/fixtures/words.json'

if len(sys.argv) >= 4:
    print 'Usage: init_db.py [words_file [output_fixture]]'
    print 'Default values:'
    print '    words_file = %s' % (words_file,)
    print '    output_fixture = %s' % (output_fixture,)
    sys.exit(2)

if len(sys.argv) >= 3:
    output_fixture = sys.argv[2]

if len(sys.argv) >= 2:
    words_file = sys.argv[1]


fixture = []
with open(words_file, 'r') as infile:
    for line in infile:
        line = line[:-1]
        tabs = line.count('\t')
        if tabs > 4:
            print 'Malformed line:'
            print line
            continue
        elif tabs < 4:
            line += '\t' * (4 - tabs)
        entry, notes, defn, source, alts = line.split('\t')
        pos = get_pos(entry, defn)
        root = get_root(entry, defn)
        fixture.append({
            'model': 'dictionary.Chunk',
            'pk': len(fixture) + 1,
            'fields': {
                'entry': entry,
                'pos_auto': pos,
                'pos_final': pos,
                'root_auto': root,
                'root_final': root,
                'defn': defn,
                'source': source,
                'search_text': '%s %s' % (entry, defn),
            },
        })


with open(output_fixture, 'w') as outfile:
    json.dump(fixture, outfile, indent=4, separators=(',', ': '))

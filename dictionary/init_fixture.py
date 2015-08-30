#!/usr/bin/env python
import sys
import json

from alutiiq import get_pos, get_root, normalize

words_file = 'dict_sources/words.csv'
output_fixture = 'dictionary/fixtures/words.json'
# Note that output_fixture will be created, but sources_fixture
# should already exist.
sources_fixture = 'dictionary/fixtures/sources.json'

if len(sys.argv) >= 4:
    print 'Usage: init_fixture.py [words_file [sources_fixture [output_fixture]]]'
    print 'Default values:'
    print '    words_file = %s' % (words_file,)
    print '    output_fixture = %s' % (output_fixture,)
    sys.exit(2)

if len(sys.argv) >= 4:
    output_fixture = sys.argv[2]

if len(sys.argv) >= 3:
    sources_fixture = sys.argv[2]

if len(sys.argv) >= 2:
    words_file = sys.argv[1]


SOURCES = {}
with open(sources_fixture, 'r') as infile:
    sources_json = json.load(infile)
    for source in sources_json:
        SOURCES[source['fields']['abbrev']] = source['pk']


def parse_source(source):
    tokens = source.split()
    if tokens and tokens[0] in SOURCES:
        return SOURCES[tokens[0]], ' '.join(tokens[1:])
    else:
        return None, ' '.join(tokens)


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
        source_pk, source_info = parse_source(source)
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
                'source': source_pk,
                'source_info': source_info,
                'search_text': '%s %s' % (normalize(entry), defn),
            },
        })


with open(output_fixture, 'w') as outfile:
    json.dump(fixture, outfile, indent=4, separators=(',', ': '))

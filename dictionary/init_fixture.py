# Run with: python -m dictionary.init_fixture

import sys
import json

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()

from models import Chunk

words_file = 'dictionary/fixtures/words.csv'
sources_fixture = 'dictionary/fixtures/sources.json'
# Note that output_fixture will be created, but sources_fixture
# and words_file should already exist.
output_fixture = 'dictionary/fixtures/words.json'

pk_null = False

if len(sys.argv) >= 5:
    print 'Usage: init_fixture.py [words_file [sources_fixture [output_fixture]]]'
    print 'Default values:'
    print '    words_file = %s' % (words_file,)
    print '    output_fixture = %s' % (output_fixture,)
    sys.exit(2)

if len(sys.argv) >= 4:
    output_fixture = sys.argv[3]
    pk_null = True

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
            print repr(line)
            continue
        elif tabs < 4:
            line += '\t' * (4 - tabs)
        entry, notes, defn, source, alts = line.split('\t')
        source_pk, source_info = parse_source(source)
        c = Chunk(entry=entry, defn=defn)
        c.fill()
        fixture.append({
            'model': 'dictionary.Chunk',
            'pk': (None if pk_null else (len(fixture) + 1)),
            'fields': {
                'entry': c.entry,
                'pos_auto': c.pos_auto,
                'pos_final': c.pos_final,
                'root_auto': c.root_auto,
                'root_final': c.root_final,
                'defn': c.defn,
                'source': source_pk,
                'source_info': source_info,
                'search_text': c.search_text,
            },
        })


with open(output_fixture, 'w') as outfile:
    json.dump(fixture, outfile, indent=4, separators=(',', ': '))

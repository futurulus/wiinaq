# -*- coding: utf-8 -*-
import random
import re
import binascii
import itertools
from collections import namedtuple

from django.db import connection
from django.db.models import Max
from django.http import Http404
from django.shortcuts import get_list_or_404, redirect, render
from django.template.defaultfilters import urlencode
from django.urls import reverse
from django.views.generic.base import RedirectView

from .models import Entry as EntryModel, Source as SourceModel
from .alutiiq import inflection_data, normalize


ALUTIIQ_SUBDIR = '/ems/'

SEARCH_LIMIT = 1000

if connection.vendor == 'mysql':
    SOW = '(^|[[:space:][:punct:]])'
    EOW = '($|[[:space:][:punct:]])'
elif connection.vendor == 'postgresql':
    SOW = r'\m'
    EOW = r'\M'
else:
    SOW = EOW = r'\b'


def subdir(view):
    def redirect_to_subdir(request, *args, **kwargs):
        if request.path.startswith(ALUTIIQ_SUBDIR):
            new_view = view
        else:
            print(repr(urlencode(request.path)))
            new_view = RedirectView.as_view(url=ALUTIIQ_SUBDIR[:-1] +
                                            urlencode(request.path).replace('%', '%%'),
                                            # why is this used as a Python format string???
                                            query_string=True)
        return new_view(request, *args, **kwargs)

    return redirect_to_subdir


def index(request):
    return search(request)


@subdir
def credits(request):
    return render(request, 'dictionary/credits.html',
                  {'sources': SourceModel.objects.order_by('ordering', 'id'),
                   'url': request.build_absolute_uri(request.get_full_path())})


@subdir
def entry(request, word):
    chunks = get_list_or_404(EntryModel, entry=word, hidden=False)
    entries = group_entries(chunks, separate_roots=True)
    assert len(entries) == 1
    context = {'word': word,
               'roots': [{'root': root.root,
                          'pos': root.pos,
                          'id': root.id,
                          'inflections': inflection_data(root),
                          'sources': root.sources}
                         for root in entries[0].roots],
               'url': request.build_absolute_uri(request.get_full_path()),
               'request': request}
    return render(request, 'dictionary/entry.html', context)


MAX_RANDOM_TRIES = 100


@subdir
def random_entry(request):
    max_id = EntryModel.objects.aggregate(Max('id'))['id__max']
    random_entry = None
    for _ in range(MAX_RANDOM_TRIES):
        random_id = random.randint(0, max_id)
        try:
            random_entry = EntryModel.objects.get(id=random_id)
            break
        except EntryModel.DoesNotExist:
            pass

    if random_entry is None:
        raise Http404
    else:
        return redirect('entry', word=random_entry.entry)


def build(request):
    return search(request)


def remove_parens(s):
    return re.sub(r'\([^)]+\)', '', s)


Entry = namedtuple('Entry', ['word', 'roots'])
Root = namedtuple('Root', ['word', 'pos', 'root', 'id', 'defns', 'sources'])
Source = namedtuple('Source', ['source', 'senses'])
Sense = namedtuple('Sense', ['chunks', 'defn', 'sources', 'examples',
                             'etymologies', 'comments',
                             'main_entries', 'subentries', 'see_also'])


def chunk_relevance(chunk, query):
    query_l = query.lower()
    query_fuzzy = normalize(query)

    score = 0

    # Return results in the reverse of the following order:

    # Beginning or end definition match inside parens
    without_parens = remove_parens(chunk.defn)
    inside_parens = ' '.join(re.findall(r'(?<=\()[^)]+(?=\))', chunk.defn))
    if re.search(r'\b%s' % re.escape(query_l), inside_parens) or \
            re.search(r'%s\b' % re.escape(query_l), inside_parens):
        score = 10

    # Beginning or end outside of parens
    if re.search(r'\b%s' % re.escape(query_l), without_parens) or \
            re.search(r'%s\b' % re.escape(query_l), without_parens):
        score = 20

    # Whole-word definition match inside parens
    if re.search(r'\b%s\b' % re.escape(query_l), inside_parens):
        score = 30

    # Beginning or end of Alutiiq word with spelling correction
    if re.search(r'\b%s' % re.escape(query_fuzzy), normalize(chunk.entry)) or \
            re.search(r'%s\b' % re.escape(query_fuzzy), normalize(chunk.entry)):
        score = 33

    # Beginning or end of Alutiiq word
    if re.search(r'\b%s' % re.escape(query), chunk.entry) or \
            re.search(r'%s\b' % re.escape(query), chunk.entry):
        score = 35

    # Whole-word outside of parens
    if re.search(r'\b%s\b' % re.escape(query_l), without_parens):
        score = 40

    # Full Alutiiq word match with spelling correction
    if query_fuzzy in normalize(chunk.entry).split():
        score = 45

    # Whole definition (ignoring parenthesized expressions), with optional object
    full_entries = re.split("[,;] ?", chunk.defn.lower())
    full_entries_no_parens = [remove_parens(e).strip() for e in full_entries]

    accessories = [
        ('', ''),
        ('', ' her'),
        ('', ' ~her~'),
        ('', ' ~her/~'),
        ('', ' him'),
        ('', ' ~him~'),
        ('', ' ~him/~'),
        ('', ' ~him/her~'),
        ('', ' it'),
        ('', ' ~it~'),
        ('', ' ~it/~'),
        ('', ' some'),
        ('', ' something'),
        ('', ' things'),
        ('', ' them'),
        ('be ', ''),
        ('to be ', ''),
        ('is ', ''),
        ('are ', ''),
        ('a ', ''),
        ('the ', ''),
    ]
    if any(
        (pre + query_l + suff in full_entries_no_parens) or (
            pre == '' and 'to ' + query_l + suff in full_entries_no_parens
        )
        for pre, suff in accessories
    ):
        score = 50

    # Whole definition, with optional object
    if any(
        (pre + query_l + suff in full_entries) or (
            pre == '' and 'to ' + query_l + suff in full_entries
        )
        for pre, suff in accessories
    ):
        score = 55

    # Full Alutiiq word match
    if query in chunk.entry.split():
        score = 60

    return (-score, chunk.entry.lower())


def relevance(query):
    def sort_key(entry):
        return (max(chunk_relevance(chunk, query)
                    for root in entry.roots
                    for source in root.sources
                    for sense in source.senses
                    for chunk in sense.chunks),
                entry.word.lower(),
                entry.word)

    return sort_key


def build_sense(defn, chunks):
    chunks = list(chunks)
    return Sense(defn=defn, chunks=chunks, sources=[c.source_info for c in chunks],
                 examples=[e for c in chunks for e in c.examples.filter(hidden=False)],
                 comments=[c.comments for c in chunks if c.comments is not None],
                 etymologies=[c.etymology for c in chunks if c.etymology is not None],
                 main_entries=dedupe([c.main_entry for c in chunks
                                      if c.main_entry is not None and not c.main_entry.hidden]),
                 subentries=dedupe([s for c in chunks for s in c.subentries.filter(hidden=False)]),
                 see_also=dedupe([s for c in chunks for s in c.see_also.filter(hidden=False)]))


def dedupe(entries):
    seen = set()
    result = []
    for entry in entries:
        url = reverse('entry', kwargs={'word': entry})
        if url not in seen:
            seen.add(url)
            result.append(entry)
    return result


def root_to_id(pos, root):
    if root is None:
        return pos
    root_stripped = re.sub(r'[\W_]+', '', root)
    root_binary = binascii.hexlify(root.encode('utf-8')).decode('ascii')
    return f'{pos}-{root_stripped}{root_binary}'


def build_root(word, pos, root, chunks, separate_sources=True):
    if separate_sources:
        chunks = sorted(chunks, key=lambda c: ((c.source.ordering,
                                                c.source.abbrev) if c.source else (9999, 'other')) +
                                               (len(c.defn), c.defn))
        sources = [
            Source(source, sorted([
                build_sense(defn=defn, chunks=group)
                for defn, group in itertools.groupby(sub_chunks, lambda c: c.defn)
            ], key=lambda s: s.defn))
            for source, sub_chunks in itertools.groupby(chunks, lambda c: c.source)
        ]
    else:
        chunks = sorted(chunks, key=lambda c: (len(c.defn), c.defn))
        sources = [Source('', [
            build_sense(defn=defn, chunks=group)
            for defn, group in itertools.groupby(chunks, lambda c: c.defn)
        ])]

    defns = [s.defn for so in sources for s in so.senses]
    id = root_to_id(pos, root)
    return Root(word=word, pos=pos, root=root, id=id,
                defns=defns, sources=sources)


def convert_none(field):
    return '' if field == 'None' else field


def pos_root(chunk, separate_roots=False):
    pos = convert_none(chunk.pos_final)
    if separate_roots:
        return (pos, convert_none(chunk.root_final) if pos else None)
    else:
        return (pos, None)


def run_search_query(query):
    # g matches g or r
    # r matches g, r, or R
    # R matches only R
    alutiiq_query = re.sub(
        r'(?<!n)g', 'r',
        re.escape(normalize(query, g_and_r=False)).replace('r', '[rRřŘ]')
    )
    english_query = re.escape(query.lower())

    alutiiq_regexes = [
        '^{}-?$'.format(alutiiq_query),
        '^{}'.format(alutiiq_query),
        '{}-?$'.format(alutiiq_query),
        alutiiq_query,
    ]

    english_regexes = [
        '{}{}{}'.format(SOW, english_query, EOW),
        '{}{}'.format(SOW, english_query),
        '{}{}'.format(english_query, EOW),
    ]

    final_list = []
    for regex in alutiiq_regexes:
        search = EntryModel.objects.filter(search_word__regex=regex)[:SEARCH_LIMIT]
        this_count = len(search)
        if this_count == SEARCH_LIMIT:
            break

        final_list.extend(search)

    for regex in english_regexes:
        search = EntryModel.objects.filter(search_text__regex=regex)[:SEARCH_LIMIT]
        this_count = len(search)
        if this_count == SEARCH_LIMIT:
            break

        final_list.extend(search)

    return sorted(final_list, key=lambda e: (e.entry, e.pos_final))


def group_entries(chunk_list, separate_roots=False):
    entries = itertools.groupby(chunk_list, lambda c: c.entry)
    return [
        Entry(word=word, roots=[
            build_root(word=word, pos=pos, root=root, chunks=list(chunks),
                       separate_sources=separate_roots)
            for (pos, root), chunks in
            itertools.groupby(sorted(group, key=lambda c: pos_root(c, separate_roots)),
                              lambda c: pos_root(c, separate_roots))
        ])
        for word, group in entries
    ]


@subdir
def search(request):
    context = {'url': request.build_absolute_uri(request.get_full_path()),
               'newdomain': False}

    '''
    if 'w' in request.GET:
        context['build_chunks'] = request.GET['w'].replace(' ', '+')
        context['partial_word'] = morpho_join(context['build_chunks'].split('_'))
    else:
        context['partial_word'] = context['build_chunks'] = ''
    '''

    if 'q' in request.GET and request.GET['q']:
        query = request.GET['q']
        chunk_list = run_search_query(query)
        chunk_list = [c for c in chunk_list]
        entry_list = sorted(group_entries(chunk_list), key=relevance(query))
        context['entry_list'] = entry_list
        context['query'] = query
    else:
        context['entry_list'] = []
        context['query'] = ''

        if 'heroku' in context['url'].split('/')[2]:
            context['newdomain'] = True

    return render(request, 'dictionary/index.html', context)


def get_404_query(path, get):
    if 'q' in get:
        return get['q']
    else:
        components = path.replace('/', ' ').split()
        if components:
            return components[-1]
        else:
            return None


def show_404_page(request, exception):
    context = {'query': get_404_query(request.path, request.GET),
               'url': request.build_absolute_uri(request.get_full_path())}
    return render(request, 'dictionary/404.html', context, status=404)


def show_500_page(request):
    context = {'url': request.build_absolute_uri(request.get_full_path())}
    return render(request, 'dictionary/500.html', context, status=500)

import re
import itertools
from collections import namedtuple

from django.shortcuts import render, get_object_or_404, get_list_or_404

from .models import Chunk
from .alutiiq import morpho_join, inflection_data


def index(request):
    return search(request)


def entry(request, word):
    chunks = get_list_or_404(Chunk, entry=word)
    context = {'word': word,
               'chunks': [{'chunk': chunk,
                           'inflections': inflection_data(chunk)}
                          for chunk in chunks]}
    return render(request, 'dictionary/entry.html', context)


def build(request):
    return search(request)


def remove_parens(s):
    return re.sub(r'\([^)]+\)', '', s)


Entry = namedtuple('Entry', ['word', 'senses'])
Sense = namedtuple('Sense', ['pos', 'chunks', 'defns'])

def chunk_relevance(chunk, query):
    query_l = query.lower()

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

    # Beginning or end of Alutiiq word
    if re.search(r'\b%s' % re.escape(query), chunk.entry) or \
            re.search(r'%s\b' % re.escape(query), chunk.entry):
        score = 35

    # Whole-word outside of parens
    if re.search(r'\b%s\b' % re.escape(query_l), without_parens):
        score = 40

    # Whole definition (ignoring parenthesized expressions), with optional object
    full_entries = re.split("[,;] ?", chunk.defn)
    full_entries_no_parens = [remove_parens(e).strip() for e in full_entries]

    accessories = [
        ('', ''),
        ('', ' her'),
        ('', ' him'),
        ('', ' it'),
        ('', ' some'),
        ('', ' something'),
        ('', ' things'),
        ('', ' them'),
        ('be ', ''),
        ('is ', ''),
        ('are ', ''),
    ]
    if any(pre + query_l + suff in full_entries_no_parens for pre, suff in accessories):
        score = 50

    # Whole definition, with optional object
    if any(pre + query_l + suff in full_entries for pre, suff in accessories):
        score = 55

    # Full Alutiiq word match
    if query in chunk.entry.split():
        score = 60

    return (-score, chunk.entry.lower())


def relevance(query):
    def sort_key(entry):
        return (max(chunk_relevance(chunk, query)
                    for sense in entry.senses
                    for chunk in sense.chunks),
                entry.word.lower(),
                entry.word)


    return sort_key


def build_sense(pos, chunks):
    chunks = list(chunks)
    return Sense(pos=pos, chunks=chunks,
                 defns=sorted(set(c.defn for c in chunks)))


def group_entries(chunk_list):
    entries = itertools.groupby(chunk_list, lambda c: c.entry)
    return [
        Entry(word=word, senses=[
            build_sense(pos=pos, chunks=list(chunks))
            for pos, chunks in itertools.groupby(group, lambda c: c.pos)
        ])
        for word, group in entries
    ]


def search(request):
    context = {}

    '''
    if 'w' in request.GET:
        context['build_chunks'] = request.GET['w'].replace(' ', '+')
        context['partial_word'] = morpho_join(context['build_chunks'].split('_'))
    else:
        context['partial_word'] = context['build_chunks'] = ''
    '''

    if 'q' in request.GET:
        query = request.GET['q']
        chunk_list = (Chunk.objects
                           .filter(search_text__contains=query)
                           .order_by('entry', 'pos'))
        entry_list = sorted(group_entries(chunk_list), key=relevance(query))
        context['entry_list'] = entry_list
        context['query'] = query
    else:
        context['entry_list'] = []
        context['query'] = ''

    return render(request, 'dictionary/index.html', context)

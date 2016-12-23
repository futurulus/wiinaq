import re
import binascii
import itertools
from collections import namedtuple

from django.shortcuts import render, get_list_or_404
from django.views.generic.base import RedirectView

from .models import Chunk
from .alutiiq import inflection_data, normalize


ALUTIIQ_SUBDIR = '/ems/'


def subdir(view):
    def redirect_to_subdir(request, *args, **kwargs):
        if request.path.startswith(ALUTIIQ_SUBDIR):
            new_view = view
        else:
            new_view = RedirectView.as_view(url=ALUTIIQ_SUBDIR[:-1] + request.path,
                                            query_string=True)
        return new_view(request, *args, **kwargs)

    return redirect_to_subdir


def index(request):
    return search(request)


@subdir
def entry(request, word):
    chunks = get_list_or_404(Chunk, entry=word)
    entries = group_entries(chunks, separate_roots=True)
    assert len(entries) == 1
    context = {'word': word,
               'roots': [{'root': root.root,
                          'pos': root.pos,
                          'id': root.id,
                          'inflections': inflection_data(root),
                          'senses': root.senses}
                         for root in entries[0].roots],
               'url': request.build_absolute_uri(request.get_full_path()),
               'request': request}
    return render(request, 'dictionary/entry.html', context)


def build(request):
    return search(request)


def remove_parens(s):
    return re.sub(r'\([^)]+\)', '', s)


Entry = namedtuple('Entry', ['word', 'roots'])
Root = namedtuple('Root', ['word', 'pos', 'root', 'id', 'defns', 'senses'])
Sense = namedtuple('Sense', ['chunks', 'defn', 'sources'])


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
                    for root in entry.roots
                    for sense in root.senses
                    for chunk in sense.chunks),
                entry.word.lower(),
                entry.word)

    return sort_key


def build_sense(defn, chunks):
    chunks = list(chunks)
    return Sense(defn=defn, chunks=chunks, sources=[c.source for c in chunks])


def root_to_id(pos, root):
    if root is None:
        return pos
    root = root.encode('utf-8')
    return '%s-%s%s' % (pos, re.sub('[\W_]+', '', root),
                        binascii.hexlify(root))


def build_root(word, pos, root, chunks):
    chunks = sorted(chunks, key=lambda c: (len(c.defn), c.defn))
    senses = [
        build_sense(defn=defn, chunks=group)
        for defn, group in itertools.groupby(chunks, lambda c: c.defn)
    ]
    defns = [s.defn for s in senses]
    id = root_to_id(pos, root)
    return Root(word=word, pos=pos, root=root, id=id,
                defns=defns, senses=senses)


def convert_none(field):
    return '' if field == 'None' else field


def pos_root(chunk, separate_roots=False):
    if separate_roots:
        return (convert_none(chunk.pos_final), convert_none(chunk.root_final))
    else:
        return (convert_none(chunk.pos_final), None)


def group_entries(chunk_list, separate_roots=False):
    entries = itertools.groupby(chunk_list, lambda c: c.entry)
    return [
        Entry(word=word, roots=[
            build_root(word=word, pos=pos, root=root, chunks=list(chunks))
            for (pos, root), chunks in
            itertools.groupby(group, lambda c: pos_root(c, separate_roots))
        ])
        for word, group in entries
    ]


def matches_query(chunk, query):
    '''
    >>> from .models import Chunk
    >>> c = Chunk(); c.entry = "gwa'i"; c.defn = 'here (restricted)'; c.fill()
    >>> matches_query(c, 'try')
    False
    >>> c = Chunk(); c.entry = "Kasaakaq"; c.defn = 'Russian'; c.fill()
    >>> matches_query(c, 'kasaak')
    True
    '''
    return (query.lower() in chunk.defn.lower() or
            normalize(query) in normalize(chunk.entry))


@subdir
def search(request):
    context = {}

    '''
    if 'w' in request.GET:
        context['build_chunks'] = request.GET['w'].replace(' ', '+')
        context['partial_word'] = morpho_join(context['build_chunks'].split('_'))
    else:
        context['partial_word'] = context['build_chunks'] = ''
    '''

    if 'q' in request.GET and request.GET['q']:
        query = request.GET['q']
        chunk_list = ((Chunk.objects
                            .filter(search_text__contains=query.lower()) |
                       Chunk.objects
                            .filter(search_text__contains=normalize(query)))
                      .order_by('entry', 'pos_final'))
        chunk_list = [c for c in chunk_list if matches_query(c, query)]
        entry_list = sorted(group_entries(chunk_list), key=relevance(query))
        context['entry_list'] = entry_list
        context['query'] = query
    else:
        context['entry_list'] = []
        context['query'] = ''

    return render(request, 'dictionary/index.html', context)

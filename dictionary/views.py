import re

from django.shortcuts import render, get_object_or_404

from .models import Chunk
from .alutiiq import morpho_join, inflection_data


def index(request):
    return build(request)


def entry(request, chunk_id):
    chunk = get_object_or_404(Chunk, pk=chunk_id)
    context = {'chunk': chunk}
    context.update(inflection_data(chunk))
    return render(request, 'dictionary/entry.html', context)


def search(request):
    return build(request)


def remove_parens(s):
    return re.sub(r'\([^)]+\)', '', s)


def relevance(query):
    query = query.lower()

    def sort_key(chunk):
        score = 0

        # Return results in the reverse of the following order:

        # Beginning or end definition match inside parens
        without_parens = remove_parens(chunk.defn)
        inside_parens = ' '.join(re.findall(r'(?<=\()[^)]+(?=\))', chunk.defn))
        if re.search(r'\b%s' % re.escape(query), inside_parens) or \
                re.search(r'%s\b' % re.escape(query), inside_parens):
            score = 10

        # Beginning or end outside of parens
        if re.search(r'\b%s' % re.escape(query), without_parens) or \
                re.search(r'%s\b' % re.escape(query), without_parens):
            score = 20

        # Whole-word definition match inside parens
        if re.search(r'\b%s\b' % re.escape(query), inside_parens):
            score = 30

        # Beginning or end of Alutiiq word
        if re.search(r'\b%s' % re.escape(query), chunk.entry) or \
                re.search(r'%s\b' % re.escape(query), chunk.entry):
            score = 35

        # Whole-word outside of parens
        if re.search(r'\b%s\b' % re.escape(query), without_parens):
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
        if any(pre + query + suff in full_entries_no_parens for pre, suff in accessories):
            score = 50

        # Whole definition, with optional object
        if any(pre + query + suff in full_entries for pre, suff in accessories):
            score = 55

        # Full Alutiiq word match
        if query in chunk.entry.split():
            score = 60

        return (-score, chunk.entry.lower())

    return sort_key


def build(request):
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
                           .filter(search_text__contains=query))
        chunk_list = sorted(chunk_list, key=relevance(query))
        context['chunk_list'] = chunk_list
        context['query'] = query
    else:
        context['chunk_list'] = []
        context['query'] = ''

    return render(request, 'dictionary/index.html', context)

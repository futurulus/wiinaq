from django.shortcuts import render, get_object_or_404

from .models import Chunk
from .alutiiq import morpho_join


def index(request):
    return build(request)


def entry(request, chunk_id):
    chunk = get_object_or_404(Chunk, pk=chunk_id)
    return render(request, 'dictionary/entry.html', {'chunk': chunk})


def search(request):
    return build(request)


def build(request):
    context = {}

    if 'w' in request.GET:
        context['build_chunks'] = request.GET['w'].replace(' ', '+')
        context['partial_word'] = morpho_join(context['build_chunks'].split('_'))
    else:
        context['partial_word'] = context['build_chunks'] = ''

    if 'q' in request.GET:
        query = request.GET['q']
        chunk_list = (Chunk.objects
                           .filter(search_text__contains=query)
                           .order_by('entry'))
        context['chunk_list'] = chunk_list
        context['query'] = query
    else:
        context['chunk_list'] = []
        context['query'] = ''

    return render(request, 'dictionary/index.html', context)

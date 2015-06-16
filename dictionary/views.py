from django.shortcuts import render, get_object_or_404

from .models import Chunk


def index(request):
    chunk_list = Chunk.objects.order_by('entry')
    context = {'chunk_list': chunk_list}
    return render(request, 'dictionary/index.html', context)


def entry(request, chunk_id):
    chunk = get_object_or_404(Chunk, pk=chunk_id)
    return render(request, 'dictionary/entry.html', {'chunk': chunk})


def search(request):
    chunk_list = Chunk.objects.filter(search_text__contains=request.GET['q'])
    context = {'chunk_list': chunk_list}
    return render(request, 'dictionary/index.html', context)

from django.contrib import admin

from .models import Chunk


class ChunkAdmin(admin.ModelAdmin):
    readonly_fields = ('search_text',)
    list_display = ['entry', 'pos', 'defn']
    list_filter = ['pos']
    search_fields = ['entry', 'defn']

admin.site.register(Chunk, ChunkAdmin)

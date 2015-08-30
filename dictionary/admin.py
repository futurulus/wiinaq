from django.contrib import admin

from .models import Chunk, Source


class ChunkAdmin(admin.ModelAdmin):
    readonly_fields = ('pos_auto', 'root_auto', 'search_text')
    list_display = ['entry', 'pos_final', 'defn']
    list_filter = ['pos']
    search_fields = ['entry', 'defn']
    save_as = True

admin.site.register(Chunk, ChunkAdmin)


class SourceAdmin(admin.ModelAdmin):
    list_display = ['abbrev', 'description']

admin.site.register(Source, SourceAdmin)

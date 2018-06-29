from django.contrib import admin

from .models import Entry, Source


class EntryAdmin(admin.ModelAdmin):
    readonly_fields = ('pos_auto', 'root_auto', 'search_text')
    list_display = ['entry', 'pos_final', 'defn']
    list_filter = ['pos']
    search_fields = ['entry', 'defn']
    save_as = True

admin.site.register(Entry, EntryAdmin)


class SourceAdmin(admin.ModelAdmin):
    list_display = ['abbrev', 'description']

admin.site.register(Source, SourceAdmin)

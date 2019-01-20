from django.contrib import admin
from django.db import models
from django.forms import Textarea

from .models import Entry, Source, Example, Variety
from .models import SeeAlso, EntryExampleInfo, EntryVarietyInfo, ExampleVarietyInfo


class CustomTitleAdmin(admin.ModelAdmin):
    custom_title = None

    def changelist_view(self, request, extra_context=None):
        if self.custom_title is not None:
            extra_context = {'title': self.custom_title}
        return super(CustomTitleAdmin, self).changelist_view(request, extra_context=extra_context)


class EntryExamplesInline(admin.TabularInline):
    model = EntryExampleInfo
    raw_id_fields = ['example']
    extra = 1  # how many rows to show
    verbose_name = 'example'
    verbose_name_plural = 'examples'


class ExampleEntriesInline(admin.TabularInline):
    model = EntryExampleInfo
    raw_id_fields = ['entry']
    extra = 1  # how many rows to show
    verbose_name = 'entry'
    verbose_name_plural = 'entries'


class EntryVarietyInfoInline(admin.TabularInline):
    model = EntryVarietyInfo
    extra = 1  # how many rows to show
    verbose_name = 'variety'
    verbose_name_plural = 'language variety information'


class ExampleVarietyInfoInline(admin.TabularInline):
    model = ExampleVarietyInfo
    extra = 1  # how many rows to show
    verbose_name = 'variety'
    verbose_name_plural = 'language variety information'


class SeeAlsoInline(admin.TabularInline):
    model = SeeAlso
    raw_id_fields = ['target']
    fk_name = 'source'
    extra = 1  # how many rows to show
    verbose_name = 'See Also link'
    verbose_name_plural = 'See Also links'


class EntryAdmin(CustomTitleAdmin):
    custom_title = 'An entry is a single definition of a single word from a single source. ' \
                   'All entries for the same word are shown on that word\'s page.'
    readonly_fields = ('pos_auto', 'root_auto', 'search_text')
    raw_id_fields = ('main_entry',)
    list_display = ['entry', 'pos_final', 'defn']
    list_filter = ['pos', 'source']
    search_fields = ['entry', 'defn']
    filter_horizontal = ['examples']
    inlines = (EntryVarietyInfoInline, EntryExamplesInline, SeeAlsoInline)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 70})},
    }
    save_as = True

admin.site.register(Entry, EntryAdmin)


class SourceAdmin(CustomTitleAdmin):
    custom_title = 'Sources are where we heard the word from: ' \
                   'speakers, books, other dictionaries, etc.'
    list_display = ['abbrev', 'description']

admin.site.register(Source, SourceAdmin)


class VarietyAdmin(CustomTitleAdmin):
    custom_title = 'A short list of broad language varieties, dialects, or geographic regions. ' \
                   'For smaller regions, cities, or speakers, use the "Details" field.'
    list_display = ['abbrev', 'description']

admin.site.register(Variety, VarietyAdmin)


class ExampleAdmin(CustomTitleAdmin):
    custom_title = "Example sentences and phrases showing word usage. Make sure they're added " \
                   "to an Entry or people can't see them."
    list_display = ['vernacular', 'english']
    search_fields = ['vernacular', 'english']
    inlines = (ExampleVarietyInfoInline, ExampleEntriesInline)

admin.site.register(Example, ExampleAdmin)

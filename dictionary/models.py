from django.db import models
from django.template.defaultfilters import truncatechars

from .alutiiq import normalize, get_pos, get_root


class Source(models.Model):
    abbrev = models.CharField('abbreviation', unique=True, max_length=100)
    description = models.CharField('description', max_length=1000)
    ordering = models.IntegerField('sort location',
                                   default=0,
                                   help_text='Controls what order sources show up in each '
                                             'dictionary entry. Sources with lower values of this '
                                             'number will appear first, with ties broken by '
                                             'alphabetical ordering of the abbreviation.')

    def annotated(self):
        return '<span class="source" title="%s">%s</span>' % (self.description, self.abbrev)

    def __unicode__(self):
        return self.description


class Variety(models.Model):
    abbrev = models.CharField('abbreviation', unique=True, max_length=100)
    description = models.CharField(max_length=1000)

    class Meta:
        verbose_name_plural = "varieties"

    def annotated(self):
        return '<span class="variety" title="%s">%s</span>' % (self.description, self.abbrev)

    def __unicode__(self):
        return self.description


class Example(models.Model):
    vernacular = models.TextField('Alutiiq',
                                  help_text='Text in Alutiiq (or perhaps other focus languages '
                                            'in the future?)')
    english = models.TextField('English', blank=True,
                               help_text='Natural translation of the text into English')
    source = models.ForeignKey(Source, blank=True, null=True,
                               help_text='Dictionary, book, speaker interview, etc. where this '
                                         'word was found')
    source_info = models.CharField('source details', max_length=200, default='', blank=True,
                                   help_text='Page numbers, file IDs, dates, or other specific '
                                             'information needed to find the word in the source.')
    source_link = models.URLField(max_length=200, default='', blank=True,
                                  help_text='A URL to link to the source. If not empty, this will '
                                            'turn the "source details" into a hyperlink.')
    varieties = models.ManyToManyField(Variety,
                                       help_text='Broad language variety, dialect, or geographic '
                                                 'region',
                                       through='ExampleVarietyInfo',
                                       blank=True)
    comments = models.TextField(help_text="Usage notes, miscellaneous points of interest, etc. "
                                          "These are visible below the example.",
                                blank=True, default='')
    notes = models.TextField(help_text="Dictionary maintainers' notes. These are private and only "
                                       "visible to people with access to this admin site.",
                             blank=True, default='')
    hidden = models.BooleanField(default=False,
                                 help_text='Check this to hide the example from public viewing '
                                           '(e.g. if it contains things that are sacred, '
                                           'offensive, etc.)')

    def __unicode__(self):
        return u'{} | {}'.format(truncatechars(self.vernacular, 20),
                                 truncatechars(self.english, 20))


class Entry(models.Model):
    entry = models.CharField('word', max_length=100)
    pos = models.CharField('part of speech',
                           help_text='To remove the part of speech entirely '
                                     '(show no ending tables for this word), enter "None".',
                           default='',
                           blank=True,
                           max_length=10)
    pos_auto = models.CharField('part of speech (guess)',
                                editable=False,
                                help_text='Automatically detected based on the '
                                          'word and other information. If "part of speech" is '
                                          'blank, this will be used.',
                                default='None',
                                max_length=10)
    pos_final = models.CharField('Part of speech',
                                 editable=False,
                                 default='None',
                                 max_length=10)
    root = models.CharField(max_length=100, default='', blank=True)
    root_auto = models.CharField('root (guess)',
                                 editable=False,
                                 help_text='Automatically detected based on the '
                                           'word and other information. If "root" is '
                                           'blank, this will be used.',  # TODO: document syntax
                                 default='',
                                 max_length=100)
    root_final = models.CharField('Root',
                                  editable=False,
                                  default='',
                                  max_length=100)
    etymology = models.TextField(blank=True, default='')
    defn = models.TextField('definition')
    search_word = models.TextField(editable=False, default='')
    search_text = models.TextField(editable=False, default='')
    source = models.ForeignKey(Source, blank=True, null=True,
                               help_text='Dictionary, book, speaker interview, etc. where this '
                                         'word was found')
    comments = models.TextField(help_text="Usage notes, miscellaneous points of interest, etc. "
                                          "These are visible on the word's page.",
                                blank=True, default='')
    notes = models.TextField(help_text="Dictionary maintainers' notes. These are private and only "
                                       "visible to people with access to this admin site.",
                             blank=True, default='')
    source_info = models.CharField('source details', max_length=200, default='', blank=True,
                                   help_text='Page numbers, file IDs, dates, or other specific '
                                             'information needed to find the word in the source.')
    source_link = models.URLField(max_length=200, default='', blank=True,
                                  help_text='A URL to link to the source. If not empty, this will '
                                            'turn the "source details" into a hyperlink.')
    main_entry = models.ForeignKey('Entry', blank=True, null=True,
                                   related_name='subentries',
                                   help_text='If this is a sub-entry, link to the parent entry '
                                             '(form without a postbase, for example).')
    varieties = models.ManyToManyField(Variety, through='EntryVarietyInfo', blank=True,
                                       help_text='Broad language variety, dialect, or geographic '
                                                 'region')
    examples = models.ManyToManyField(Example, through='EntryExampleInfo', blank=True)
    see_also = models.ManyToManyField('Entry', through='SeeAlso', blank=True,
                                      related_name='see_also_linked',
                                      help_text='Other entries that might be useful to look at')
    hidden = models.BooleanField(default=False,
                                 help_text='Check this to hide the entry from public viewing '
                                           '(e.g. if it contains things that are sacred, '
                                           'offensive, etc.)')

    class Meta:
        verbose_name_plural = "entries"

    def pos_or_auto(self):
        return self.pos or self.pos_auto

    def root_or_auto(self):
        return self.root or self.root_auto

    def fill(self):
        self.search_word = normalize(self.entry)
        self.search_text = self.defn.lower()
        self.pos_auto = get_pos(self.entry, self.defn)
        self.pos_final = self.pos or self.pos_auto
        self.root_auto = get_root(self.entry, self.pos_final, self.defn)
        self.root_final = self.root or self.root_auto

    def save(self):
        self.fill()
        super(Entry, self).save()

    def __unicode__(self):
        return self.entry


class EntryVarietyInfo(models.Model):
    entry = models.ForeignKey(Entry)
    variety = models.ForeignKey(Variety)
    detail = models.CharField(max_length=200, default='', blank=True,
                              help_text='Additional language variety details, e.g. city names, '
                                        'Northern/Southern for Kodiak, or specific speakers')

    def __unicode__(self):
        return u'{} ({})'.format(self.variety.abbrev, self.detail)


class ExampleVarietyInfo(models.Model):
    example = models.ForeignKey(Example)
    variety = models.ForeignKey(Variety)
    detail = models.CharField('details', max_length=200, default='', blank=True,
                              help_text='Additional language variety details, e.g. city names, '
                                        'Northern/Southern for Kodiak, or specific speakers')

    def __unicode__(self):
        return u'{} ({})'.format(self.variety.abbrev, self.detail)


class EntryExampleInfo(models.Model):
    entry = models.ForeignKey(Entry)
    example = models.ForeignKey(Example, verbose_name='example ID',
                                help_text='Use the magnifying glass icon to search for or create '
                                          'new examples, then select an example and its ID will '
                                          'appear here.')

    def __unicode__(self):
        return u'Example for "{}": {}'.format(self.entry, truncatechars(self.example.vernacular, 20))


class SeeAlso(models.Model):
    source = models.ForeignKey(Entry,
                               related_name='see_also_outgoing',
                               help_text='The entry on which this "see also" will appear.')
    target = models.ForeignKey(Entry,
                               related_name='see_also_incoming',
                               help_text='The entry this "see also" link will point to. Use the '
                                         'magnifying glass icon to search for entires, then select '
                                         'an entry and its ID will appear here.')

    def __unicode__(self):
        return u'{}: see also "{}"'.format(self.source, self.target)

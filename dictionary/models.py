from django.db import models

from .alutiiq import normalize, get_pos, get_root


class Source(models.Model):
    abbrev = models.CharField('abbreviation', unique=True, max_length=100)
    description = models.CharField('description', max_length=1000)

    def annotated(self):
        return '<span class="source" title="%s">%s</span>' % (self.description, self.abbrev)

    def __unicode__(self):
        return self.description


class Chunk(models.Model):
    entry = models.CharField('word', max_length=100)
    pos = models.CharField('part of speech',
                           help_text='''To remove the part of speech entirely
                           (show no ending tables for this word), enter "None".''',
                           default='',
                           blank=True,
                           max_length=10)
    pos_auto = models.CharField('part of speech (guess)',
                                editable=False,
                                help_text='''Automatically detected based on the
                                word and other information. If "part of speech" is
                                blank, this will be used.''',
                                default='None',
                                max_length=10)
    pos_final = models.CharField('Part of speech',
                                 editable=False,
                                 default='None',
                                 max_length=10)
    root = models.CharField(max_length=100, default='', blank=True)
    root_auto = models.CharField('root (guess)',
                                 editable=False,
                                 help_text='''Automatically detected based on the
                                 word and other information. If "root" is
                                 blank, this will be used.''',  # TODO: document syntax
                                 default='',
                                 max_length=100)
    root_final = models.CharField('Root',
                                  editable=False,
                                  default='',
                                  max_length=100)
    defn = models.TextField('definition')
    search_text = models.TextField(editable=False, default='')
    source = models.ForeignKey(Source, null=True)
    source_info = models.CharField(max_length=200, default='', blank=True)
    source_link = models.URLField(max_length=200, default='', blank=True)

    def pos_or_auto(self):
        return self.pos or self.pos_auto

    def root_or_auto(self):
        return self.root or self.root_auto

    def fill(self):
        self.search_text = '%s %s' % (normalize(self.entry), self.defn.lower())
        self.pos_auto = get_pos(self.entry, self.defn)
        self.pos_final = self.pos or self.pos_auto
        self.root_auto = get_root(self.entry, self.defn)
        self.root_final = self.root or self.root_auto

    def save(self):
        self.fill()
        super(Chunk, self).save()

    def __unicode__(self):
        return self.entry

from django.db import models

from .alutiiq import get_pos, get_root


class Chunk(models.Model):
    entry = models.CharField('word', max_length=100)
    pos = models.CharField('part of speech',
                           help_text='''To remove the part of speech entirely
                           (show no ending tables for this word), enter "None".''',
                           default='',
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
    root = models.CharField(max_length=100, default='')
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
    source = models.CharField(max_length=200)

    def pos_or_auto(self):
        return self.pos or self.pos_auto

    def root_or_auto(self):
        return self.root or self.root_auto

    def save(self):
        self.search_text = '%s %s' % (self.entry, self.defn)
        self.pos_auto = get_pos(self.entry, self.defn)
        self.pos_final = self.pos or self.pos_auto
        self.root_auto = get_root(self.entry, self.defn)
        self.root_final = self.root or self.root_auto
        super(Chunk, self).save()

    def __unicode__(self):
        return self.entry

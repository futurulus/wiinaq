from django.db import models


class Chunk(models.Model):
    entry = models.CharField(max_length=100)
    pos = models.CharField(max_length=10)
    defn = models.TextField()
    search_text = models.TextField(editable=False, default='')
    source = models.CharField(max_length=200)

    def save(self):
        self.search_text = '%s %s' % (self.entry, self.defn)
        super(Chunk, self).save()

    def __unicode__(self):
        return self.entry

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_chunk_search_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='chunk',
            name='source',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]

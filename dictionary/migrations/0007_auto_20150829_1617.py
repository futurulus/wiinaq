# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0006_auto_20150829_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='chunk',
            name='source_info',
            field=models.CharField(default=b'', max_length=200),
        ),
        migrations.AddField(
            model_name='chunk',
            name='source_link',
            field=models.URLField(default=b''),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='source',
            field=models.ForeignKey(to='dictionary.Source'),
        ),
    ]

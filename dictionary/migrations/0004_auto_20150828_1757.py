# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0003_chunk_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='chunk',
            name='pos_auto',
            field=models.CharField(default=b'', help_text=b'Automatically detected based on the\n                                word and other information. If "part of speech" is\n                                blank, this will be used.', max_length=10, verbose_name=b'part of speech (guess)'),
        ),
        migrations.AddField(
            model_name='chunk',
            name='root',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AddField(
            model_name='chunk',
            name='root_auto',
            field=models.CharField(default=b'', help_text=b'Automatically detected based on the\n                                 word and other information. If "root" is\n                                 blank, this will be used.', max_length=100, verbose_name=b'root (guess)'),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='defn',
            field=models.TextField(verbose_name=b'definition'),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='entry',
            field=models.CharField(max_length=100, verbose_name=b'word'),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='pos',
            field=models.CharField(default=b'', help_text=b'To remove the part of speech entirely\n                           (show no ending tables for this word), enter "None".', max_length=10, verbose_name=b'part of speech'),
        ),
    ]

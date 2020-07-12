# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('entry', models.CharField(max_length=100, verbose_name=b'word')),
                ('pos', models.CharField(default=b'', help_text=b'To remove the part of speech entirely\n                           (show no ending tables for this word), enter "None".', max_length=10, verbose_name=b'part of speech', blank=True)),
                ('pos_auto', models.CharField(default=b'None', help_text=b'Automatically detected based on the\n                                word and other information. If "part of speech" is\n                                blank, this will be used.', max_length=10, editable=False, verbose_name=b'part of speech (guess)')),
                ('pos_final', models.CharField(default=b'None', verbose_name=b'Part of speech', max_length=10, editable=False)),
                ('root', models.CharField(default=b'', max_length=100, blank=True)),
                ('root_auto', models.CharField(default=b'', help_text=b'Automatically detected based on the\n                                 word and other information. If "root" is\n                                 blank, this will be used.', max_length=100, editable=False, verbose_name=b'root (guess)')),
                ('root_final', models.CharField(default=b'', verbose_name=b'Root', max_length=100, editable=False)),
                ('defn', models.TextField(verbose_name=b'definition')),
                ('search_text', models.TextField(default=b'', editable=False)),
                ('source_info', models.CharField(default=b'', max_length=200, blank=True)),
                ('source_link', models.URLField(default=b'', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abbrev', models.CharField(unique=True, max_length=100, verbose_name=b'abbreviation')),
                ('description', models.CharField(max_length=1000, verbose_name=b'description')),
            ],
        ),
        migrations.AddField(
            model_name='chunk',
            name='source',
            field=models.ForeignKey(to='dictionary.Source', on_delete=models.SET_NULL, null=True),
        ),
    ]

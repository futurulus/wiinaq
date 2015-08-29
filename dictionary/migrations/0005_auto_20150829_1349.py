# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0004_auto_20150828_1757'),
    ]

    operations = [
        migrations.AddField(
            model_name='chunk',
            name='pos_final',
            field=models.CharField(default=b'None', max_length=10, editable=False),
        ),
        migrations.AddField(
            model_name='chunk',
            name='root_final',
            field=models.CharField(default=b'', max_length=100, editable=False),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='pos_auto',
            field=models.CharField(default=b'None', help_text=b'Automatically detected based on the\n                                word and other information. If "part of speech" is\n                                blank, this will be used.', max_length=10, editable=False, verbose_name=b'part of speech (guess)'),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='root_auto',
            field=models.CharField(default=b'', help_text=b'Automatically detected based on the\n                                 word and other information. If "root" is\n                                 blank, this will be used.', max_length=100, editable=False, verbose_name=b'root (guess)'),
        ),
    ]

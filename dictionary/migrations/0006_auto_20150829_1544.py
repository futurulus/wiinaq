# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0005_auto_20150829_1349'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('abbrev', models.CharField(unique=True, max_length=100, verbose_name=b'abbreviation')),
                ('description', models.CharField(max_length=1000, verbose_name=b'description')),
            ],
        ),
        migrations.AlterField(
            model_name='chunk',
            name='pos_final',
            field=models.CharField(default=b'None', verbose_name=b'Part of speech', max_length=10, editable=False),
        ),
        migrations.AlterField(
            model_name='chunk',
            name='root_final',
            field=models.CharField(default=b'', verbose_name=b'Root', max_length=100, editable=False),
        ),
    ]

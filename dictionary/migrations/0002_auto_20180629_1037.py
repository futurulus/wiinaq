# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-29 17:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Chunk',
            new_name='Entry',
        ),
    ]
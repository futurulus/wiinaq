# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-14 05:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0005_auto_20190202_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='search_word',
            field=models.TextField(default=b'', editable=False),
        ),
    ]
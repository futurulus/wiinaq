# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0007_auto_20150829_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chunk',
            name='source',
            field=models.ForeignKey(to='dictionary.Source', null=True),
        ),
    ]

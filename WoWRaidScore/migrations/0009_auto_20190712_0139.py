# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-12 01:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WoWRaidScore', '0008_fightevent_score_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raidscore',
            name='spec',
            field=models.IntegerField(null=True),
        ),
    ]

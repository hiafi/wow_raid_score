# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-21 02:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tos', '0010_maidenscore_right_orb'),
    ]

    operations = [
        migrations.AddField(
            model_name='maidenscore',
            name='bomb_from_echos',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='maidenscore',
            name='bomb_from_p1_orb',
            field=models.IntegerField(default=0),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-20 18:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tos', '0009_discore'),
    ]

    operations = [
        migrations.AddField(
            model_name='maidenscore',
            name='right_orb',
            field=models.IntegerField(default=0),
        ),
    ]
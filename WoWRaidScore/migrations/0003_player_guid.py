# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-10 13:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WoWRaidScore', '0002_fight_attempt'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='guid',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]

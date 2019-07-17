# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-07-17 00:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WoWRaidScore', '0009_auto_20190712_0139'),
        ('azshara_palace', '0002_azsharascore_drained_soul'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommanderScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('bolts', models.IntegerField(default=0)),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
    ]

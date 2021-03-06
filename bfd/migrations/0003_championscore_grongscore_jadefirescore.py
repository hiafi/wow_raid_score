# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-02-17 17:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WoWRaidScore', '0007_auto_20171026_0221'),
        ('bfd', '0002_conclavescore_rhastakhanscore'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChampionScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('wave_of_light', models.IntegerField(default=0)),
                ('divine_mallet', models.IntegerField(default=0)),
                ('blinding_faith', models.IntegerField(default=0)),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
        migrations.CreateModel(
            name='GrongScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('fear', models.IntegerField(default=0)),
                ('chill_of_death', models.IntegerField(default=0)),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
        migrations.CreateModel(
            name='JadefireScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('multisided_strike', models.IntegerField(default=0)),
                ('beam', models.IntegerField(default=0)),
                ('phoenix_strike', models.IntegerField(default=0)),
                ('failed_trap_fall', models.IntegerField(default=0)),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
    ]

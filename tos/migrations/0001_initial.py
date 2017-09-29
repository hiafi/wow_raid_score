# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 19:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('WoWRaidScore', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GorothScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('splashing_from_meteors', models.IntegerField()),
                ('soaking_infernals', models.IntegerField()),
                ('not_hiding', models.IntegerField()),
                ('spike_damage', models.IntegerField()),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
        migrations.CreateModel(
            name='MistressScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('bufferfish_uptime', models.IntegerField(blank=True, default=0, null=True)),
                ('dropoffs', models.IntegerField(default=0)),
                ('tornado_damage', models.IntegerField(default=0)),
                ('hit_by_giant_fish', models.IntegerField(default=0)),
                ('hydra_shots', models.IntegerField(default=0)),
                ('murlock_debuff_uptime', models.IntegerField(blank=True, default=0, null=True)),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
    ]

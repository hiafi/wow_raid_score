# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-26 02:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WoWRaidScore', '0006_boss_ordering'),
    ]

    operations = [
        migrations.CreateModel(
            name='FightEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minute', models.IntegerField()),
                ('second', models.IntegerField()),
                ('text', models.TextField()),
                ('fight', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='WoWRaidScore.Fight')),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='WoWRaidScore.Player')),
            ],
        ),
        migrations.AlterModelOptions(
            name='boss',
            options={'ordering': ['zone_id', 'ordering']},
        ),
    ]

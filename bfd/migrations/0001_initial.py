# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-02-17 02:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('WoWRaidScore', '0007_auto_20171026_0221'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpulenceScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('flames_of_punishment', models.IntegerField(default=0)),
                ('volatile_charge', models.IntegerField(default=0)),
                ('crush', models.IntegerField(default=0)),
                ('molten_gold', models.IntegerField(default=0)),
                ('deadly_hex', models.IntegerField(default=0)),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
    ]
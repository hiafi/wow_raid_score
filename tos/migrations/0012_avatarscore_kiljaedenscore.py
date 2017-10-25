# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-22 18:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('WoWRaidScore', '0004_auto_20171011_0236'),
        ('tos', '0011_auto_20171021_0227'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvatarScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('touch_of_sargeras_soak', models.IntegerField(default=0)),
                ('unbound_chaos', models.IntegerField(default=0)),
                ('shadow_blades', models.IntegerField(default=0)),
                ('meteor_soak', models.IntegerField(default=0)),
                ('tornados', models.IntegerField(default=0)),
                ('dark_marks', models.IntegerField(default=0)),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
        migrations.CreateModel(
            name='KiljaedenScore',
            fields=[
                ('raidscore_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='WoWRaidScore.RaidScore')),
                ('soaking_rain', models.IntegerField(default=0)),
                ('soaking_lasers', models.IntegerField(default=0)),
                ('obelisks', models.IntegerField(default=0)),
            ],
            bases=('WoWRaidScore.raidscore',),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-22 18:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tos', '0012_avatarscore_kiljaedenscore'),
    ]

    operations = [
        migrations.AddField(
            model_name='kiljaedenscore',
            name='dreadburst',
            field=models.IntegerField(default=0),
        ),
    ]

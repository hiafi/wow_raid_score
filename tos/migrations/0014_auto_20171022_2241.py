# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-22 22:41
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tos', '0013_kiljaedenscore_dreadburst'),
    ]

    operations = [
        migrations.RenameField(
            model_name='kiljaedenscore',
            old_name='dreadburst',
            new_name='bursting_dreadflame',
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-02-27 23:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bfd', '0007_conclavescore_raptor_damage'),
    ]

    operations = [
        migrations.AddField(
            model_name='mekkatorquescore',
            name='radiation',
            field=models.IntegerField(default=0),
        ),
    ]

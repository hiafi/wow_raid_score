# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-05-25 01:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bfd', '0011_jainascore_heart_of_frost'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blockadescore',
            old_name='sea_storm',
            new_name='ire_of_the_deep',
        ),
        migrations.RemoveField(
            model_name='blockadescore',
            name='torrential_swell',
        ),
    ]
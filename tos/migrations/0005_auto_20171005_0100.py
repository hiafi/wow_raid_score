# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-05 01:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tos', '0004_auto_20170929_0256'),
    ]

    operations = [
        migrations.AddField(
            model_name='mistressscore',
            name='dispels',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='mistressscore',
            name='interupts',
            field=models.IntegerField(default=0),
        ),
    ]

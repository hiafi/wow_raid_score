# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-05-02 23:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bfd', '0010_auto_20190424_0129'),
    ]

    operations = [
        migrations.AddField(
            model_name='jainascore',
            name='heart_of_frost',
            field=models.IntegerField(default=0),
        ),
    ]

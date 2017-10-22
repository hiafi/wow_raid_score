# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from model_utils.managers import InheritanceManager
from unidecode import unidecode
from django.contrib.auth.models import User


class Player(models.Model):
    name = models.CharField(max_length=20)
    server = models.CharField(max_length=30)
    guid = models.IntegerField()

    class Meta:
        app_label = "WoWRaidScore"

    def __str__(self):
        return "<Player {}>".format(self.name)

    @property
    def safe_name(self):
        return unidecode(self.name)


class Boss(models.Model):
    name = models.CharField(max_length=30)
    zone_id = models.IntegerField()
    boss_id = models.IntegerField()

    def __str__(self):
        return "<Boss {}>".format(self.name)

    def __repr__(self):
        return self.__str__()


class Group(models.Model):
    name = models.CharField(max_length=30)
    short_name = models.SlugField(max_length=10)
    user_access = models.ManyToManyField(User)


class Raid(models.Model):
    raid_id = models.CharField(max_length=30)
    time = models.DateTimeField()
    user = models.ForeignKey(User)
    group = models.ForeignKey(Group, null=True, blank=True)

    def __str__(self):
        return "<Raid {} - {}>".format(self.raid_id, self.time)

    def __repr__(self):
        return self.__str__()


class Fight(models.Model):
    raid = models.ForeignKey(Raid)
    boss = models.ForeignKey(Boss)

    fight_id = models.IntegerField()
    attempt = models.IntegerField()
    percent = models.FloatField()
    killed = models.BooleanField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return "<Fight {} ({}%) - {}>".format(self.boss, self.percent, self.raid)

    def __repr__(self):
        return self.__str__()


class RaidScore(models.Model):
    fight = models.ForeignKey(Fight)
    player = models.ForeignKey(Player)

    spec = models.IntegerField()
    melee_dps = models.BooleanField()
    ranged_dps = models.BooleanField()
    tank = models.BooleanField()
    healer = models.BooleanField()

    objects = InheritanceManager()

    @property
    def base_score(self):
        return 0

    @property
    def score_dict(self):
        return {}

    @property
    def total(self):
        return self.base_score + sum(self.score_dict.values())

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from model_utils.managers import InheritanceManager
from unidecode import unidecode
from django.contrib.auth.models import User
import datetime
from django.utils import timezone


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

    last_analyzer_update = models.DateField(default=timezone.now)
    ordering = models.IntegerField(default=0)

    class Meta:
        ordering = ['zone_id', 'ordering']

    def __str__(self):
        return "<Boss {} ({}) Valid Date: {}>".format(self.name, self.ordering, self.last_analyzer_update)

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

    @property
    def local_time(self):
        return timezone.localtime(self.time)

    def __str__(self):
        return "<Raid {} - {}>".format(self.raid_id, self.time)

    def __repr__(self):
        return self.__str__()


class Fight(models.Model):
    raid = models.ForeignKey(Raid)
    boss = models.ForeignKey(Boss)
    date_parsed = models.DateField(default=timezone.now)

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

    def __str__(self):
        return "<ScoreObj: {} - {}>".format(self.fight, self.player)

    @property
    def base_score(self):
        return 0

    @property
    def score_dict(self):
        return {}

    @property
    def total(self):
        return self.base_score + sum(self.score_dict.values())

    @property
    def score_description(self):
        return {}


class FightEvent(models.Model):
    fight = models.ForeignKey(Fight)
    player = models.ForeignKey(Player, null=True, blank=True)
    minute = models.IntegerField()
    second = models.IntegerField()
    text = models.TextField()
    score_value = models.IntegerField(null=True, blank=True)

    @property
    def second_string(self):
        return "{:02d}".format(self.second)

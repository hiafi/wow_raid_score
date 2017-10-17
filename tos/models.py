# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from WoWRaidScore.models import RaidScore


# Create your models here.

class GorothScore(RaidScore):
    splashing_from_meteors = models.IntegerField(default=0)
    soaking_infernals = models.IntegerField(default=0)
    not_hiding = models.IntegerField(default=0)

    @property
    def table_keys(self):
        return [
            "Dropping Meteors on others", "Soaking Infernals", "Not hiding"
        ]

    @property
    def score_dict(self):
        return {
            "Dropping Meteors on others": self.splashing_from_meteors,
            "Soaking Infernals": self.soaking_infernals,
            "Not hiding": self.not_hiding
        }


class MistressScore(RaidScore):
    bufferfish_uptime = models.IntegerField(default=0)
    dropoffs = models.IntegerField(default=0)
    tornado_damage = models.IntegerField(default=0)
    hit_by_giant_fish = models.IntegerField(default=0)
    hydra_shots = models.IntegerField(default=0)
    stacked_hydra_shots = models.IntegerField(default=0)
    murlock_debuff_uptime = models.IntegerField(default=0)
    interrupts = models.IntegerField(default=0)
    dispels = models.IntegerField(default=0)

    @property
    def table_keys(self):
        return [
            "Tornado Damage", "Stacked Hydra Shots", "Missed Hydra Shots", "Hit by the giant fish",
            "Shadow Dropoffs", "Murlock debuff uptime", "Bufferfish Uptime", "Interrupts", "Dispels"
        ]

    @property
    def score_dict(self):
        return {
            "Bufferfish Uptime": self.bufferfish_uptime, "Shadow Dropoffs": self.dropoffs,
            "Tornado Damage": self.tornado_damage, "Stacked Hydra Shots": self.stacked_hydra_shots, "Hit by the giant fish": self.hit_by_giant_fish,
            "Missed Hydra Shots": self.hydra_shots, "Murlock debuff uptime": self.murlock_debuff_uptime,
            "Interrupts": self.interrupts, "Dispels": self.dispels
        }


class MaidenScore(RaidScore):
    wrong_color = models.IntegerField(default=0)
    wrong_orb = models.IntegerField(default=0)
    didnt_jump_in_hole = models.IntegerField(default=0)

    @property
    def table_keys(self):
        return [
            "Wrong side", "Wrong orb", "Bomb explosions"
        ]

    @property
    def score_dict(self):
        return {
            "Wrong side": self.wrong_color,
            "Wrong orb": self.wrong_orb,
            "Bomb explosions": self.didnt_jump_in_hole,
        }
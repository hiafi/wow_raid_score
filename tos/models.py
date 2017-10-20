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


class DIScore(RaidScore):
    interrupts = models.IntegerField(default=0)
    grouping_jail = models.IntegerField(default=0)
    explosive_anguish = models.IntegerField(default=0)
    times_in_jail = models.IntegerField(default=0)

    @property
    def table_keys(self):
        return [
            "Times in jail", "Explosive Anguish", "Going to jail in a group", "Interrupts"
        ]

    @property
    def score_dict(self):
        return {
            "Times in jail": self.times_in_jail,
            "Explosive Anguish": self.explosive_anguish,
            "Going to jail in a group": self.grouping_jail,
            "Interrupts": self.interrupts
        }


class HarjatanScore(RaidScore):
    soaking_slams = models.IntegerField(default=0)
    stacks_of_debuff = models.IntegerField(default=0)

    @property
    def table_keys(self):
        return [
            "Soaking slams", "Debuff stacks"
        ]

    @property
    def score_dict(self):
        return {
            "Soaking slams": self.soaking_slams,
            "Debuff stacks": self.stacks_of_debuff,
        }


class SistersScore(RaidScore):
    glaive_storm = models.IntegerField(default=0)
    twilight_glaive = models.IntegerField(default=0)
    astral_vuln = models.IntegerField(default=0)
    lunar_beacon = models.IntegerField(default=0)

    @property
    def table_keys(self):
        return [
            "Glaive Storm", "Twilight Glaive", "Lunar Beacon", "Astral Vulnerability"
        ]

    @property
    def score_dict(self):
        return {
            "Glaive Storm": self.glaive_storm,
            "Twilight Glaive": self.twilight_glaive,
            "Lunar Beacon": self.lunar_beacon,
            "Astral Vulnerability": self.astral_vuln,
        }


class HostScore(RaidScore):
    dissonance = models.IntegerField(default=0)
    break_armors = models.IntegerField(default=0)
    soulbinds = models.IntegerField(default=0)
    rupturing_slam = models.IntegerField(default=0)
    tormented_cries = models.IntegerField(default=0)

    @property
    def table_keys(self):
        return [
            "Dissonance", "Breaking Armors", "Soulbind", "Rupturing Slams", "Tormented Cries"
        ]

    @property
    def score_dict(self):
        return {
            "Dissonance": self.dissonance,
            "Breaking Armors": self.break_armors,
            "Soulbind": self.soulbinds,
            "Rupturing Slams": self.rupturing_slam,
            "Tormented Cries": self.tormented_cries,
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
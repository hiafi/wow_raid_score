# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from WoWRaidScore.models import RaidScore


# Create your models here.

class TalocScore(RaidScore):
    bad_pool_drops = models.IntegerField(default=0)
    too_close_to_mace = models.IntegerField(default=0)
    blown_up_by_add = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 90

    @property
    def table_keys(self):
        return [
            "Bad Pool Drops", "Too Close to the Mace", "Blown up by the slime"
        ]

    @property
    def score_dict(self):
        return {
            "Bad Pool Drops": self.bad_pool_drops,
            "Too Close to the Mace": self.too_close_to_mace,
            "Blown up by the slime": self.blown_up_by_add
        }

    @property
    def score_description(self):
        return {
            "Soaking Annihilation": "-8 points per missed soak. +2 points for every time you soak more than one annihilation / shrapnel",
            "Hit by the laser": "-15 points per time hit by the laser (Surging Fel) during Apocalypse Drive",
            "Hit by Decimation": "-15 points per time hit by the large Decimation circle",
        }


class ZekVozScore(RaidScore):
    bad_cloud_drops = models.IntegerField(default=0)
    active_the_cloud = models.IntegerField(default=0)
    eye_beam = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 90

    @property
    def table_keys(self):
        return [
            "Bad Cloud Drops", "Touched the Cloud", "Hit others with the eyebeam"
        ]

    @property
    def score_dict(self):
        return {
            "Bad Cloud Drops": self.bad_cloud_drops,
            "Touched the Cloud": self.active_the_cloud,
            "Hit others with the eyebeam": self.eye_beam
        }

    @property
    def score_description(self):
        return {
            "Bad Cloud Drops": "-8 points per missed soak. +2 points for every time you soak more than one annihilation / shrapnel",
            "Touched the Cloud": "-15 points per time hit by the laser (Surging Fel) during Apocalypse Drive",
            "Hit others with the eyebeam": "-15 points per time hit by the large Decimation circle",
        }
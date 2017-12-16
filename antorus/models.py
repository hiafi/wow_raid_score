# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from WoWRaidScore.models import RaidScore


# Create your models here.

class WorldbreakerScore(RaidScore):
    annihilation_soaks = models.IntegerField(default=0)
    hit_from_laser = models.IntegerField(default=0)
    decimation = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 90

    @property
    def table_keys(self):
        return [
            "Soaking Annihilation", "Hit by the laser", "Hit by Decimation"
        ]

    @property
    def score_dict(self):
        return {
            "Soaking Annihilation": self.annihilation_soaks,
            "Hit by the laser": self.hit_from_laser,
            "Hit by Decimation": self.decimation
        }

    @property
    def score_description(self):
        return {
            "Soaking Annihilation": "-8 points per missed soak. +2 points for every time you soak more than one annihilation / shrapnel",
            "Hit by the laser": "-15 points per time hit by the laser (Surging Fel) during Apocalypse Drive",
            "Hit by Decimation": "-15 points per time hit by the large Decimation circle",
        }


class FelhoundsScore(RaidScore):
    molten_flare = models.IntegerField(default=0)
    consuming_sphere = models.IntegerField(default=0)
    desolate_path = models.IntegerField(default=0)
    enflamed = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 50

    @property
    def table_keys(self):
        return [
            "Molten Flare", "Stood in the Sphere", "Desolate Path", "Enflamed"
        ]

    @property
    def score_dict(self):
        return {
            "Molten Flare": self.molten_flare,
            "Stood in the Sphere": self.consuming_sphere,
            "Desolate Path": self.desolate_path,
            "Enflamed": self.enflamed,
        }


class HighCommandScore(RaidScore):
    step_on_mines = models.IntegerField(default=0)
    bladestorm = models.IntegerField(default=0)
    good_use_of_pod = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 90

    @property
    def table_keys(self):
        return [
            "Stepped on a mine", "Bladestorm", "Used the pods well"
        ]

    @property
    def score_dict(self):
        return {
            "Stepped on a mine": self.step_on_mines,
            "Bladestorm": self.bladestorm,
            "Used the pods well": self.good_use_of_pod
        }

    @property
    def score_description(self):
        return {
            "Bladestorm": "-1 * amount of times hit by the same blade storm past the second tick (EX: 6 points (3 + 2 + 1) for 5 ticks)",
            "Stepped on a mine": "-5 points for each mine stepped on. Ignores mines that were stepped on if only you take damage from it and there are less than 2 stacks",
        }


class PortalKeeperScore(RaidScore):
    felstorm_barrage = models.IntegerField(default=0)
    missed_orb_pickup = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 50

    @property
    def table_keys(self):
        return [
            "Felstorm Barrage", "Messed up the orb"
        ]

    @property
    def score_dict(self):
        return {
            "Felstorm Barrage": self.felstorm_barrage,
            "Messed up the orb": self.missed_orb_pickup
        }


class EonarScore(RaidScore):
    rain_of_fire_splash = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 50

    @property
    def table_keys(self):
        return [
            "Splashing Rain of Fire"
        ]

    @property
    def score_dict(self):
        return {
            "Splashing Rain of Fire": self.rain_of_fire_splash
        }


class ImonarScore(RaidScore):
    stepping_on_mines = models.IntegerField(default=0)
    sleep_canister = models.IntegerField(default=0)
    charged_blasts = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 50

    @property
    def table_keys(self):
        return [
            "Stepped on a mine", "Sleep Canister", "Charged Blast"
        ]

    @property
    def score_dict(self):
        return {
            "Stepped on a mine": self.stepping_on_mines,
            "Sleep Canister": self.sleep_canister,
            "Charged Blast": self.charged_blasts
        }


class KingarothScore(RaidScore):
    ruiner = models.IntegerField(default=0)
    annihilation_soaks = models.IntegerField(default=0)
    destruction_soaks = models.IntegerField(default=0)
    decimation = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 50

    @property
    def table_keys(self):
        return [
            "Ruiner", "Soaking Annihilation", "Hit by Decimation", "Soaked Destruction"
        ]

    @property
    def score_dict(self):
        return {
            "Ruiner": self.ruiner,
            "Soaking Annihilation": self.annihilation_soaks,
            "Hit by Decimation": self.decimation,
            "Soaked Destruction": self.destruction_soaks
        }


class VarimathrasScore(RaidScore):
    bad_embrace = models.IntegerField(default=0)
    bad_arrows = models.IntegerField(default=0)
    fissure = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 50

    @property
    def table_keys(self):
        return [
            "Bad Embrace", "Hit the tank with an arrow", "Hit by shadow fissure"
        ]

    @property
    def score_dict(self):
        return {
            "Bad Embrace": self.bad_embrace,
            "Hit the tank with an arrow": self.bad_arrows,
            "Hit by shadow fissure": self.fissure
        }

    @property
    def score_description(self):
        return {
            "Hit by shadow fissure": "-5 points for each tick you take from Shadow Fissure.",
        }


class CovenScore(RaidScore):
    storm_damage = models.IntegerField(default=0)
    norgannon = models.IntegerField(default=0)
    khazgoroth = models.IntegerField(default=0)
    golganoth = models.IntegerField(default=0)
    whirlwind = models.IntegerField(default=0)
    shadowblades = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            "Storm of Darkness hits", "Shadowblade damage", "Whirlwind damage", "Norgannon damage",
            "Khazgoroth damage", "Golganoth damage"
        ]

    @property
    def score_dict(self):
        return {
            "Storm of Darkness hits": self.storm_damage,
            "Shadowblade damage": self.shadowblades,
            "Whirlwind damage": self.whirlwind,
            "Norgannon damage": self.norgannon,
            "Khazgoroth damage": self.khazgoroth,
            "Golganoth damage": self.golganoth
        }

    @property
    def score_description(self):
        return {
            "Norgannon damage": "-30 points (-20 if you are tank) for each time you are hit by a walking Norgannon add.",
            "Khazgoroth damage": "-10 points for each tick you take from the flames of Khazgoroth",
            "Golganoth damage": "-5 points for each tick you take from the lightning of Golganoth",
            "Whirlwind damage": "-3 points when you are hit by the blade landing and -3 points for each tick you take from the spinning blades",
            "Shadowblade damage": "-5 points each time you are hit by a shadowblade",
            "Storm of Darkness hits": "-5 points for each tick you take from storm of darkness beyond the 2nd tick for each storm.",
        }


class AggramarScore(RaidScore):
    soaking_combo = models.IntegerField(default=0)
    flare_damage = models.IntegerField(default=0)
    blaze_damage = models.IntegerField(default=0)
    wake_of_flame = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 50

    @property
    def table_keys(self):
        return [
            "Soaking the combo", "Wake of Flames damage", "Blaze damage", "Flare damage"
        ]

    @property
    def score_dict(self):
        return {
            "Soaking the combo": self.soaking_combo,
            "Wake of Flames damage": self.wake_of_flame,
            "Blaze damage": self.blaze_damage,
            "Flare damage": self.flare_damage
        }


class ArgusScore(RaidScore):
    bomb_burst_damage = models.IntegerField(default=0)
    death_fog = models.IntegerField(default=0)
    scythe = models.IntegerField(default=0)
    cosmic_ray = models.IntegerField(default=0)
    ember_of_rage = models.IntegerField(default=0)

    @property
    def base_score(self):
        return 50

    @property
    def table_keys(self):
        return [
            "Soulbomb and Soulburst damage", "Hit by Death Fog", "Hit by Scythe", "Hit by Cosmic Ray",
            "Hit by Ember of Rage"
        ]

    @property
    def score_dict(self):
        return {
            "Soulbomb and Soulburst damage": self.bomb_burst_damage,
            "Hit by Death Fog": self.death_fog,
            "Hit by Scythe": self.scythe,
            "Hit by Cosmic Ray": self.cosmic_ray,
            "Hit by Ember of Rage": self.ember_of_rage
        }

    @property
    def score_description(self):
        return {
            "Hit by Death Fog": "-1 point for each tick of death fog you take.",
            "Hit by Scythe": "-5 points for each time you are hit by scythe in phase 2.",
            "Hit by Ember of Rage": "-10 points for each Ember of Rage (small swirl) stack you get in phase 4.",
        }

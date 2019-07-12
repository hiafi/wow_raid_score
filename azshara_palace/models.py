# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from WoWRaidScore.models import RaidScore


class AzsharaScore(RaidScore):
    sanction = models.IntegerField(default=0)
    beckon = models.IntegerField(default=0)
    detonation = models.IntegerField(default=0)
    drained_soul = models.IntegerField(default=0)

    sanction_str = "Sanction"
    beckon_str = "Beckon"
    detonation_str = "Detonation"
    drained_soul_str = "Drained Soul Soak"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.sanction_str,
            self.beckon_str,
            self.detonation_str,
            self.drained_soul_str,
        ]

    @property
    def score_dict(self):
        return {
            self.sanction_str: self.sanction,
            self.beckon_str: self.beckon,
            self.detonation_str: self.detonation,
            self.drained_soul_str: self.drained_soul,
        }

    @property
    def score_description(self):
        return {
            self.sanction_str: "Getting hit by flames of punishment while on the fire side (right side). The best way to handle this mechanic is to stand in melee range right behind the boss.",
            self.beckon_str: "Standing too close to another player when dropping off volatile charge causes a large burst of damage that is often leathal. Try to stay out of the way when dropping off Volatile charge.",
            self.detonation_str: "You lose points by being hit by crush. Crush happens in phase 1 where the add slams half of the room, being hit by this stuns and deals damage.",
            self.drained_soul_str: "You lose points by being hit by crush. Crush happens in phase 1 where the add slams half of the room, being hit by this stuns and deals damage.",
        }

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from WoWRaidScore.models import RaidScore


class ChampionScore(RaidScore):
    wave_of_light = models.IntegerField(default=0)
    divine_mallet = models.IntegerField(default=0)
    blinding_faith = models.IntegerField(default=0)

    wave_of_light_str = "Wave of Light"
    divine_mallet_str = "Divine Mallet"
    blinding_faith_str = "Blinding Faith"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.wave_of_light_str,
            self.divine_mallet_str,
            self.blinding_faith_str,
        ]

    @property
    def score_dict(self):
        return {
            self.wave_of_light_str: self.wave_of_light,
            self.divine_mallet_str: self.divine_mallet,
            self.blinding_faith_str: self.blinding_faith,
        }

    @property
    def score_description(self):
        return {
            self.wave_of_light_str: "Getting hit by flames of punishment while on the fire side (right side). The best way to handle this mechanic is to stand in melee range right behind the boss.",
            self.divine_mallet_str: "Standing too close to another player when dropping off volatile charge causes a large burst of damage that is often leathal. Try to stay out of the way when dropping off Volatile charge.",
            self.blinding_faith_str: "You lose points by being hit by crush. Crush happens in phase 1 where the add slams half of the room, being hit by this stuns and deals damage.",
        }


class JadefireScore(RaidScore):
    multisided_strike = models.IntegerField(default=0)
    beam = models.IntegerField(default=0)
    phoenix_strike = models.IntegerField(default=0)
    failed_trap_fall = models.IntegerField(default=0)

    multisided_strike_str = "Multi-Sided Strike"
    beam_str = "P1 Beam"
    phoenix_strike_str = "P2 Swirls"
    failed_trap_fall_str = "Failed Flame Traps (falling)"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.multisided_strike_str,
            self.beam_str,
            self.phoenix_strike_str,
            self.failed_trap_fall_str,
        ]

    @property
    def score_dict(self):
        return {
            self.multisided_strike_str: self.multisided_strike,
            self.beam_str: self.beam,
            self.phoenix_strike_str: self.phoenix_strike,
            self.failed_trap_fall_str: self.failed_trap_fall,
        }

    @property
    def score_description(self):
        return {
            self.multisided_strike_str: "Getting hit by flames of punishment while on the fire side (right side). The best way to handle this mechanic is to stand in melee range right behind the boss.",
            self.beam_str: "Standing too close to another player when dropping off volatile charge causes a large burst of damage that is often leathal. Try to stay out of the way when dropping off Volatile charge.",
            self.phoenix_strike_str: "You lose points by being hit by crush. Crush happens in phase 1 where the add slams half of the room, being hit by this stuns and deals damage.",
            self.failed_trap_fall_str: "You lose points by being hit by crush. Crush happens in phase 1 where the add slams half of the room, being hit by this stuns and deals damage.",
        }


class GrongScore(RaidScore):
    fear = models.IntegerField(default=0)
    chill_of_death = models.IntegerField(default=0)
    deathly_echo = models.IntegerField(default=0)
    not_running_out_throw = models.IntegerField(default=0)

    fear_str = "Fear"
    chill_of_death_str = "Chill of Death"
    deathly_echo_str = "Deathly Echo"
    not_running_out_throw_str = "Not running throw out"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.fear_str,
            self.chill_of_death_str,
            self.deathly_echo_str,
            self.not_running_out_throw_str,
        ]

    @property
    def score_dict(self):
        return {
            self.fear_str: self.fear,
            self.chill_of_death_str: self.chill_of_death,
            self.deathly_echo_str: self.deathly_echo,
            self.not_running_out_throw_str: self.not_running_out_throw,
        }

    @property
    def score_description(self):
        return {
            self.fear_str: "Getting hit by flames of punishment while on the fire side (right side). The best way to handle this mechanic is to stand in melee range right behind the boss.",
            self.chill_of_death_str: "Standing too close to another player when dropping off volatile charge causes a large burst of damage that is often leathal. Try to stay out of the way when dropping off Volatile charge.",
        }


class OpulenceScore(RaidScore):
    flames_of_punishment = models.IntegerField(default=0)
    volatile_charge = models.IntegerField(default=0)
    crush = models.IntegerField(default=0)
    flame_jets = models.IntegerField(default=0)
    lasers = models.IntegerField(default=0)
    molten_gold = models.IntegerField(default=0)
    deadly_hex = models.IntegerField(default=0)

    flames_of_punishment_str = "Flames of Punishment"
    volatile_charge_str = "Volatile Charge"
    crush_str = "Crush"
    flame_jets_str = "Flame Jets"
    lasers_str = "Scorching Ground (laser)"
    molten_gold_str = "Molten Gold"
    deadly_hex_str = "Deadly Hex"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.flames_of_punishment_str,
            self.volatile_charge_str,
            self.crush_str,
            self.flame_jets_str,
            self.lasers_str,
            self.molten_gold_str,
            self.deadly_hex_str
        ]

    @property
    def score_dict(self):
        return {
            self.flames_of_punishment_str: self.flames_of_punishment,
            self.volatile_charge_str: self.volatile_charge,
            self.crush_str: self.crush,
            self.flame_jets_str: self.flame_jets,
            self.lasers_str: self.lasers,
            self.molten_gold_str: self.molten_gold,
            self.deadly_hex_str: self.deadly_hex,
        }

    @property
    def score_description(self):
        return {
            self.flames_of_punishment_str: "Getting hit by flames of punishment while on the fire side (right side). The best way to handle this mechanic is to stand in melee range right behind the boss.",
            self.volatile_charge_str: "Standing too close to another player when dropping off volatile charge causes a large burst of damage that is often leathal. Try to stay out of the way when dropping off Volatile charge.",
            self.crush_str: "You lose points by being hit by crush. Crush happens in phase 1 where the add slams half of the room, being hit by this stuns and deals damage.",
            self.flame_jets_str: "Flame jets are fairly nasty on mythic, especially lightening side. Taking 2 or more ticks will give you a -3 penalty per tick after the first one.",
            self.lasers_str: "Standing in the fire from the laser is bad. Taking 2 or more ticks in a row will give you a -2 penalty per tick after the first.",
        }


class ConclaveScore(RaidScore):
    lacerating_claws = models.IntegerField(default=0)
    kimbul_wrath = models.IntegerField(default=0)
    kragwa_wrath = models.IntegerField(default=0)
    static_orb = models.IntegerField(default=0)
    paku_wrath = models.IntegerField(default=0)
    raptor_damage = models.IntegerField(default=0)

    lacerating_claws_str = "Lacerating Claws"
    kimbul_wrath_str = "Kimbul\'s Wrath"
    kragwa_wrath_str = "Krag\'wa's Wrath"
    static_orb_str = "Static Orb"
    paku_wrath_str = "Pa\'ku's Wrath"
    raptor_damage_str = "Raptors"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.lacerating_claws_str,
            self.kimbul_wrath_str,
            self.kragwa_wrath_str,
            self.static_orb_str,
            self.paku_wrath_str,
            self.raptor_damage_str,
        ]

    @property
    def score_dict(self):
        return {
            self.lacerating_claws_str: self.lacerating_claws,
            self.kimbul_wrath_str: self.kimbul_wrath,
            self.kragwa_wrath_str: self.kragwa_wrath,
            self.static_orb_str: self.static_orb,
            self.paku_wrath_str: self.paku_wrath,
            self.raptor_damage_str: self.raptor_damage,
        }

    @property
    def score_description(self):
        return {
            self.lacerating_claws_str: "Lacerating Claws is a frontal cleave by Kimbul and should only be taken by tanks. Any DPS or healers hit by this are standing in front of the boss.",
            self.kimbul_wrath_str: "Kimbul's mechanic will target 4 players and leap between them. Standing too close to a target will cause them to be stunned and take a permanent bleed causing a lot of damage.",
            self.kragwa_wrath_str: "Krag'wa will occasionally jump to the furthest target creating a large damage zone knocking players back and dealing damage, this is espcially bad during Pa'ku's wrath.",
            self.static_orb_str: "Static Orb is caused by Akuna. When the debuff expires 5 orbs are created, touching one of them will cause damage and will stun",
            self.paku_wrath_str: "Every minute, Pa'ku will fly down and deal a lot of damage to anyone who isn't standing near him.",
            self.raptor_damage_str: "Raptors chase you through the room. If you bring them close to the other raptors it increases their speed.",
        }


class RhastakhanScore(RaidScore):
    deathly_withering = models.IntegerField(default=0)
    toads = models.IntegerField(default=0)
    seal_of_purification = models.IntegerField(default=0)
    plague_of_fire = models.IntegerField(default=0)

    deathly_withering_str = "Deathly Withering"
    toads_str = "Toads"
    seal_of_purification_str = "Seal of Purification"
    plague_of_fire_str = "Plague of Fire"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.deathly_withering_str,
            self.toads_str,
            self.seal_of_purification_str,
            self.plague_of_fire_str
        ]

    @property
    def score_dict(self):
        return {
            self.deathly_withering_str: self.deathly_withering,
            self.toads_str: self.toads,
            self.seal_of_purification_str: self.seal_of_purification,
            self.plague_of_fire_str: self.plague_of_fire,
        }

    @property
    def score_description(self):
        return {
            self.deathly_withering_str: "Standing near Bwamsandi in P2 or not clearing your stacks in P3 can lead to massive issues. After 20 stacks, this becomes a serious issue.",
            self.toads_str: "Occasionally a wave of toads will be fired off. Getting hit by these toads puts a fairly massive dot on you and should be avoided.",
            self.seal_of_purification_str: "In mythic, Seal of purification leaves a flame trial following the laser, standing in this causes a lot of unneeded damage.",
            self.plague_of_fire_str: "Every 30 seconds or so, Rhastakhan will put plague of fire on players. If those players are not spread out, nearby players will be affected by their plague of fire leading to massive issues of spreading.",
        }


class MekkatorqueScore(RaidScore):
    buster_cannon = models.IntegerField(default=0)
    blastoff = models.IntegerField(default=0)
    trample = models.IntegerField(default=0)
    failed_bots = models.IntegerField(default=0)
    sheep = models.IntegerField(default=0)
    gigavolt_blast = models.IntegerField(default=0)
    radiation = models.IntegerField(default=0)

    buster_cannon_str = "Buster Cannon"
    blastoff_str = "Blast off / Crash Down"
    trample_str = "Trampled"
    failed_bots_str = "Failed Bot"
    sheep_str = "Sheep Shrapnel"
    gigavolt_blast_str = "Gigavolt Blast"
    radiation_str = "Radiation"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.buster_cannon_str,
            self.blastoff_str,
            self.trample_str,
            self.failed_bots_str,
            self.sheep_str,
            self.gigavolt_blast_str,
            self.radiation_str,
        ]

    @property
    def score_dict(self):
        return {
            self.buster_cannon_str: self.buster_cannon,
            self.blastoff_str: self.blastoff,
            self.trample_str: self.trample,
            self.failed_bots_str: self.failed_bots,
            self.sheep_str: self.sheep,
            self.radiation_str: self.radiation,
        }

    @property
    def score_description(self):
        return {
            self.buster_cannon_str: "",
            self.blastoff_str: "",
            self.trample_str: "",
            self.failed_bots_str: "",
            self.sheep_str: "",
            self.gigavolt_blast_str: "",
            self.radiation_str: "",
        }


class BlockadeScore(RaidScore):
    voltaic_flash = models.IntegerField(default=0)
    sea_swell = models.IntegerField(default=0)
    sea_storm = models.IntegerField(default=0)
    torrential_swell = models.IntegerField(default=0)

    voltaic_flash_str = "Voltaic Flash"
    sea_swell_str = "Sea Swell"
    sea_storm_str = "Sea Storm"
    torrential_swell_str = "Torrential Swell"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.voltaic_flash_str,
            self.sea_swell_str,
            self.sea_storm_str,
            self.torrential_swell_str,
        ]

    @property
    def score_dict(self):
        return {
            self.voltaic_flash_str: self.voltaic_flash,
            self.sea_swell_str: self.sea_swell,
            self.sea_storm_str: self.sea_storm,
            self.torrential_swell_str: self.torrential_swell,
        }

    @property
    def score_description(self):
        return {
            self.voltaic_flash_str: "",
            self.sea_swell_str: "",
            self.sea_storm_str: "",
            self.torrential_swell_str: "",
        }


class JainaScore(RaidScore):
    avalanche = models.IntegerField(default=0)
    glacial_ray = models.IntegerField(default=0)
    glacial_shards = models.IntegerField(default=0)
    icefall = models.IntegerField(default=0)

    avalanche_str = "Avalanche"
    glacial_ray_str = "Avalanche"
    glacial_shards_str = "Avalanche"
    icefall_str = "Avalanche"

    @property
    def base_score(self):
        return 100

    @property
    def table_keys(self):
        return [
            self.avalanche_str,
            self.glacial_ray_str,
            self.glacial_shards_str,
            self.icefall_str,
        ]

    @property
    def score_dict(self):
        return {
            self.avalanche_str: self.avalanche,
            self.glacial_ray_str: self.glacial_ray,
            self.glacial_shards_str: self.glacial_shards,
            self.icefall_str: self.icefall,
        }

    @property
    def score_description(self):
        return {
            self.avalanche_str: "",
            self.glacial_ray_str: "",
            self.glacial_shards_str: "",
            self.icefall_str: "",
        }
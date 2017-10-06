from WoWRaidScore.models import RaidScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes

import math


class SpecInfo(object):
    DH_VENG = None
    DH_HAVOC = None
    DK_BLOOD = 250
    DK_FROST = 251
    DK_UNHOLY = None
    DRUID_GUARDIAN = 104
    DRUID_BALANCE = 102
    DRUID_FERAL = None
    DRUID_RESTO = 105
    HUNTER_BM = None
    HUNTER_MM = None
    HUNTER_SV = None
    MAGE_ARCANE = None
    MAGE_FIRE = None
    MAGE_FROST = None
    MONK_MW = 270
    MONK_BM = 268
    MONK_WW = 269
    PALADIN_HOLY = None
    PALADIN_RET = None
    PALADIN_PROT = None
    PRIEST_HOLY = 257
    PRIEST_DISC = None
    PRIEST_SHADOW = 258
    ROGUE_SUB = 261
    ROGUE_ASS = None
    SHAMAN_RESTO = 264
    SHAMAN_ELE = None
    SHAMAN_ENH = 263
    WARLOCK_AFF = None
    WARLOCK_DESTR = None
    WARLOCK_DEMO = 266
    WARRIOR_PROT = None
    WARRIOR_ARMS = 72
    WARRIOR_FURY = None


class BossAnalyzer(object):
    SCORE_OBJ = RaidScore
    STOP_AT_DEATH = 7

    NORMAL_DIFFICULTY = 1
    HEROIC_DIFFICULTY = 2
    MYTHIC_DIFFICULTY = 5

    def __init__(self, wcl_fight, wcl_client, score_objs, actors):
        self.wcl_fight = wcl_fight
        self.client = wcl_client
        self.score_objs = score_objs
        self.actors = actors

        self._cached_deaths = {}

    def cleanup(self):
        self._cached_deaths = {}

    @staticmethod
    def distance_calculation(coord1, coord2):
        return math.sqrt(math.pow(coord2[0] - coord1[0], 2) + math.pow(coord2[1] - coord1[1], 2))

    @staticmethod
    def between_duration(start_time, end_time, time_to_check):
        return start_time <= time_to_check <= end_time

    def check_for_wipe(self, event, death_count=None, time_count=None, ignore_percent=20.0):
        """
        Returns if it is a wipe
        :param event:
        :param death_count:
        :param time_count:
        :param ignore_percent:
        :return: True if it is a wipe, False otherwise
        """
        death_time = self.wcl_fight.end_time_str
        wipe_time = self.wcl_fight.end_time_str
        if self.wcl_fight.percent >= ignore_percent:
            death_time = self.get_wipe_time(death_count)
            last_twenty = int((self.wcl_fight.end_time_str - self.wcl_fight.start_time_str) * 0.2)
            if time_count is None:
                wipe_time = self.wcl_fight.end_time_str - max(20000, last_twenty)
            else:
                wipe_time = self.wcl_fight.end_time_str - time_count
        if (death_time and event.timestamp > death_time) or (wipe_time and event.timestamp > wipe_time):
            return True
        return False

    @classmethod
    def create_raid_scores(cls, players, fight, specs):
        scores = {}
        for player in players:
            scores[player] = cls.create_raid_score_obj(player, fight, specs.get(player))
        return scores

    def save_score_objs(self):
        for score_obj in self.score_objs.values():
            score_obj.save()

    @classmethod
    def create_raid_score_obj(cls, player, fight, spec):
        melee_dps_specs = {
            259,
            70,
            71,
            577,
            SpecInfo.SHAMAN_ENH,  # Enh Shaman
            SpecInfo.MONK_WW,  # WW monk
            SpecInfo.WARRIOR_ARMS,  # Arms war
            SpecInfo.DK_FROST,  # Frost DK
            SpecInfo.ROGUE_SUB,  # sub rogue
        }
        ranged_dps_specs = {
            258,  #
            102,  # balance druid
            254,  #
            265,  # affliction lock
            267,  # destruction lock
            64,  # frost mage
            262,  # Ele shaman
            SpecInfo.WARLOCK_DEMO,
        }
        healer_specs = {
            SpecInfo.DRUID_RESTO,
            SpecInfo.MONK_MW,
            SpecInfo.SHAMAN_RESTO,
            SpecInfo.PALADIN_HOLY,
            SpecInfo.PRIEST_HOLY,
            SpecInfo.PRIEST_DISC,
        }
        tank_specs = {
            SpecInfo.MONK_BM,  # BM monk
            SpecInfo.DRUID_GUARDIAN,  # druid
            SpecInfo.DK_BLOOD,  # blood dk
            SpecInfo.WARRIOR_PROT,  # blood dk
            SpecInfo.PALADIN_PROT,  # blood dk
            SpecInfo.DH_VENG,  # blood dk
        }
        if spec not in melee_dps_specs and spec not in ranged_dps_specs and spec not in healer_specs and spec not in tank_specs:
            print("Unable to find spec {} ({})".format(spec, player.safe_name))
        return cls.SCORE_OBJ(player=player, fight=fight, spec=spec,
                             melee_dps=spec in melee_dps_specs,
                             ranged_dps=spec in ranged_dps_specs,
                             tank=spec in tank_specs,
                             healer=spec in healer_specs)

    def get_player_death_times(self):
        if self._cached_deaths != {}:
            return self._cached_deaths
        deaths = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={"type": WCLEventTypes.death},
                                            actors_obj_dict=self.actors):
            if event.target_is_friendly and event.target != "Unknown" and not isinstance(event.target, int):
                deaths[event.target] = event.timestamp
        self._cached_deaths = deaths
        return deaths

    def get_player_death_order(self):
        deaths = self.get_player_death_times()
        tmp = sorted([(death_time, player) for player, death_time in deaths.items()], key=lambda x: x[0])
        return [p[1] for p in tmp]

    def get_player_death_number(self):
        return {player: i+1 for i, player in enumerate(self.get_player_death_order())}

    def get_wipe_time(self, number_of_deaths=None):
        if number_of_deaths is None:
            number_of_deaths = int(len(self.score_objs) * 0.35)
        death_order = self.get_player_death_order()
        death_time = None
        if len(death_order) > number_of_deaths:
            death_time = self.get_player_death_times().get(death_order[number_of_deaths])
        return death_time

    def analyze(self):
        raise NotImplementedError()

from WoWRaidScore.models import RaidScore, FightEvent
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict
from WoWRaidScore.wcl_utils.wcl_util_functions import get_readable_time
from wow_raid_score.settings import DEBUG_EVENTS

import math


class PlayerStatus(object):
    def __init__(self, damage_event):
        self.player_hp = damage_event.hp_remaining
        self.max_hp = damage_event.hp_max
        self.point_x = damage_event.point_x
        self.point_y = damage_event.point_y

    @property
    def location(self):
        return (self.point_x, self.point_y)

    @property
    def hp_percent(self):
        return float(self.player_hp) / self.max_hp

    def __str__(self):
        return "<PlayerStatus - {} / {} {}".format(self.player_hp, self.max_hp, self.location)

    def __repr__(self):
        return self.__str__()


class SpecInfo(object):
    DH_VENG = 581
    DH_HAVOC = 577
    DK_BLOOD = 250
    DK_FROST = 251
    DK_UNHOLY = 252
    DRUID_GUARDIAN = 104
    DRUID_BALANCE = 102
    DRUID_FERAL = 103
    DRUID_RESTO = 105
    HUNTER_BM = 253
    HUNTER_MM = 254
    HUNTER_SV = None
    MAGE_ARCANE = 62
    MAGE_FIRE = 63
    MAGE_FROST = 64
    MONK_MW = 270
    MONK_BM = 268
    MONK_WW = 269
    PALADIN_HOLY = 65
    PALADIN_RET = 70
    PALADIN_PROT = 66
    PRIEST_HOLY = 257
    PRIEST_DISC = 256
    PRIEST_SHADOW = 258
    ROGUE_SUB = 261
    ROGUE_ASS = 259
    ROGUE_OUTLAW = 260
    SHAMAN_RESTO = 264
    SHAMAN_ELE = 262
    SHAMAN_ENH = 263
    WARLOCK_AFF = 265
    WARLOCK_DESTR = 267
    WARLOCK_DEMO = 266
    WARRIOR_PROT = 73
    WARRIOR_ARMS = 72
    WARRIOR_FURY = None

    melee_dps_specs = {
        SHAMAN_ENH,  # Enh Shaman
        MONK_WW,  # WW monk
        WARRIOR_ARMS,  # Arms war
        DK_FROST,  # Frost DK
        DK_UNHOLY,
        ROGUE_SUB,  # sub rogue
        ROGUE_OUTLAW,
        ROGUE_ASS,
        DRUID_FERAL,
        PALADIN_RET
    }
    ranged_dps_specs = {
        DH_HAVOC,
        PRIEST_SHADOW,
        DRUID_BALANCE,
        HUNTER_BM,
        HUNTER_MM,
        WARLOCK_AFF,
        WARLOCK_DESTR,
        WARLOCK_DEMO,
        MAGE_FROST,
        MAGE_FIRE,
        MAGE_ARCANE,
        SHAMAN_ELE,
    }
    healer_specs = {
        DRUID_RESTO,
        MONK_MW,
        SHAMAN_RESTO,
        PALADIN_HOLY,
        PRIEST_HOLY,
        PRIEST_DISC,
    }
    tank_specs = {
        MONK_BM,
        DRUID_GUARDIAN,
        DK_BLOOD,
        WARRIOR_PROT,
        PALADIN_PROT,
        DH_VENG,
    }


class BossAnalyzer(object):
    DEBUG = False
    SCORE_OBJ = RaidScore
    STOP_AT_DEATH = 7

    NORMAL_DIFFICULTY = 3
    HEROIC_DIFFICULTY = 4
    MYTHIC_DIFFICULTY = 5

    def debug_message(self, message):
        if self.DEBUG:
            print(message)

    def __init__(self, wcl_fight, wcl_client, score_objs, actors, fight_obj):
        self.wcl_fight = wcl_fight
        self.client = wcl_client
        self.score_objs = score_objs
        self.actors = actors
        self.fight_obj = fight_obj

        self._cached_deaths = {}
        self._cached_status = defaultdict(dict)
        self._cached_defensives = defaultdict(list)

    def cleanup(self):
        self._cached_deaths = {}
        self._cached_status = {}
        self._cached_defensives = {}

    @staticmethod
    def distance_calculation(coord1, coord2):
        return math.sqrt(math.pow(coord2[0] - coord1[0], 2) + math.pow(coord2[1] - coord1[1], 2))

    @staticmethod
    def angle_between_points(origin, destination):
        hyp = BossAnalyzer.distance_calculation(origin, destination)
        opp = float(destination[1] - origin[1])
        return math.degrees(math.asin(opp/hyp))

    @staticmethod
    def between_duration(start_time, time_to_check, end_time):
        return start_time <= time_to_check <= end_time

    @staticmethod
    def between_multiple_durations(time_to_check, durations):
        if not time_to_check:
            return False
        for (start_time, end_time) in durations:
            if start_time is None or end_time is None:
                continue
            if start_time <= time_to_check <= end_time:
                return True
        return False

    def get_debuff_start_and_end(self, ability_name, target=None):
        debuffs = defaultdict(list)
        tmp_store = {}
        if target is not None:
            actor_id = self.get_actor_id(target)
        else:
            actor_id = None
        for event in self.client.get_events(self.wcl_fight, actor_id=actor_id,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.remove_debuff],
                                                "ability.name": ability_name
                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_debuff:
                tmp_store[event.target] = event.timestamp
            else:
                debuffs[event.target].append((tmp_store.get(event.target), event.timestamp))
                tmp_store[event.target] = None
        for person, start_time in tmp_store.items():
            if start_time is not None:
                debuffs[person].append((start_time, self.wcl_fight.end_time_str))
        return debuffs

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
        if spec not in SpecInfo.melee_dps_specs and spec not in SpecInfo.ranged_dps_specs and spec not in SpecInfo.healer_specs and spec not in SpecInfo.tank_specs:
            print("Unable to find spec {} ({})".format(spec, player.safe_name))
        if spec is None:
            print("Unable to determine spec {} - {} - {}".format(spec, player.safe_name, fight))
        return cls.SCORE_OBJ(player=player, fight=fight, spec=spec,
                             melee_dps=spec in SpecInfo.melee_dps_specs,
                             ranged_dps=spec in SpecInfo.ranged_dps_specs,
                             tank=spec in SpecInfo.tank_specs,
                             healer=spec in SpecInfo.healer_specs)

    def get_big_defensives(self):
        if self._cached_defensives:
            return self._cached_defensives
        temp = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={"type": [WCLEventTypes.apply_buff, WCLEventTypes.remove_buff],
                                                "ability.name": ["Metamorphosis", "Dispersion"]
                                                 },
                                            actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_buff:
                temp[event.target] = event.timestamp
            else:
                if event.target in temp:
                    self._cached_defensives[event.target].append((temp[event.target], event.timestamp))
                    del temp[event.target]
                elif event.timestamp - self.wcl_fight.start_time_str <= 30000:
                    self._cached_defensives[event.target].append((self.wcl_fight.start_time_str, event.timestamp))
        for person, timestamp in temp.items():
            self._cached_defensives[person].append((timestamp, self.wcl_fight.end_time_str))
        return self._cached_defensives

    def check_for_a_defensive_used(self, event, target):
        defensives = self.get_big_defensives().get(target, [])
        for (defensive_start, defensive_end) in defensives:
            if self.between_duration(defensive_start, event.timestamp, defensive_end):
                return True
        return False

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

    def create_score_event(self, timestamp, text, player=None, point_value=None):
        if DEBUG_EVENTS:
            tmin, tsec = get_readable_time(timestamp, self.wcl_fight.start_time_str)
            print("[{}:{:02d}] {} - {}".format(tmin, tsec, player.safe_name, text))
        minute, second = get_readable_time(timestamp, self.wcl_fight.start_time_str)
        fe = FightEvent(fight=self.fight_obj, player=player, minute=minute, second=second,
                        text=text, score_value=point_value)
        fe.save()

    def get_player_death_order(self):
        deaths = self.get_player_death_times()
        tmp = sorted([(death_time, player) for player, death_time in deaths.items()], key=lambda x: x[0])
        return [p[1] for p in tmp]

    def get_player_death_number(self):
        return {player: i+1 for i, player in enumerate(self.get_player_death_order())}

    def get_wipe_time(self, number_of_deaths=None):
        if number_of_deaths is None:
            number_of_deaths = int(len(self.score_objs) * 0.30)
        death_order = self.get_player_death_order()
        death_time = None
        if len(death_order) > number_of_deaths:
            death_time = self.get_player_death_times().get(death_order[number_of_deaths])
        return death_time

    def get_actor_id(self, actor):
        for id, actor_obj in self.actors.items():
            if actor == actor_obj:
                return id
        return None

    def _player_status_from_damage(self, player, timestamp, roll_back):
        latest_event = None
        for event in self.client.get_events(self.wcl_fight,
                                            start_time=timestamp - roll_back,
                                            end_time=timestamp,
                                            filters={"type": [WCLEventTypes.damage, WCLEventTypes.heal], "target.name": player.name},
                                            actors_obj_dict=self.actors):
            if event.hp_remaining and event.point_x and event.point_y and not isinstance(event.target, int) and event.target_is_friendly:
                latest_event = PlayerStatus(event)
        return latest_event

    def _player_status_from_cast(self, player, timestamp, roll_back, require_hp=True, require_loc=True):
        latest_event = None
        for event in self.client.get_events(self.wcl_fight,
                                            start_time=timestamp - roll_back,
                                            end_time=timestamp,
                                            filters={"type": WCLEventTypes.cast, "target.name": player.name},
                                            actors_obj_dict=self.actors):
            try:
                if event.point_x and event.point_y:
                    latest_event = PlayerStatus(event)
            except AttributeError:
                pass
        return latest_event

    def get_player_status_at_time(self, player, timestamp, time_to_look_back=None, cache=False):
        if self._cached_status.get(timestamp, {}).get(player):
            return self._cached_status.get(timestamp, {}).get(player)
        if time_to_look_back is None:
            time_to_look_back = (1000, 2000, 5000)
        if isinstance(time_to_look_back, int):
            time_to_look_back = (time_to_look_back,)
        latest_event = None
        for advancing_rollback in time_to_look_back:
            latest_event = self._player_status_from_damage(player, timestamp, advancing_rollback)
            if latest_event:
                break
        if cache:
            self._cached_status[timestamp][player] = latest_event
        return latest_event

    def get_all_player_status_at_time(self, timestamp, time_to_look_back=None, cache=False):
        status = {}
        if self._cached_status.get(timestamp):
            return self._cached_status.get(timestamp)
        if time_to_look_back is None:
            time_to_look_back = (1000, 2000, 5000)
        if isinstance(time_to_look_back, int):
            time_to_look_back = (time_to_look_back,)
        for advancing_rollback in time_to_look_back:
            for event in self.client.get_events(self.wcl_fight,
                                                start_time=timestamp-advancing_rollback,
                                                end_time=timestamp,
                                                filters={"type": [WCLEventTypes.damage, WCLEventTypes.heal], "target.disposition": "friendly"},
                                                actors_obj_dict=self.actors):

                if event.hp_remaining and event.point_x and not isinstance(event.target, int) and event.target_is_friendly:
                    status[event.target] = PlayerStatus(event)
        if cache:
            self._cached_status[timestamp] = status
        return status

    def analyze(self):
        raise NotImplementedError()

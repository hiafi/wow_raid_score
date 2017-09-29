from WoWRaidScore.models import RaidScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes

import math


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

    def distance_calculation(self, coord1, coord2):
        return math.sqrt(math.pow(coord2[0] - coord1[0], 2) + math.pow(coord2[1] - coord1[1], 2))

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
            263,  # Enh Shaman
            269,  # WW monk
            72,  # Arms war
            251,  # Frost DK
            261,  # sub rogue
        }
        ranged_dps_specs = {
            258,  #
            102,  # balance druid
            254,  #
            265,  # affliction lock
            267,  # destruction lock
            64,  # frost mage
            262,  # Ele shaman
        }
        healer_specs = {
            257,  # h priest
            270,  # MW monk
            105,  # r druid
            264  # r shaman
        }
        tank_specs = {
            268,  # BM monk
            104  # druid
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

    def get_wipe_time(self, number_of_deaths=7):
        death_order = self.get_player_death_order()
        death_time = None
        if len(death_order) > 7:
            death_time = self.get_player_death_times().get(death_order[7])
        return death_time

    def analyze(self):
        raise NotImplementedError()

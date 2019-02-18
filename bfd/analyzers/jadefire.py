
from WoWRaidScore.common.analyzer import BossAnalyzer
from WoWRaidScore.models import Player
from bfd.models import JadefireScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class JadefireAnalyzer(BossAnalyzer):
    SCORE_OBJ = JadefireScore
    STOP_AT_DEATH = 6

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.multisided_strike()
        self.beam()
        self.phoenix_strike()
        self.failed_falling()
        self.cleanup()
        self.save_score_objs()

    def multisided_strike(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.id": 284028
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).multisided_strike -= 10
            self.create_score_event(event.timestamp, "was hit by a Multi-Sided Strike",
                                    event.target)

    def beam(self):
        last_hit = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Beam"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if event.timestamp < last_hit.get(event.target, 0) + 2000:
                continue
            last_hit[event.target] = event.timestamp
            self.score_objs.get(event.target).beam -= 10
            self.create_score_event(event.timestamp, "was hit by a by the beam",
                                    event.target)

    def phoenix_strike(self):
        last_hit = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Phoenix Strike"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if not isinstance(event.target, Player):
                continue
            last_hit[event.target] = event.timestamp
            self.score_objs.get(event.target).phoenix_strike -= 1
            self.create_score_event(event.timestamp, "was hit by a by the red swirl during the maze",
                                    event.target)

    def failed_falling(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.id": 3
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if event.damage_done < 200000:
                continue
            self.score_objs.get(event.target).failed_trap_fall -= 30
            self.create_score_event(event.timestamp, "died by falling damage from the flame trap",
                                    event.target)



from WoWRaidScore.common.analyzer import BossAnalyzer
from bfd.models import MekkatorqueScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class MekkatorqueAnalyzer(BossAnalyzer):
    SCORE_OBJ = MekkatorqueScore
    STOP_AT_DEATH = 3

    BUSTER_CANNON_SCORE = 60
    TRAMPLE_SCORE = 30
    SHEEP_SCORE = 20
    GIGAVOLT_SCORE = 30
    RADIATION_SCORE = 20

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.buster_cannon()
        self.trample()
        self.sheep()
        self.radiation()
        self.cleanup()
        self.save_score_objs()

    def buster_cannon(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Buster Cannon"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).buster_cannon -= self.BUSTER_CANNON_SCORE
            self.create_score_event(event.timestamp, "was hit by a Buster Cannon", event.target)

    def trample(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Trample"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.source).trample -= self.TRAMPLE_SCORE
            self.create_score_event(event.timestamp, "trampled {}".format(event.target.safe_name), event.source)

    def sheep(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Sheep Shrapnel"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).sheep -= self.SHEEP_SCORE
            self.create_score_event(event.timestamp, "was hit by a Sheep Shrapnel", event.target)

    def radiation(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Gigavolt Radiation"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).radiation -= self.RADIATION_SCORE
            self.create_score_event(event.timestamp, "was hit by a Buster Cannon", event.target)

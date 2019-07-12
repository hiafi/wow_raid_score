
from WoWRaidScore.common.analyzer import BossAnalyzer
from azshara_palace.models import AzsharaScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class AzsharaAnalyzer(BossAnalyzer):
    SCORE_OBJ = AzsharaScore
    STOP_AT_DEATH = 6

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.sanction()
        self.beckon()
        self.detonation()
        self.drained_soul()
        self.cleanup()
        self.save_score_objs()

    def sanction(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.apply_debuff_stack],
                                                "ability.name": "Sanction"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).sanction -= 5
            self.create_score_event(event.timestamp, "got a stack of Sanction",
                                    event.target)

    def drained_soul(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.apply_debuff_stack],
                                                "ability.name": "Drained Soul"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).drained_soul += 1
            self.create_score_event(event.timestamp, "got a stack of Drained Soul",
                                    event.target)

    def beckon(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Devotion"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).beckon -= 50
            self.create_score_event(event.timestamp, "was hit by a Divine Mallet",
                                    event.target)

        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Crushing Depths"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).beckon -= 50
            self.create_score_event(event.timestamp, "was hit by a Divine Mallet",
                                    event.target)

    def detonation(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Arcane Detonation"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if self.score_objs.get(event.target):
                self.score_objs.get(event.target).detonation -= 80
                self.create_score_event(event.timestamp, "got hit by detonation",
                                        event.target)

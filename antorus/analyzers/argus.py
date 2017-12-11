
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import ArgusScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class ArgusAnalyzer(BossAnalyzer):
    SCORE_OBJ = ArgusScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.cleanup()
        self.death_fog()
        self.scythe_damage()
        self.ember_of_rage()
        self.save_score_objs()

    def bomb_burst_damage(self):
        pass

    def death_fog(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Death Fog"
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).death_fog -= 1

    def scythe_damage(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Deadly Scythe"
                                            }, actors_obj_dict=self.actors):
            score = self.score_objs.get(event.target)
            if not score.tank:
                score.scythe -= 5
                self.create_score_event(event.timestamp, "Was hit by a Deadly Scythe", event.target)

    def cosmic_ray(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Cosmic Ray"
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).cosmic_ray -= 10
            self.create_score_event(event.timestamp, "Was hit by Cosmic Ray", event.target)

    def ember_of_rage(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.apply_debuff_stack],
                                                "ability.name": "Ember of Rage"
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).ember_of_rage -= 10
            self.create_score_event(event.timestamp, "Was hit by an Ember of Rage (blue swirl P4)", event.target)


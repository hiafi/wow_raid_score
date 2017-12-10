
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import EonarScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class EonarAnalyzer(BossAnalyzer):
    SCORE_OBJ = EonarScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.rain_of_fire_splash()
        self.cleanup()
        self.save_score_objs()

    def rain_of_fire_splash(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Surging Fel"
                                            }, actors_obj_dict=self.actors):
            pass

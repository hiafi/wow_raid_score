
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import VarimathrasScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class VarimathrasAnalyzer(BossAnalyzer):
    SCORE_OBJ = VarimathrasScore
    STOP_AT_DEATH = 3

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.shadow_fissure()
        self.cleanup()
        self.save_score_objs()

    def shadow_fissure(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Shadow Fissure"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event.timestamp, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).shadow_fissure -= 10
            self.create_score_event(event.timestamp, "took a tick of Shadow Fissure", event.target)
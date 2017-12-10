
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import KingarothScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class KingarothAnalyzer(BossAnalyzer):
    SCORE_OBJ = KingarothScore
    STOP_AT_DEATH = 3

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.ruiner()
        self.cleanup()
        self.save_score_objs()

    def ruiner(self):
        time_last_hit = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Ruiner"
                                            }, actors_obj_dict=self.actors):
            if time_last_hit[event.target] + 10000 < event.timestamp:
                self.score_objs.get(event.target).ruiner -= 25
                self.create_score_event(event.timestamp, "Was hit by Ruiner (laser)", event.target)
            else:
                time_last_hit[event.target] = event.timestamp

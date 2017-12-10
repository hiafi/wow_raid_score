
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import ImonarScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class ImonarAnalyzer(BossAnalyzer):
    SCORE_OBJ = ImonarScore
    STOP_AT_DEATH = 7

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.pulse_mines()
        self.shrapnel_mines()
        self.cleanup()
        self.save_score_objs()

    def pulse_mines(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Pulse Grenade"
                                            }, actors_obj_dict=self.actors):
            pass

    def shrapnel_mines(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Shrapnel Blast"
                                            }, actors_obj_dict=self.actors):
            pass

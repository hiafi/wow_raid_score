
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import HarjatanScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict

class HarjatanAnalyzer(BossAnalyzer):
    SCORE_OBJ = HarjatanScore

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.soaking_slams()
        self.debuff_stacks()
        self.cleanup()
        self.save_score_objs()

    def soaking_slams(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 231854
                                            }, actors_obj_dict=self.actors):
            score_obj = self.score_objs.get(event.target)
            score_obj.soaking_slams += 10

    def debuff_stacks(self):
        stacks_over_5 = defaultdict(int)
        stacks_over_10 = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff_stack],
                                                "ability.name": "Drenched"
                                            }, actors_obj_dict=self.actors):
            if event.stack >= 10:
                stacks_over_10[event.target] += 1
            elif event.stack >= 5:
                stacks_over_5[event.target] += 1

        for actor, under_10 in stacks_over_5.items():
            self.score_objs.get(actor).stacks_of_debuff -= int(0.25 * under_10)
        for actor, over_10 in stacks_over_10.items():
            self.score_objs.get(actor).stacks_of_debuff -= int(0.5 * over_10)

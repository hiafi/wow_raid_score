
from WoWRaidScore.common.analyzer import BossAnalyzer
from azshara_palace.models import CommanderScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class CommanderAnalyzer(BossAnalyzer):
    SCORE_OBJ = CommanderScore
    STOP_AT_DEATH = 6

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.bolts()
        self.cleanup()
        self.save_score_objs()

    def bolts(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": ["Overwhelming Frost", "Overwhelming Toxin"]
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.target)
            if score_obj.tank:
                continue
            score_obj.bolts -= 20
            self.create_score_event(event.timestamp, "got a stack of Bolt",
                                    event.target, 20)

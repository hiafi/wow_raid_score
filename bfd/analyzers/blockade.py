
from WoWRaidScore.common.analyzer import BossAnalyzer
from bfd.models import BlockadeScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class BlockadeAnalyzer(BossAnalyzer):
    SCORE_OBJ = BlockadeScore
    STOP_AT_DEATH = 2

    SEASWELL = 200
    IRE = 100

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.seaswell()
        self.ire_of_the_deep()
        self.cleanup()
        self.save_score_objs()

    def seaswell(self):
        last_seen = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.id": 290693
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if last_seen.get(event.target, 0) + 100 > event.timestamp:
                continue

            self.score_objs.get(event.target).sea_swell -= self.SEASWELL
            self.create_score_event(event.timestamp, "was hit by a Seaswell",
                                    event.target)

            last_seen[event.target] = event.timestamp

    def ire_of_the_deep(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.id": 285040,
                                                "ability.amount": (">", 2000000)
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.target)
            if score_obj.tank:
                continue
            score_obj.ire_of_the_deep -= self.IRE
            self.create_score_event(event.timestamp, "was hit by a Ire of the Deep (unmitigated)",
                                    event.target)

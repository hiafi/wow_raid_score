
from WoWRaidScore.common.analyzer import BossAnalyzer
from WoWRaidScore.models import Player
from bfd.models import RhastakhanScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class RhastakhanAnalyzer(BossAnalyzer):
    SCORE_OBJ = RhastakhanScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.plague_of_fire()
        self.toads()
        self.deathly_withering()
        self.seal_of_purification()
        self.cleanup()
        self.save_score_objs()

    def plague_of_fire(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Plague of Fire"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if isinstance(event.source, Player):
                self.score_objs.get(event.source).plague_of_fire -= 15
                self.create_score_event(event.timestamp, "spread plague of fire to {}".format(event.target.safe_name),
                                        event.source)

    def toads(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Toad Toxin"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).toads -= 10
            self.create_score_event(event.timestamp, "hit by a Toad",
                                    event.target)

    def deathly_withering(self):
        pass

    def seal_of_purification(self):
        pass

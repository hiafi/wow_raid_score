
from WoWRaidScore.common.analyzer import BossAnalyzer
from bfd.models import OpulenceScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class OpulenceAnalyzer(BossAnalyzer):
    SCORE_OBJ = OpulenceScore
    STOP_AT_DEATH = 3

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.flames_of_punishment()
        self.volatile_charge()
        self.crush()
        self.cleanup()
        self.save_score_objs()

    def flames_of_punishment(self):
        last_hit = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Flames of Punishment"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if event.tick:
                continue
            if event.damage_done <= 10000:
                continue
            if event.timestamp < last_hit.get(event.target, -2000) + 2000:
                continue
            last_hit[event.target] = event.timestamp
            self.score_objs.get(event.target).flames_of_punishment -= 20
            self.create_score_event(event.timestamp, "was hit by a Flames of Punishment",
                                    event.target)

    def volatile_charge(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.id": 283557
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if isinstance(event.target, int):
                continue
            self.score_objs.get(event.source).volatile_charge -= 15
            self.create_score_event(event.timestamp, "hit {} by a Volatile Charge".format(event.target.safe_name),
                                    event.source)

    def crush(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Crush"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).crush -= 10
            self.create_score_event(event.timestamp, "was hit by Crush!",
                                    event.target)

    def molten_gold(self):
        pass

    def deadly_hex(self):
        pass

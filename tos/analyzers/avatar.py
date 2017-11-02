
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import AvatarScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class AvatarAnalyzer(BossAnalyzer):
    SCORE_OBJ = AvatarScore
    STOP_AT_DEATH = 3

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.unbound_chaos()
        if self.wcl_fight.difficulty < self.MYTHIC_DIFFICULTY:
            self.tornado_damage()
            self.soaking_touches()
        self.soaking_dark_marks()
        self.soaking_p2_meteors()
        self.shadow_blades()
        self.cleanup()
        self.save_score_objs()

    def tornado_damage(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.apply_debuff_stack],
                                                "ability.name": "Black Winds"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).tornados -= 10
            self.create_score_event(event.timestamp, "{} was hit by a tornado".format(event.target.safe_name), event.target)

    def unbound_chaos(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Unbound Chaos"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.source)
            if score_obj.tank:
                score_obj.unbound_chaos -= 4
            elif event.source != event.target:
                score_obj.unbound_chaos -= 1
            else:
                score_obj.unbound_chaos -= 2
            self.create_score_event(event.timestamp, "{} hit {} with unbound chaos".format(event.source.safe_name, event.target.safe_name), event.source)

    def soaking_touches(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Touch of Sargeras"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.target)
            val = 5
            if score_obj.tank:
                val = 10

            score_obj.touch_of_sargeras_soak += val

    def soaking_dark_marks(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Dark Mark"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.target)
            val = 5
            if score_obj.tank:
                val = 10
            score_obj.dark_marks += val

    def soaking_p2_meteors(self):
        pass

    def shadow_blades(self):
        pass

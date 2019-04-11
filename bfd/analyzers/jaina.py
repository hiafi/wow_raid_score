
from WoWRaidScore.common.analyzer import BossAnalyzer
from bfd.models import JainaScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class JainaAnalyzer(BossAnalyzer):
    SCORE_OBJ = JainaScore
    STOP_AT_DEATH = 3

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.avalanche()
        self.stand_in_fire()
        self.ice_block()
        self.bombard()
        self.cleanup()
        self.save_score_objs()

    def stand_in_fire(self):
        last_hit = {}
        times_hit = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Searing Pitch"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return

            if last_hit.get(event.target, 0) >= event.timestamp - 1200:
                times_hit[event.target] += 1
                if times_hit[event.target] >= 2:
                    points = 2 ** times_hit[event.target]
                    self.score_objs.get(event.target).standing_in_fire -= points
                    self.create_score_event(event.timestamp, "stood in fire (tick {})".format(times_hit[event.target]),
                                            event.target, points)
            else:
                times_hit[event.target] = 1
            last_hit[event.target] = event.timestamp

    def avalanche(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Avalanche"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.target)
            if score_obj.tank:
                continue
            score_obj.avalanche -= 10
            self.create_score_event(event.timestamp, "stood in fire",
                                    event.target)

    def ice_block(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Frozen Solid"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).ice_blocked -= 10
            self.create_score_event(event.timestamp, "got iceblocked",
                                    event.target)

    def bombard(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Bombard"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).bombards -= 10
            self.create_score_event(event.timestamp, "got hit by bombard",
                                    event.target)


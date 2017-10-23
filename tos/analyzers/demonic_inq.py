
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import DIScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict

class DIAnalyzer(BossAnalyzer):
    SCORE_OBJ = DIScore

    def analyze(self):
        print("Processing {}".format(self.wcl_fight))
        self.times_in_jail()
        self.interrupts()
        if self.wcl_fight.difficulty >= self.MYTHIC_DIFFICULTY:
            self.grouping_jail()
            self.explosive_anguish()
        self.cleanup()
        self.save_score_objs()

    def times_in_jail(self):
        times_in_jail_dict = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.apply_debuff,
                                                "ability.id": 236283
                                            }, actors_obj_dict=self.actors):

            times_in_jail_dict[event.target] += 1

        for player, times_in in times_in_jail_dict.items():
            score_obj = self.score_objs.get(player)
            if score_obj.tank or times_in <= 1:
                continue

            elif score_obj.healer:
                score_obj.times_in_jail -= (times_in - 1) * 1
            else:
                score_obj.times_in_jail -= (times_in - 1) * 2

    def explosive_anguish(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Explosive Anguish"
                                            }, actors_obj_dict=self.actors):
            score_obj = self.score_objs.get(event.target)
            if not score_obj:
                continue
            if score_obj.tank:
                continue
            if score_obj.melee_dps:
                score_obj.explosive_anguish -= 2
            else:
                score_obj.explosive_anguish -= 5

    def grouping_jail(self):
        self._group_jail(WCLEventTypes.remove_debuff, 1000)
        self._group_jail(WCLEventTypes.apply_debuff, 3000, bad_score=1, number_needed=2)

    def _group_jail(self, event_type, time_thresh, bad_score=5, good_score=1, number_needed=3):
        last_timestamp = 0
        people_leaving_jail = []
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": event_type,
                                                "ability.id": 236283
                                            }, actors_obj_dict=self.actors):
            if self.score_objs.get(event.target).tank and event_type == WCLEventTypes.apply_debuff:
                continue
            if event.timestamp > last_timestamp + time_thresh:
                for person in people_leaving_jail:
                    score_obj = self.score_objs.get(person)
                    if len(people_leaving_jail) < number_needed:
                        score_obj.grouping_jail -= bad_score
                    else:
                        score_obj.grouping_jail += good_score

                people_leaving_jail = []
            people_leaving_jail.append(event.target)
            last_timestamp = event.timestamp

    def interrupts(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.interrupt],
                                                "target.name": "Belac"
                                            }, actors_obj_dict=self.actors):
            score_obj = self.score_objs.get(event.source)
            if score_obj:
                score_obj.interrupts += 1 if score_obj.melee_dps else 2


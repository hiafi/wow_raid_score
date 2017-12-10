
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import CovenScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class CovenAnalyzer(BossAnalyzer):
    SCORE_OBJ = CovenScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.storm_damage()
        self.whirlwind()
        self.shadowblades()
        self.norgannon()
        self.khazgoroth()
        self.golganoth()
        self.cleanup()
        self.save_score_objs()

    def storm_damage(self):
        time_last_hit = defaultdict(int)
        times_hit = defaultdict(int)
        times_needed = 2
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Storm of Darkness"
                                            }, actors_obj_dict=self.actors):
            if time_last_hit[event.target]+20000 < event.timestamp:
                time_last_hit[event.target] = event.timestamp
                times_hit[event.target] = 1
                if times_hit[event.target] > times_needed:
                    self.score_objs.get(event.target).storm_damage -= (times_hit[event.target] - times_needed) * 5
            else:
                times_hit[event.target] += 1
            if times_hit[event.target] > times_needed:
                self.create_score_event(event.timestamp, "Was hit by Storm of Darkness", event.target)

        for target, hit in times_hit.items():
            if hit > times_needed:
                self.score_objs.get(target).storm_damage -= (hit - times_needed) * 5

    def whirlwind(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 245629
                                            }, actors_obj_dict=self.actors):
            score = self.score_objs.get(event.target)
            if score:
                score.whirlwind -= 3
                self.create_score_event(event.timestamp, "Was hit by the whirlwind landing", event.target)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 245634
                                            }, actors_obj_dict=self.actors):
            score = self.score_objs.get(event.target)
            if score:
                score.whirlwind -= 3
                self.create_score_event(event.timestamp, "Was hit by the whirlwind spinning through them", event.target)

    def shadowblades(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Shadow Blades"
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).shadowblades -= 5
            self.create_score_event(event.timestamp, "Was hit by shadowblades", event.target)

    def norgannon(self):
        time_last_hit = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 245921
                                            }, actors_obj_dict=self.actors):
            if time_last_hit[event.target] + 35000 < event.timestamp:
                self.score_objs.get(event.target).norgannon -= 30
                self.create_score_event(event.timestamp, "Was hit by Spectral Army of Norgannon (walking dudes)", event.target)
            else:
                time_last_hit[event.target] = event.timestamp

    def khazgoroth(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 245674
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).khazgoroth -= 10
            self.create_score_event(event.timestamp, "Was hit by Flames of Khaz'goroth (flamethrower)",
                                    event.target)

    def golganoth(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Fury of Golganneth"
                                            }, actors_obj_dict=self.actors):
            score = self.score_objs.get(event.target)
            if not score.tank:
                self.score_objs.get(event.target).golganoth -= 5
                self.create_score_event(event.timestamp, "Was hit by Fury of Golganneth (chain lightning)", event.target)

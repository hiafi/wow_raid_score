
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import WorldbreakerScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class WorldbreakerAnalyzer(BossAnalyzer):
    SCORE_OBJ = WorldbreakerScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        if self.wcl_fight.difficulty >= self.MYTHIC_DIFFICULTY:
            self.annihilation_soaks_mythic()
        else:
            self.annihilation_soaks()
        self.hit_from_laser()
        self.decimation()
        self.cleanup()
        self.save_score_objs()

    def annihilation_soaks(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 244761
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).annihilation_soaks += 1

    def annihilation_soaks_mythic(self):
        annihilation_casts = []
        last_shrap_cast = 0
        last_soak_time = defaultdict(int)
        num_soaks = defaultdict(int)
        deaths = self.get_player_death_times()
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.cast,
                                                "ability.id": [244294, 247044]
                                            }, actors_obj_dict=self.actors):
            if event.name == "Annihilation":
                annihilation_casts.append(event.timestamp)
            else:
                if event.timestamp > last_shrap_cast + 2000:
                    annihilation_casts.append(event.timestamp)
                    last_shrap_cast = event.timestamp

        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": [244761, 246971, 247044]
                                            }, actors_obj_dict=self.actors):
            num_soaks[event.target] += 1
            score_obj = self.score_objs.get(event.target)
            if not score_obj.tank:
                self.create_score_event(event.timestamp, "soaked an Annihilation circle!", event.target)
        for person, num_soaked in num_soaks.items():
            score_obj = self.score_objs.get(person)
            if score_obj.tank:
                continue
            expected = 0
            for ts in annihilation_casts:
                if ts < deaths.get(person, annihilation_casts[-1] + 1000):
                    expected += 1
            if num_soaked < expected:
                score = -8 * (expected - num_soaked)
                self.create_score_event(event.timestamp, "missed {} soaks total".format(expected), event.target)
            else:
                score = 2 * (num_soaked - expected)
            score_obj.annihilation_soaks = score

    def hit_from_laser(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Surging Fel"
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).hit_from_laser -= 15
            self.create_score_event(event.timestamp, "Was hit by the laser", event.target)

    def decimation(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Decimation",
                                                "effectiveDamage": (">", 1000000)
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).decimation -= 15
            self.create_score_event(event.timestamp, "Was hit by decimation", event.target)

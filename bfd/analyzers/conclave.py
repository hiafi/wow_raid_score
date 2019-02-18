
from WoWRaidScore.common.analyzer import BossAnalyzer
from bfd.models import ConclaveScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class ConclaveAnalyzer(BossAnalyzer):
    SCORE_OBJ = ConclaveScore
    STOP_AT_DEATH = 3

    paku_wrath_threshold = {
        BossAnalyzer.MYTHIC_DIFFICULTY: 70000
    }

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.lacerating_claws()
        self.kimbul_wrath()
        self.kragwa_wrath()
        self.static_orb()
        self.paku_wrath()
        self.cleanup()
        self.save_score_objs()

    def lacerating_claws(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Lacerating Claws"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.target)
            if score_obj.tank:
                continue
            if event.tick:
                continue
            score_obj.lacerating_claws -= 10
            self.create_score_event(event.timestamp, "was hit by a Lacerating Claws",
                                    event.target)

    def kimbul_wrath(self):
        targeted_players = []
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.remove_debuff],
                                                "ability.id": 282834
                                            }, actors_obj_dict=self.actors):
            targeted_players.append(event.target)

        last_timestamp = 0
        leap_count = -1
        current_target = None
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.id": 282447
                                            }, actors_obj_dict=self.actors):

            if event.timestamp > last_timestamp + 500:
                last_timestamp = event.timestamp
                current_target = event.target
                leap_count += 1
            if current_target != event.target:
                leap_target = targeted_players[leap_count]
                self.score_objs.get(leap_target).kimbul_wrath -= 25
                self.create_score_event(event.timestamp, "hit {} with Kimbul's Wrath".format(event.target.safe_name),
                                        leap_target)

    def kragwa_wrath(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.id": 282636
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).kragwa_wrath -= 10
            self.create_score_event(event.timestamp, "was hit by Krag'wa's Wrath!",
                                    event.target)

    def static_orb(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Static Orb"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).static_orb -= 10
            self.create_score_event(event.timestamp, "was hit by a static orb",
                                    event.target)

    def paku_wrath(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.id": 282109,
                                                "rawDamage": (">", self.paku_wrath_threshold.get(self.wcl_fight.difficulty)),
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.target)
            if score_obj.tank:
                continue
            score_obj.paku_wrath -= 5
            self.create_score_event(event.timestamp, "was not in Pa'ku's circle during Pa'ku's Wrath",
                                    event.target)

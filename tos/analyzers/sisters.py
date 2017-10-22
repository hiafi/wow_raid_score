
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import SistersScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class SistersAnalyzer(BossAnalyzer):
    SCORE_OBJ = SistersScore
    CENTER_OF_ROOM = (102000, 619000)

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.glaive_storm()
        self.lunar_beacon()
        self.twilight_glaive()
        if self.wcl_fight.difficulty >= self.MYTHIC_DIFFICULTY:
            self.astral_vuln()
        self.cleanup()
        self.save_score_objs()

    def glaive_storm(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 236480
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).glaive_storm -= 5

    def lunar_beacon(self):
        start_timestamp = None
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.remove_debuff, WCLEventTypes.apply_debuff],
                                                "ability.name": "Lunar Beacon"
                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_debuff:
                start_timestamp = event.timestamp
            if event.type == WCLEventTypes.remove_debuff:
                if start_timestamp and event.timestamp - start_timestamp < 5500:
                    start_timestamp = None
                    continue
                status_at_start = self.get_player_status_at_time(event.target, event.timestamp)
                status_at_end = self.get_player_status_at_time(event.target, event.timestamp+3500)

                if status_at_start and status_at_end:
                    score_val = 0
                    distance = self.distance_calculation(status_at_start.location, status_at_end.location)
                    distance_from_center = self.distance_calculation(status_at_start.location, self.CENTER_OF_ROOM)
                    if distance_from_center > 2000 and distance < 50:
                        score_val = 2
                    elif distance_from_center > 2000 and distance < 500:
                        score_val = 1
                    elif distance_from_center > 1500 and distance < 800:
                        score_val = 0
                    elif distance_from_center < 1500 or distance > 1500:
                        score_val = -15

                    self.score_objs.get(event.target).lunar_beacon += score_val
                else:
                    print(event.target, "Unable to get status", status_at_start, status_at_end)
                start_timestamp = None

    def twilight_glaive(self):
        cast_target = None
        people_hit_by_glaive = defaultdict(int)
        player_names_hit_by_glaive = defaultdict(list)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.cast, WCLEventTypes.damage],
                                                "ability.name": "Twilight Glaive"
                                            }, actors_obj_dict=self.actors):
            if event.target is None:
                continue
            if event.type == WCLEventTypes.cast:
                cast_target = event.target
            else:
                if cast_target is None or cast_target == event.target:
                    continue
                people_hit_by_glaive[cast_target] += 1
                player_names_hit_by_glaive[cast_target].append(event.target)
        for person, num_hit in people_hit_by_glaive.items():
            self.score_objs.get(person).twilight_glaive -= num_hit * 5

    def astral_vuln(self):
        last_stack_time = 0
        stack_count = 0
        DEBUFF_DURATION = 2000
        triggered_per_cycle = defaultdict(int)
        triggered_above_six = defaultdict(int)
        last_person = None
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Astral Purge"
                                            }, actors_obj_dict=self.actors):
            if event.source == last_person:
                continue
            if event.timestamp > last_stack_time + DEBUFF_DURATION:
                self.calc_astral_for_cycle(stack_count, triggered_per_cycle, triggered_above_six)
                stack_count = 0
                triggered_per_cycle = defaultdict(int)
                triggered_above_six = defaultdict(int)
            stack_count += 1
            last_stack_time = event.timestamp
            triggered_per_cycle[event.source] += 1
            if stack_count > 6:
                triggered_above_six[event.source] += 1
            last_person = event.source

    def calc_astral_for_cycle(self, stack_count, triggered_per_cycle, triggered_above_six):
        for player, count, in triggered_per_cycle.items():
            val = 0
            if count >= 2 and stack_count > 8:
                val = 5
            if count >= 2:
                val = 2
            elif player in triggered_above_six:
                val = triggered_above_six.get(player)
            self.score_objs.get(player).astral_vuln -= val * count

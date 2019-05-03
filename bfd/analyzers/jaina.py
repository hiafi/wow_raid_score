
from WoWRaidScore.common.analyzer import BossAnalyzer
from bfd.models import JainaScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class JainaAnalyzer(BossAnalyzer):
    SCORE_OBJ = JainaScore
    STOP_AT_DEATH = 4

    AVALANCHE_SCORE = 20
    ICEBLOCK_SCORE = 30
    BOMBARD_SCORE = 25
    FREEZING_BLAST = 20
    GLACIAL_RAY = 30
    HEART_OF_FROST = 40

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.ice_block_times = self.get_debuff_start_and_end("Frozen Solid")
        self.ice_block()
        self.avalanche()
        self.stand_in_fire()
        self.bombard()
        self.glacial_ray()
        self.freezing_blast()
        self.heart_of_frost()
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
                    points = min(2 ** (times_hit[event.target]), 50)
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
            if self.between_multiple_durations(event.timestamp, self.ice_block_times.get(event.target, [])):
                continue
            score_obj.avalanche -= self.AVALANCHE_SCORE
            self.create_score_event(event.timestamp, "stood in fire",
                                    event.target, self.AVALANCHE_SCORE)

    def ice_block(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Frozen Solid"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).ice_blocked -= self.ICEBLOCK_SCORE
            self.create_score_event(event.timestamp, "got iceblocked",
                                    event.target, self.ICEBLOCK_SCORE)

    def bombard(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Bombard"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if self.between_multiple_durations(event.timestamp, self.ice_block_times.get(event.target, [])):
                continue
            self.score_objs.get(event.target).bombards -= self.BOMBARD_SCORE
            self.create_score_event(event.timestamp, "got hit by bombard",
                                    event.target, self.BOMBARD_SCORE)

    def freezing_blast(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Freezing Blast"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).freezing_blast -= self.FREEZING_BLAST
            self.create_score_event(event.timestamp, "got hit by freezing blast",
                                    event.target, self.FREEZING_BLAST)

    def glacial_ray(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Glacial Ray"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if self.between_multiple_durations(event.timestamp, self.ice_block_times.get(event.target, [])):
                continue
            self.score_objs.get(event.target).glacial_ray -= self.GLACIAL_RAY
            self.create_score_event(event.timestamp, "got hit by glacial ray",
                                    event.target, self.GLACIAL_RAY)

    def heart_of_frost(self):
        heart_of_frost_timings = defaultdict(list)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Heart of Frost"
                                            }, actors_obj_dict=self.actors):
            heart_of_frost_timings[event.target].append((event.timestamp, event.timestamp+12000))
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Heart of Frost"
                                            }, actors_obj_dict=self.actors):
            for caster, timestamps in heart_of_frost_timings.items():
                if self.between_multiple_durations(event.timestamp, timestamps):

                    s1 = self.get_player_status_at_time(caster, event.timestamp, cache=True)
                    s2 = self.get_player_status_at_time(event.target, event.timestamp, cache=True)
                    if s1 and s2:
                        dist = self.distance_calculation(s1.location, s2.location)
                        if dist < 0.05:
                            self.score_objs.get(caster).heart_of_frost -= self.HEART_OF_FROST
                            self.create_score_event(event.timestamp,
                                                    "hit {} with heart of frost".format(event.target.safe_name),
                                                    caster, self.HEART_OF_FROST)





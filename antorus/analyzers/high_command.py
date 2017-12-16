
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import HighCommandScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class MineLocation(object):
    def __init__(self, event):
        self.timestamp = event.timestamp
        self.location = event.location

    def __str__(self):
        return "<Mine {}>".format(self.location)


class HighCommandAnalyzer(BossAnalyzer):
    SCORE_OBJ = HighCommandScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.step_on_mine()
        self.bladestorm()
        self.cleanup()
        self.save_score_objs()

    def get_stun_times(self):
        stun_times = defaultdict(list)
        last_stun = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.remove_debuff],
                                                "ability.name": "Shocked",
                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.remove_debuff:
                if last_stun.get(event.target) is not None:
                    stun_times[event.target].append((last_stun.get(event.target), event.timestamp))
                    last_stun[event.target] = None
            else:
                last_stun[event.target] = event.timestamp
        for target, start_stun in last_stun.items():
            if start_stun is not None:
                stun_times[target].append((start_stun, self.wcl_fight.end_time_str))

        return stun_times

    def bladestorm(self):
        last_hit = defaultdict(int)
        times_hit = defaultdict(int)
        stun_times = self.get_stun_times()
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 253039,
                                            }, actors_obj_dict=self.actors):
            if self.between_multiple_durations(event.timestamp, stun_times.get(event.target, [])):
                continue
            if last_hit[event.target] + 5000 < event.timestamp:
                if times_hit[event.target] > 3:
                    score_obj = self.score_objs.get(event.target)
                    if score_obj is not None and not score_obj.tank:
                        score_obj.bladestorm -= sum([i for i in range(times_hit[event.target]-1)])
                        self.create_score_event(event.timestamp,
                                                "was hit by {} bladestorm ticks".format(times_hit[event.target]),
                                                event.target)
                times_hit[event.target] = 1
                last_hit[event.target] = event.timestamp

            else:
                times_hit[event.target] += 1
        for target, times_hit_count in times_hit.items():
            if times_hit_count > 3:
                score_obj = self.score_objs.get(target)
                if score_obj is not None and not score_obj.tank:
                    score_obj.bladestorm -= sum([i for i in range(times_hit_count-1)])
                    self.create_score_event(last_hit[target],
                                            "was hit by {} bladestorm ticks".format(times_hit_count),
                                            target)

    def get_mine_locations(self):
        mine_locations = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.cast,
                                                "source.name": "Entropic Mine"
                                            }, actors_obj_dict=self.actors):
            mine_locations[event.source_instance] = MineLocation(event)
        return mine_locations

    def get_mine_stack_count(self, event):
        last_seen_stack = 0
        last_seen_time = 0
        for event in self.client.get_events(self.wcl_fight,
                                            start_time=event.timestamp - 4000,
                                            end_time=event.timestamp + 500,
                                            filters={
                                                "target.name": event.target.name,
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.apply_debuff_stack],

                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_debuff_stack:
                last_seen_stack = event.stack
            else:
                last_seen_stack = 1
            last_seen_time = event.timestamp
        return last_seen_stack, last_seen_time

    def step_on_mine(self):
        mine_locations = self.get_mine_locations()
        current_stack_count = 0
        current_stack_time = 0
        people_hit_by_the_mine = defaultdict(int)
        potential_person_hit = defaultdict(list)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": 245121
                                            }, actors_obj_dict=self.actors):
            triggered_mine = mine_locations.get(event.source_instance)
            try:
                distance_to_mine = self.distance_calculation(event.location, triggered_mine.location)
            except TypeError:
                distance_to_mine = None
            actual_timestamp = event.timestamp
            for ts in people_hit_by_the_mine.keys():
                if abs(event.timestamp - ts) < 100:
                    actual_timestamp = ts
            event.timestamp = actual_timestamp
            people_hit_by_the_mine[event.timestamp] += 1

            if distance_to_mine is not None and distance_to_mine <= 0.025:
                potential_person_hit[event.timestamp].append(event)

        for timestamp, events in potential_person_hit.items():
            for event in events:
                if current_stack_time + 5000 <= event.timestamp:
                    current_stack_count, current_stack_time = self.get_mine_stack_count(event)
                if current_stack_count < 2 and people_hit_by_the_mine[timestamp] <= 2:
                    continue
                self.create_score_event(event.timestamp, "stepped on a mine", event.target)
                self.score_objs.get(event.target).step_on_mines -= 5


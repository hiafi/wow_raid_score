
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import KiljaedenScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class KiljaedenAnalyzer(BossAnalyzer):
    SCORE_OBJ = KiljaedenScore

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.soaking_rain()
        self.soaking_lasers()
        self.dodge_obelisks()
        self.dreadburst()
        self.cleanup()
        self.save_score_objs()

    def soaking_rain(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Armageddon Rain"
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).soaking_rain += 10

    def soaking_lasers(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Focused Dreadflame"
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).soaking_lasers += 5

    def dodge_obelisks(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Demonic Obelisk"
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).obelisks -= 10

    def dreadburst(self):
        people_targeted = defaultdict(list)
        people_affected = defaultdict(list)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.cast,
                                                "ability.name": "Bursting Dreadflame",
                                            }, actors_obj_dict=self.actors):
            if event.target:
                people_targeted[event.timestamp].append(event.target)

        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Bursting Dreadflame"
                                            }, actors_obj_dict=self.actors):
            found_event = False
            for attempted_timestamp, list_to_append in people_affected.items():
                if self.between_duration(attempted_timestamp - 100, event.timestamp - 5000, attempted_timestamp + 100):
                    list_to_append.append(event)
                    found_event = True
            if not found_event:
                closest_timestamp = event.timestamp - 5000
                for maybe_timestamp in people_targeted.keys():
                    if self.between_duration(maybe_timestamp-100, event.timestamp-5000, maybe_timestamp+100):
                        closest_timestamp = maybe_timestamp
                people_affected[closest_timestamp].append(event)
        for timestamp, targeted in people_targeted.items():
            locations = {event.target: event.location for event in people_affected.get(timestamp, [])}
            for event_to_check in people_affected.get(timestamp, []):
                if event_to_check.target not in targeted:
                    for targeted_person in targeted:
                        distance = self.distance_calculation(locations.get(event_to_check.target), locations.get(targeted_person))
                        if distance < 1200:
                            self.score_objs.get(targeted_person).bursting_dreadflame -= 2


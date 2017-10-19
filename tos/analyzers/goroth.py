
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import GorothScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes


class GorothAnalyzer(BossAnalyzer):
    SCORE_OBJ = GorothScore

    def analyze(self):
        print("Processing {}".format(self.wcl_fight))

        if self.wcl_fight.difficulty >= self.MYTHIC_DIFFICULTY:
            self.debug_message("Infernal Soaking")
            self.not_soaking_infernals()
        self.debug_message("Splashing Meteors")
        self.splashing_others_with_meteor()
        self.debug_message("Hiding")
        self.not_hiding()
        self.cleanup()
        self.save_score_objs()

    def not_soaking_infernals(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "source.name": "Goroth",
                                                "ability.name": "Rain of Brimstone"
                                            }, actors_obj_dict=self.actors):
            score_obj = self.score_objs.get(event.target)
            score_obj.soaking_infernals += 20

    def splashing_others_with_meteor(self):
        recent_debuff = 0
        marked_targets = set()
        locations = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.remove_debuff, WCLEventTypes.apply_debuff],
                                                "ability.id": [232249, 230345],
                                            }, actors_obj_dict=self.actors):

            if event.type == WCLEventTypes.remove_debuff and event.id == 232249:
                if event.timestamp > recent_debuff + 5000:
                    recent_debuff = event.timestamp
                    marked_targets = set()
                    locations = {}
                marked_targets.add(event.target)
            elif event.type == WCLEventTypes.apply_debuff and event.id == 230345:
                if event.target in marked_targets:
                    continue
                target_location = self.get_player_status_at_time(event.target, event.timestamp+2000, time_to_look_back=3000)
                if target_location is None:
                    continue
                for marked_target in marked_targets:
                    if marked_target not in locations:
                        status = self.get_player_status_at_time(marked_target, event.timestamp+2000, time_to_look_back=3000)
                        if status:
                            locations[marked_target] = status
                    distance = self.distance_calculation(target_location.location, locations[marked_target].location)

                    if distance < 1000:
                        score_obj = self.score_objs.get(marked_target)
                        score_obj.splashing_from_meteors -= 10

    def not_hiding(self):
        already_counted = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "source.name": "Goroth",
                                                "ability.name": "Infernal Burning"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event):
                return
            if event.target in already_counted:
                if event.timestamp < already_counted.get(event.target) + 15000:
                    continue
            score_obj = self.score_objs.get(event.target)
            val = 50
            if score_obj.tank:
                val = 20
            score_obj.not_hiding -= val
            already_counted[event.target] = event.timestamp
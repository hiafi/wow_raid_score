
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import GorothScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes


class GorothAnalyzer(BossAnalyzer):
    SCORE_OBJ = GorothScore

    def analyze(self):
        if self.wcl_fight.difficulty >= self.MYTHIC_DIFFICULTY:
            self.not_soaking_infernals()
        self.splashing_others_with_meteor()
        self.not_hiding()
        self.cleanup()
        # self.save_score_objs()

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
        marked_locations = {}
        to_process = set()
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.remove_debuff, WCLEventTypes.damage],
                                                "ability.id": ["232249", "230345"],
                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.remove_debuff and event.id == 230345:
                continue
            if event.type == WCLEventTypes.remove_debuff:
                marked_locations, marked_targets, to_process = self.meteor_splash_rock_falling(event, marked_locations,
                                                                                               marked_targets,
                                                                                               recent_debuff,
                                                                                               to_process)
                marked_targets.add(event.target)
                recent_debuff = event.timestamp
            elif not event.tick:
                if event.point_x is None or event.point_y is None:
                    continue
                if event.target in marked_targets:
                    marked_locations[event.target] = (event.point_x, event.point_y)
                self.meteor_splash_hit_by_rock(event, marked_locations, marked_targets, to_process)

    def meteor_splash_hit_by_rock(self, event, marked_locations, marked_targets, to_process):
        if event.target not in marked_targets:
            event_coords = (event.point_x, event.point_y)

            found_responsible = False
            for player, coords in marked_locations.items():
                if event.target == player:
                    continue
                distance = self.distance_calculation(event_coords, coords)
                if distance < 1000.0:
                    score_obj = self.score_objs.get(player)
                    score_obj.splashing_from_meteors -= 10
                    found_responsible = True
            if not found_responsible:
                to_process.add((event.target, event_coords))

    def meteor_splash_rock_falling(self, event, marked_locations, marked_targets, recent_debuff, to_process):
        if recent_debuff < event.timestamp - 5000:
            if to_process:
                for player, player_coords in to_process:
                    for marked_player, marked_coord in marked_locations.items():
                        distance = self.distance_calculation(player_coords, marked_coord)
                        if distance < 1000.0:
                            score_obj = self.score_objs.get(marked_player)
                            score_obj.splashing_from_meteors -= 10

            marked_targets = set()
            marked_locations = {}
            to_process = set()

        return marked_locations, marked_targets, to_process

    def not_hiding(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "source.name": "Goroth",
                                                "ability.name": "Infernal Burning"
                                            }, actors_obj_dict=self.actors):
            score_obj = self.score_objs.get(event.target)
            val = 50
            if score_obj.tank:
                val = 20
            score_obj.not_hiding -= val
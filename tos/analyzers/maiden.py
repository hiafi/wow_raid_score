
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import MaidenScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class MaidenAnalyzer(BossAnalyzer):
    SCORE_OBJ = MaidenScore

    def analyze(self):
        # self.wrong_color()
        self.wrong_orb()
        # self.blow_up_early()
        # self.cleanup()
        # self.save_score_objs()

    def try_remove_from_dict(self, dic, key):
        try:
            del dic[key]
        except KeyError:
            pass

    def wrong_color(self):
        colors = {}
        positions = {}
        already_counted = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters=[{
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Unstable Soul"
                                            }, {
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": ["Fel Infusion", "Light Infusion"]
                                            },
                                            ], actors_obj_dict=self.actors):
            if self.check_for_wipe(event):
                return
            if event.type == WCLEventTypes.apply_debuff:
                if event.name == "Fel Infusion":
                    colors[event.target] = "Green"
                    self.try_remove_from_dict(positions, event.target)
                elif event.name == "Light Infusion":
                    colors[event.target] = "Yellow"
                    self.try_remove_from_dict(positions, event.target)
            else:
                if event.point_x is None or event.point_y is None:
                    continue
                event_position = (event.point_x, event.point_y)
                positions[event.target] = event_position
                if event.target in already_counted and already_counted.get(event.target) > event.timestamp - 15000:
                    continue
                close_mismatch = 0
                for player, position in positions.items():
                    if player == event.target:
                        continue
                    if colors.get(player) is not None and colors.get(event.target) is not None and colors.get(player) != colors.get(event.target):
                        if self.distance_calculation(event_position, position) < 1000:
                            close_mismatch += 1
                if close_mismatch > 3:
                    score_obj = self.score_objs.get(event.target)
                    score_obj.wrong_color -= 50
                    already_counted[event.target] = event.timestamp

    def blow_up_early(self):
        damage_dealt = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": "235138"
                                            }, actors_obj_dict=self.actors):
            damage_dealt[event.source] += event.damage_total
        for player, damage_done in damage_dealt.items():
            score_obj = self.score_objs.get(player)
            score_obj.didnt_jump_in_hole = int(damage_done / -500000.0)

    def wrong_orb(self):
        locations = {}
        wrath_name = "Wrath of the Creators"
        for event in self.client.get_events(self.wcl_fight,
                                            filters=[{
                                                "type": WCLEventTypes.damage,
                                                "ability.name": wrath_name
                                            }, {
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": ["Unstable Soul"]
                                            },
                                            ], actors_obj_dict=self.actors):
            if event.name == wrath_name:
                locations[event.target] = event.location
            else:
                print(event, locations)

from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import MaidenScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes


class MaidenAnalyzer(BossAnalyzer):
    SCORE_OBJ = MaidenScore

    def analyze(self):
        self.wrong_color()
        self.wrong_orb()
        self.blow_up_early()
        asdf
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
        for event in self.client.get_events(self.wcl_fight,
                                            filters=[{
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Unstable Soul"
                                            }, {
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": ["Fel Infusion", "Light Infusion"]
                                            },
                                            ], actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_debuff:
                if event.name == "Fel Infusion":
                    colors[event.target] = "Green"
                    self.try_remove_from_dict(positions, event.target)
                elif event.name == "Light Infusion":
                    colors[event.target] = "Yellow"
                    self.try_remove_from_dict(positions, event.target)
            else:
                positions[event.target] = (event.point_x, event.point_y)

    def blow_up_early(self):
        pass

    def wrong_orb(self):
        pass


from WoWRaidScore.common.analyzer import BossAnalyzer
from bfd.models import MekkatorqueScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class MekkatorqueAnalyzer(BossAnalyzer):
    SCORE_OBJ = MekkatorqueScore
    STOP_AT_DEATH = 3

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.wave_of_light()
        self.cleanup()
        self.save_score_objs()

    def wave_of_light(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Wave of Light"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).wave_of_light -= 10
            self.create_score_event(event.timestamp, "was hit by a Wave of Light",
                                    event.target)


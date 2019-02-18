
from WoWRaidScore.common.analyzer import BossAnalyzer
from uldir.models import ZekVozScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class ZekVozAnalyzer(BossAnalyzer):
    SCORE_OBJ = ZekVozScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.cleanup()
        self.save_score_objs()

    def touching_clouds(self):
        pass

    def eyebeams(self):
        pass

    def dropping_off_clouds_in_mid(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.remove_debuff,
                                                "ability.name": "Roiling Deceit"
                                            }, actors_obj_dict=self.actors):
            status = self.get_player_status_at_time(event.target, event.timestamp)
            print status
            if 2.65 >= status.point_y >= 2.45 and -1.55 <= status.point_x <= -1.2:
                self.create_score_event(event.timestamp, "Dropped off a cloud in a bad location.", event.target)
                self.score_objs.get(event.target).annihilation_soaks -= 15


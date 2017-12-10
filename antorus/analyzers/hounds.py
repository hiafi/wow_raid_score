
from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import FelhoundsScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class FelhoundsAnalyzer(BossAnalyzer):
    SCORE_OBJ = FelhoundsScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.molten_flare()
        self.consuming_sphere()
        self.desolate_path()
        self.enflamed()
        self.cleanup()
        self.save_score_objs()

    def molten_flare(self):
        pass

    def consuming_sphere(self):
        pass

    def desolate_path(self):
        pass

    def enflamed(self):
        pass
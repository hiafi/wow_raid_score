
from WoWRaidScore.common.analyzer import BossAnalyzer
from uldir.models import TalocScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class TalocAnalyzer(BossAnalyzer):
    SCORE_OBJ = TalocScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.cleanup()
        self.save_score_objs()
    

from WoWRaidScore.common.analyzer import BossAnalyzer
from antorus.models import AggramarScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class AggramarAnalyzer(BossAnalyzer):
    SCORE_OBJ = AggramarScore
    STOP_AT_DEATH = 5

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.cleanup()
        self.save_score_objs()

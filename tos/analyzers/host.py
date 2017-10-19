
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import HostScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class HostAnalyzer(BossAnalyzer):
    SCORE_OBJ = HostScore

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))

        self.cleanup()
        self.save_score_objs()


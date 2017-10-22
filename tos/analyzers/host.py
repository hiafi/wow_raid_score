
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import HostScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class HostAnalyzer(BossAnalyzer):
    SCORE_OBJ = HostScore
    ENGINE_LOCATION = (110600, 645700)
    PHYSICAL_SIDE = 109200

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.armor_breaking()
        self.soulbinds()
        self.tormented_cries()
        self.rupturing_slam()
        self.dissonance()
        self.cleanup()
        self.save_score_objs()

    def dissonance(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Dissonance",
                                                "source.disposition": "friendly"
                                            }, actors_obj_dict=self.actors):
            score_obj = self.score_objs.get(event.source)
            if not score_obj.tank:
                self.score_objs.get(event.source).dissonance -= 1

    def _get_armor_durations(self):
        bonecages = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_buff, WCLEventTypes.remove_buff],
                                                "ability.name": "Bonecage Armor"
                                            }, actors_obj_dict=self.actors):
            if event.target.name != "Ghastly Bonewarden":
                continue
            key = (event.target, event.target_instance)
            if event.type == WCLEventTypes.apply_buff:
                bonecages[key] = (event.timestamp, self.wcl_fight.end_time_str)
            else:
                bonecages[key] = (bonecages[key][0], event.timestamp)
        return bonecages

    def armor_breaking(self):
        bonecage_durations = self._get_armor_durations()
        last_scream_target = None
        already_missed = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.remove_debuff,
                                                "ability.name": "Shattering Scream"
                                            }, actors_obj_dict=self.actors):

            if (event.target, event.timestamp) == last_scream_target:
                continue
            last_scream_target = (event.target, event.timestamp)
            to_remove = []
            for armored_target, bonecage_duration in bonecage_durations.items():
                if self.between_duration(event.timestamp-100, bonecage_duration[1], event.timestamp+100):
                    to_remove.append(armored_target)
                    status = self.get_player_status_at_time(event.target, event.timestamp)
                    if status.point_x >= self.PHYSICAL_SIDE:
                        self.score_objs.get(event.target).break_armors += 8
                    else:
                        self.score_objs.get(event.target).break_armors += 2
                elif self.between_duration(bonecage_duration[0]+3000, event.timestamp, bonecage_duration[1]-5000):
                    if already_missed.get(event.target) != event.timestamp:
                        already_missed[event.target] = event.timestamp
                        self.score_objs.get(event.target).break_armors -= 6
            for remove_me in to_remove:
                del bonecage_durations[remove_me]

    def soulbinds(self):
        soulbind_targets = {}
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.remove_debuff],
                                                "ability.name": "Soulbind"
                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_debuff:
                soulbind_targets[event.target] = event.timestamp
            else:
                if soulbind_targets.get(event.target) is None:
                    continue
                duration = event.timestamp - soulbind_targets.get(event.target)
                val = 0
                if duration < 4300:
                    val = 5
                elif duration < 6300:
                    val = 2
                elif duration < 8300:
                    val = 0
                else:
                    val = int((duration - 7000) / 2000) * -8
                self.score_objs.get(event.target).soulbinds += val
                soulbind_targets[event.target] = None

    def rupturing_slam(self):
        slam_count = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Rupturing Slam"
                                            }, actors_obj_dict=self.actors):
            slam_count[event.target] += 1

        for player, count in slam_count.items():
            score_obj = self.score_objs.get(player)
            if not score_obj.tank:
                score_obj.rupturing_slam -= int(count * 0.5)

    def tormented_cries(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.remove_debuff,
                                                "ability.id": 238018
                                            }, actors_obj_dict=self.actors):
            status = self.get_player_status_at_time(event.target, event.timestamp+200, time_to_look_back=1000)
            if not status:
                continue
            angle = self.angle_between_points(self.ENGINE_LOCATION, status.location)
            val = 0
            if 0 <= angle <= 110:
                val = 5
            elif -45 <= angle <= 0:
                val = 2
            elif -160 <= angle <= -80 or 130 <= angle <= 180:
                val = -15
            self.score_objs.get(event.target).tormented_cries += val

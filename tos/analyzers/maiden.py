
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import MaidenScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class MaidenAnalyzer(BossAnalyzer):
    SCORE_OBJ = MaidenScore

    def analyze(self):
        print("Processing {}".format(self.wcl_fight))
        if self.wcl_fight.difficulty < self.MYTHIC_DIFFICULTY:
            self.wrong_color()
        self.wrong_orb()
        self.blow_up_early()
        self.cleanup()
        self.save_score_objs()

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
            if self.check_for_wipe(event, time_count=0):
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
        players_hit = defaultdict(int)
        num_explosions = defaultdict(int)
        last_explosion = {}
        min_num_hit = 4
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.id": "235138"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, time_count=0):
                break
            damage_threshold = {
                self.MYTHIC_DIFFICULTY: 4000000
            }
            if event.damage_total > damage_threshold.get(self.wcl_fight.difficulty, 1000000):
                player = event.source
                if event.source not in last_explosion or last_explosion.get(player, 0) < event.timestamp - 3000:
                    last_explosion[player] = event.timestamp
                    if players_hit[player] > min_num_hit:
                        num_explosions[player] += 1
                    players_hit[player] = 0
                players_hit[player] += 1
        for player, num_hit in players_hit.items():
            if num_hit > min_num_hit:
                num_explosions[player] += 1
        for player, explosions in num_explosions.items():
            score_obj = self.score_objs.get(player)
            score_obj.didnt_jump_in_hole -= 50 * explosions

    def get_phase_two_times(self):
        last_wrath = None
        phase_2_times = []
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.cast,
                                                "ability.name": ["Wrath of the Creators", "Infusion"]
                                            }, actors_obj_dict=self.actors):
            if event.name == "Wrath of the Creators":
                last_wrath = event.timestamp
            else:
                if last_wrath:
                    phase_2_times.append((last_wrath, event.timestamp))
                    last_wrath = None
        if last_wrath:
            phase_2_times.append((last_wrath, None))
        return phase_2_times

    def wrong_orb(self):
        phase_2_times = self.get_phase_two_times()
        for (start_time, end_time) in phase_2_times:
            number_affected = 0
            last_timestamp = None
            found_timestamp = None
            for event in self.client.get_events(self.wcl_fight,
                                                filters={
                                                    "type": [WCLEventTypes.apply_debuff],
                                                    "ability.name": ["Unstable Soul"]
                                                }, actors_obj_dict=self.actors, start_time=start_time, end_time=end_time):
                if last_timestamp is None:
                    last_timestamp = event.timestamp
                elif last_timestamp - 3000 > event.timestamp:
                    last_timestamp = event.timestamp
                    found_timestamp = None
                    number_affected = 0
                number_affected += 1
                if number_affected > 3 and found_timestamp is None:
                    found_timestamp = last_timestamp
                    player_status = self.get_all_player_status_at_time(last_timestamp)
                    print(player_status)


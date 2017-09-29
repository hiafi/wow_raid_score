
from WoWRaidScore.common.analyzer import BossAnalyzer
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from tos.models import MistressScore
from collections import defaultdict


class MistressAnalyzer(BossAnalyzer):
    SCORE_OBJ = MistressScore

    def analyze(self):
        print("Processing {}".format(self.wcl_fight))
        if self.wcl_fight.difficulty >= self.HEROIC_DIFFICULTY:
            self.murloc_debuff_uptime()
        if self.wcl_fight.difficulty >= self.MYTHIC_DIFFICULTY:
            self.bufferfish_uptime()
        if self.wcl_fight.percent <= 70.0:
            self.shadow_dropoffs()
        self.stupid_damage()
        self.hydra_shots()

        self.cleanup()
        self.save_score_objs()

    def _bufferfish_durations(self):
        debuff_dict = defaultdict(list)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.remove_debuff],
                                                "ability.name": "Delicious Bufferfish"
                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_debuff:
                debuff_dict[event.target].append((event.timestamp, None))
            else:
                old_time = debuff_dict[event.target][-1]
                debuff_dict[event.target][-1] = (old_time[0], event.timestamp)
        return debuff_dict

    def bufferfish_uptime(self):
        bufferfish_uptimes = self._bufferfish_durations()

        for target, uptimes in bufferfish_uptimes.items():
            score_obj = self.score_objs.get(target)
            score_obj.bufferfish_uptime = 0
            for uptime in uptimes:
                start_time, end_time = uptime
                try:
                    duration = (end_time - start_time)
                    score_obj.bufferfish_uptime += int((duration / 1000 - 15) / 10)
                except TypeError:
                    pass

    def murloc_debuff_uptime(self):
        shock_times = []
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.cast,
                                                "source.name": "Mistress Sassz\'ine",
                                                "ability.name": "Thundering Shock"
                                            }, actors_obj_dict=self.actors):
            shock_times.append(event.timestamp)

        debuffs = {}
        missed_shocks = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.remove_debuff],
                                                "ability.id": "230920"
                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_debuff:
                debuffs[event.target] = event.timestamp
            else:
                start_time = debuffs[event.target]
                end_time = event.timestamp
                for shock_time in shock_times:
                    if start_time < shock_time < (end_time - 5000):
                        missed_shocks[event.target] += 1
        for target, count in missed_shocks.items():
            score_obj = self.score_objs.get(target)
            score_obj.murlock_debuff_uptime = count * -5

    def shadow_dropoffs(self):
        debuff_dict = {}
        dropoffs = defaultdict(int)

        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff, WCLEventTypes.remove_debuff],
                                                "ability.name": "Befouling Ink"
                                            }, actors_obj_dict=self.actors):
            if event.type == WCLEventTypes.apply_debuff:
                debuff_dict[event.target] = event.timestamp
            else:
                start_time = debuff_dict.get(event.target)
                duration = event.timestamp - start_time
                if duration < 5900:
                    dropoffs[event.target] += 1

        for target, dropoffs in dropoffs.items():
            score_obj = self.score_objs.get(target)
            score_obj.dropoffs = dropoffs * 10

    def remove_from_set(self, player, player_set):
        try:
            player_set.remove(player)
        except KeyError:
            pass

    def hydra_shots(self):
        bufferfish_times = self._bufferfish_durations()
        deaths = self.get_player_death_times()
        recent_timestamp = 0
        players_to_check = set()
        missed_soaks = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Hydra Acid"
                                            }, actors_obj_dict=self.actors):
            if event.timestamp - recent_timestamp > 3000:
                for player in players_to_check:
                    missed_soaks[player] += 1
                recent_timestamp = event.timestamp
                players_to_check = set([p for p in self.score_objs.keys()])

                for p, score_obj in self.score_objs.items():
                    if score_obj.tank:
                        self.remove_from_set(p, players_to_check)
                    elif deaths.get(p) is not None and deaths.get(p, 0) <= recent_timestamp:
                        self.remove_from_set(p, players_to_check)

                for player, bufferfish_time in bufferfish_times.items():
                    for start_time, end_time in bufferfish_time:
                        if end_time is None:
                            end_time = recent_timestamp + 1000
                        if start_time <= recent_timestamp <= end_time:
                            self.remove_from_set(player, players_to_check)
            self.remove_from_set(event.target, players_to_check)
        for player, missed_soak_count in missed_soaks.items():
            score_obj = self.score_objs.get(player)
            score_obj.hydra_shots -= 10

        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.apply_debuff_stack,
                                                "ability.name": "Hydra Acid"
                                            }, actors_obj_dict=self.actors):
            score_obj = self.score_objs.get(event.target)
            score_obj.stacked_hydra_shots -= 50

    def stupid_damage(self):
        death_numbers = self.get_player_death_number()
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Slicing Tornado"
                                            }, actors_obj_dict=self.actors):
            if death_numbers.get(event.target, 1) < self.STOP_AT_DEATH:
                score_obj = self.score_objs.get(event.target)
                score_obj.tornado_damage -= 40
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Crashing Wave"
                                            }, actors_obj_dict=self.actors):
            if death_numbers.get(event.target, 1) < self.STOP_AT_DEATH:
                score_obj = self.score_objs.get(event.target)
                score_obj.hit_by_giant_fish -= 60


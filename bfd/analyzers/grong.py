
from WoWRaidScore.common.analyzer import BossAnalyzer
from bfd.models import GrongScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class GrongAnalyzer(BossAnalyzer):
    SCORE_OBJ = GrongScore
    STOP_AT_DEATH = 3

    THROW_DAMAGE = {
        BossAnalyzer.MYTHIC_DIFFICULTY: 85000
    }

    def analyze(self):
        print("Analyzing {}".format(self.wcl_fight))
        self.fear()
        self.chill_of_death()
        self.slam_echo()
        self.not_running_out()
        self.cleanup()
        self.save_score_objs()

    def fear(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": "Ferocious Roar"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            score_obj = self.score_objs.get(event.target)
            if score_obj.tank:
                continue
            score_obj.fear -= 20
            self.create_score_event(event.timestamp, "was hit by a Fear",
                                    event.target)

    def chill_of_death(self):
        last_tick = {}
        num_ticks = defaultdict(int)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Chill of Death"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            if last_tick.get(event.target) < event.timestamp + 3000:
                num_ticks[event.target] += 1
            last_tick[event.target] = event.timestamp

        for target, num_ticks in num_ticks.items():
            self.score_objs.get(target).chill_of_death -= 2 * num_ticks

    def slam_echo(self):
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Deathly Echo"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                return
            self.score_objs.get(event.target).deathly_echo -= 30
            self.create_score_event(event.timestamp, "stood in the Deathly Echo",
                                    event.target)

    def not_running_out(self):
        throw_target_order = []
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.remove_debuff],
                                                "ability.name": "Bestial Throw Target"
                                            }, actors_obj_dict=self.actors):
            throw_target_order.append((event.target, event.timestamp))
        avg_dmg = []
        last_dmg_event = 0
        dmg_vals = []
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.damage],
                                                "ability.name": "Bestial Impact"
                                            }, actors_obj_dict=self.actors):
            if self.check_for_wipe(event, death_count=self.STOP_AT_DEATH):
                continue
            if event.timestamp < last_dmg_event + 5000:
                last_dmg_event = event.timestamp
                avg_dmg.append(sum(dmg_vals) / len(dmg_vals))
                dmg_vals = []
            dmg_vals.append(event.raw_damage)
        avg_dmg.append(sum(dmg_vals) / len(dmg_vals))
        for index, average in enumerate(avg_dmg):
            target, timestamp = throw_target_order[index]
            if average > self.THROW_DAMAGE.get(self.wcl_fight.difficulty, 50000):
                point_val = 5 * (average - self.THROW_DAMAGE.get(self.wcl_fight.difficulty, 50000)) / 5000.0
                self.score_objs.get(target).not_running_out_throw -= int(point_val)
                self.create_score_event(timestamp, "did not run the throw tank out far enough",
                                        target)

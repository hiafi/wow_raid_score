
from WoWRaidScore.common.analyzer import BossAnalyzer
from tos.models import MaidenScore
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes
from collections import defaultdict


class MaidenAnalyzer(BossAnalyzer):
    SCORE_OBJ = MaidenScore
    CENTER_OF_ROOM = (79500, 634800)
    ORB_DISTANCES = [(2400, 3000), (3600, 3900), (4200, 4900)]
    DISTANCE_TO_TRIGGER_BOMB = 600

    def __init__(self, *args):
        super(MaidenAnalyzer, self).__init__(*args)
        self.colors_for_fight_dict = {}
        self.safe_bombs = {}
        self.phase_2_times = []
        self.unstable_souls = []
        self.mass_instability_times = []
        self.exploding_events = []
        self.didnt_jump_in_hole_people = {}

    def cleanup(self):
        self.colors_for_fight_dict = {}
        self.safe_bombs = {}
        self.phase_2_times = []
        self.unstable_souls = []
        self.mass_instability_times = []
        self.exploding_events = []
        self.didnt_jump_in_hole_people = {}

    def analyze(self):
        solved_attempts = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                           26, 27, 28, 29, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46}
        unsolved_attempts = {}
        print("Processing {}".format(self.wcl_fight))
        self.check_for_not_jumping_in_hole()
        self.wrong_orb()
        self.wrong_color()
        # self.right_orb()
        self.cleanup()
        self.save_score_objs()

    def try_remove_from_dict(self, dic, key):
        try:
            del dic[key]
        except KeyError:
            pass

    def get_unstable_soul_debuffs(self, start_time=None, end_time=None):
        if not self.unstable_souls:
            for event in self.client.get_events(self.wcl_fight,
                                                filters={
                                                    "type": [WCLEventTypes.apply_debuff],
                                                    "ability.name": "Unstable Soul"
                                                },
                                                actors_obj_dict=self.actors):
                self.unstable_souls.append(event)
        if start_time is None:
            start_time = self.wcl_fight.start_time_str
        if end_time is None:
            end_time = self.wcl_fight.end_time_str
        return [e for e in self.unstable_souls if self.between_duration(start_time, e.timestamp, end_time)]

    def get_colors_for_fight(self):
        if self.colors_for_fight_dict:
            return self.colors_for_fight_dict
        colors = defaultdict(dict)
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": [WCLEventTypes.apply_debuff],
                                                "ability.name": ["Fel Infusion", "Light Infusion"]
                                            },
                                            actors_obj_dict=self.actors):
            if event.name == "Fel Infusion":
                colors[event.target][event.timestamp] = "Green"
            elif event.name == "Light Infusion":
                colors[event.target][event.timestamp] = "Yellow"
        self.colors_for_fight_dict = colors
        return colors

    def get_color_at_timestamp(self, player, timestamp):
        colors = self.get_colors_for_fight()
        color = None
        best_timestamp = 0
        for current_timestamp, current_color in colors.get(player, {}).items():
            if best_timestamp < current_timestamp < timestamp:
                best_timestamp = current_timestamp
                color = current_color
        return color

    def wrong_color(self):
        people_to_check_against = defaultdict(list)
        for event in self.get_unstable_soul_debuffs() + self.get_killing_explosion_events(get_first=True):
            found_existing = False
            mass_instability = False
            person_to_check = event.source if event.type == WCLEventTypes.damage else event.target
            if self.check_for_wipe(event, time_count=0):
                continue
            if self.between_duration(event.timestamp - 100, self.didnt_jump_in_hole_people.get(person_to_check, 0), event.timestamp + 100):
                continue
            for mass_instability_time in self.get_instability_times():
                if self.between_duration(event.timestamp-2300, mass_instability_time, event.timestamp-1800):
                    mass_instability = True
            if mass_instability:
                continue

            exploded = event.type == WCLEventTypes.damage
            for checking_timestamp in people_to_check_against.keys():
                if self.between_duration(event.timestamp - 100, checking_timestamp, event.timestamp + 100):
                    if person_to_check not in people_to_check_against[checking_timestamp]:
                        people_to_check_against[checking_timestamp].append(person_to_check)
                    found_existing = True
            if not found_existing:
                if person_to_check not in people_to_check_against[event.timestamp]:
                    people_to_check_against[event.timestamp].append(person_to_check)

        for timestamp, related_people in people_to_check_against.items():
            was_echos = False
            for related_person in related_people:
                was_echos = self.check_for_echos(related_person, timestamp)
            if was_echos:
                continue
            if len(related_people) == 1:
                if not self.check_for_in_wrong_group(timestamp, related_people):
                    self.check_orbs_phase_1(timestamp, related_people)
            elif len(related_people) == 2:
                if not self.check_for_running_into_wrong_color_group(timestamp, related_people):
                    self.two_people_check(timestamp, related_people)
            else:
                self.check_for_running_into_wrong_color_group(timestamp, related_people)

    def check_orbs_phase_1(self, timestamp, related_people):
        if self.between_multiple_durations(timestamp, self.get_phase_two_times()):
            return
        player = related_people[0]
        color = self.get_color_at_timestamp(player, timestamp)
        other_player_status = self.get_all_player_status_at_time(timestamp)
        player_status = other_player_status.get(player)
        similar_colors_far_away = 0
        for other_player, status in other_player_status.items():
            if other_player == player or color != self.get_color_at_timestamp(other_player, timestamp):
                continue
            distance = self.distance_calculation(player_status.location, status.location)
            if 1500 > distance > 300:
                similar_colors_far_away += 1
        if similar_colors_far_away > 2:
            print("{} ate an orb".format(player))
            self.score_objs.get(player).bomb_from_p1_orb -= 10

    def check_for_echos(self, player, timestamp):
        item_to_get = {
            "Green": "Light Echoes",
            "Yellow": "Fel Echoes"
        }
        color = self.get_color_at_timestamp(player, timestamp)
        for event in self.client.get_events(self.wcl_fight,
                                            start_time=timestamp - 3000,
                                            end_time=timestamp + 1000,
                                            actor_id=self.get_actor_id(player),
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": item_to_get.get(color)
                                            }, actors_obj_dict=self.actors):
            self.score_objs.get(event.target).bomb_from_echos -= 10
            print("{} sat in echos".format(event.target))
            return True
        return False

    def check_for_in_wrong_group(self, timestamp, related_people):
        player = related_people[0]
        all_status = self.get_all_player_status_at_time(timestamp, cache=True)
        status = all_status.get(player)
        color = self.get_color_at_timestamp(player, timestamp)
        close_by = 0
        for other_player, other_status in all_status.items():
            if player == other_player:
                continue
            other_color = self.get_color_at_timestamp(other_player, timestamp)
            distance = self.distance_calculation(status.location, other_status.location)
            if color != other_color and distance < self.DISTANCE_TO_TRIGGER_BOMB:
                close_by += 1
        if close_by >= 3:
            self.score_objs.get(player).wrong_color -= 5 * len(related_people)
            print("{} was in the wrong group".format(player))
            return True
        return False

    def two_people_check(self, timestamp, related_people):
        status = self.get_all_player_status_at_time(timestamp, cache=True)
        status_old = self.get_all_player_status_at_time(timestamp - 2000)
        person1 = related_people[0]
        person2 = related_people[1]
        distance_to_move = 300
        if self.get_color_at_timestamp(person1, timestamp) != self.get_color_at_timestamp(person2, timestamp):
            person1_movement = self.distance_calculation(status.get(person1).location, status_old.get(person1).location)
            person2_movement = self.distance_calculation(status.get(person2).location, status_old.get(person2).location)
            if person1_movement > distance_to_move and person1_movement > person2_movement:
                print("{} ran into {}".format(person1, person2))
                self.score_objs.get(person1).wrong_color -= 10
            elif person2_movement > distance_to_move and person2_movement > person1_movement:
                print("{} ran into {}".format(person2, person1))
                self.score_objs.get(person2).wrong_color -= 10
            elif person2_movement > distance_to_move and person1_movement > distance_to_move:
                print("They both fucked up")
                self.score_objs.get(person1).wrong_color -= 5
                self.score_objs.get(person2).wrong_color -= 5

    def check_for_running_into_wrong_color_group(self, timestamp, related_people):
        someone_was_in_wrong_group = False
        for person in related_people:
            all_different = True
            for person2 in related_people:
                if person == person2:
                    continue
                if self.get_color_at_timestamp(person, timestamp) == self.get_color_at_timestamp(person2, timestamp):
                    all_different = False
            if all_different:
                print("{} ran into the wrong group".format(person))
                self.score_objs.get(person).wrong_color -= 5 * len(related_people)
                someone_was_in_wrong_group = True
        return someone_was_in_wrong_group

    def check_for_not_jumping_in_hole(self):
        people_to_check = defaultdict(list)
        for person, debuff_durations in self.get_debuff_start_and_end("Unstable Soul").items():
            for (start, end) in debuff_durations:
                duration = end - start
                if duration >= 7800:
                    people_to_check[person].append((end-500, end+1000))

        for person, times_blew_up in people_to_check.items():
            found_person = False
            people_hit = 0
            for event in self.client.get_events(self.wcl_fight,
                                                actor_id=self.get_actor_id(person),
                                                filters={
                                                    "type": WCLEventTypes.damage,
                                                    "ability.name": "Unstable Soul",
                                                    "source.name": person.name
                                                }, actors_obj_dict=self.actors):
                if event.source != person:
                    continue
                if self.check_for_wipe(event, time_count=0):
                    continue
                if not self.between_multiple_durations(event.timestamp, people_to_check.get(event.source, [])):
                    continue
                if event.damage_done > 4000000:
                    people_hit += 1
                if people_hit >= 3 and not found_person:
                    print("{} Blew up".format(person))
                    self.score_objs.get(person).didnt_jump_in_hole -= 20
                    found_person = True
                    self.didnt_jump_in_hole_people[person] = event.timestamp

    def get_killing_explosion_events(self, target=None, get_first=False):
        if self.exploding_events:
            return self._return_exploding_events(target, get_first)

        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.damage,
                                                "ability.name": "Unstable Soul",
                                            }, actors_obj_dict=self.actors):
            if event.damage_done > 4000000:
                self.exploding_events.append(event)
        return self._return_exploding_events(target, get_first)

    def _return_exploding_events(self, target=None, get_first=False):
        already_found = set()
        new_events = []
        for event in self.exploding_events:
            if event.source in already_found:
                continue
            if target is not None and target != event.source:
                continue
            if get_first:
                already_found.add(event.source)
            new_events.append(event)
        return new_events

    def get_phase_two_times(self):
        if self.phase_2_times:
            return self.phase_2_times
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
            phase_2_times.append((last_wrath, self.wcl_fight.end_time_str))
        self.phase_2_times = phase_2_times
        return self.phase_2_times

    def get_instability_times(self):
        if self.mass_instability_times:
            return self.mass_instability_times
        for event in self.client.get_events(self.wcl_fight,
                                            filters={
                                                "type": WCLEventTypes.cast,
                                                "ability.name": ["Mass Instability"]
                                            }, actors_obj_dict=self.actors):
            self.mass_instability_times.append(event.timestamp)
        return self.mass_instability_times

    def wrong_orb(self):
        phase_2_times = self.get_phase_two_times()
        potentials_to_check = []
        for (start_time, end_time) in phase_2_times:
            for event in self.get_unstable_soul_debuffs(start_time, end_time):
                if self.check_for_wipe(event, time_count=0):
                    continue
                status = self.get_player_status_at_time(event.target, event.timestamp, cache=True)
                distance_from_center = self.distance_calculation(self.CENTER_OF_ROOM, status.location)
                for orb_distance in self.ORB_DISTANCES:
                    if orb_distance[0] <= distance_from_center <= orb_distance[1]:
                        potentials_to_check.append((event.target, event.timestamp))

        for player, timestamp in potentials_to_check:
            valid = True
            for other_player, other_timestamp in potentials_to_check:
                if player == other_player:
                    continue
                if self.between_duration(other_timestamp - 100, timestamp, other_timestamp + 100):
                    if self.get_color_at_timestamp(player, timestamp) != self.get_color_at_timestamp(other_player, timestamp):
                        valid = False
            if valid:
                print("Wrong Orb", player, timestamp)
                score_obj = self.score_objs.get(player)
                val = 20
                if score_obj.ranged_dps and self.wcl_fight.difficulty == self.MYTHIC_DIFFICULTY:
                    val = 10
                score_obj.wrong_orb -= val

    def right_orb(self):
        for (start_time, end_time) in self.get_phase_two_times():
            for event in self.client.get_events(self.wcl_fight,
                                                filters={
                                                    "type": [WCLEventTypes.apply_debuff, WCLEventTypes.apply_debuff_stack],
                                                    "ability.name": ["Creator's Grace", "Demon's Vigor"]
                                                }, actors_obj_dict=self.actors, start_time=start_time, end_time=end_time):
                splashed = True
                status = self.get_player_status_at_time(event.target, event.timestamp, cache=True)
                distance_from_center = self.distance_calculation(self.CENTER_OF_ROOM, status.location)
                for orb_distance in self.ORB_DISTANCES:
                    if orb_distance[0] <= distance_from_center <= orb_distance[1]:
                        splashed = False
                if splashed:
                    self.score_objs.get(event.target).wrong_orb += 1
                else:
                    self.score_objs.get(event.target).wrong_orb += 4


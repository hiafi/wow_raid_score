import requests
import time
from datetime import datetime

from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes, WCLRaid, WCLFight, WCLPlayer, WCLEnemy, WCLNPC, create_event_obj

from collections import defaultdict

API_KEY = "da1464008d3107d21c2cfa8061b5f544"


class WCLRequests(object):

    def __init__(self, raid_id):
        self.raid_id = raid_id

    @staticmethod
    def base_url():
        return "https://www.warcraftlogs.com:443/v1"

    @staticmethod
    def _to_url(string):
        string = string.replace(" ", "%20")
        string = string.replace("\"", "%22")
        string = string.replace("=", "%3D")
        return string

    @staticmethod
    def _get_players(r_json):
        return WCLRequests.get_actors(r_json, "friendlies", WCLPlayer, ignore_npc=True)

    @staticmethod
    def _get_npcs(r_json):
        return WCLRequests.get_actors(r_json, "friendlies", WCLNPC, ignore_npc=False, only_npcs=True)

    @staticmethod
    def _get_enemies(r_json):
        return WCLRequests.get_actors(r_json, "enemies", WCLEnemy, ignore_npc=False)

    @staticmethod
    def get_actors(r_json, data_category, wcl_obj, ignore_npc=True, only_npcs=False):
        actors = {}
        for actor in r_json.get(data_category):
            if ignore_npc and actor.get("type") in {'NPC', 'Unknown', 'Pet'}:
                continue
            if only_npcs and actor.get("type") not in {'NPC', 'Unknown', 'Pet'}:
                continue
            p = wcl_obj(actor)
            actors[p.id] = p
        return actors


    @staticmethod
    def _get_fights(r_json):
        fights = {}
        raid_start_time = r_json.get("start")
        for fight in r_json.get("fights"):
            if fight.get("boss") is None or fight.get("boss") == 0:
                continue
            f = WCLFight(fight, r_json.get("zone"), raid_start_time)
            fights[f.id] = f

        by_boss = defaultdict(list)
        for fight in fights.values():
            by_boss[fight.boss_id].append(fight)
        for boss, sorted_fights in by_boss.items():
            sorted_fights = sorted(sorted_fights, key=lambda x: x.id)
            for attempt in range(len(sorted_fights)):
                sorted_fights[attempt].set_attempt(attempt+1)

        return fights

    @staticmethod
    def _add_players_to_fights(players, fights):
        for player in players.values():
            for fight_id in player.fights:
                fight = fights.get(fight_id)
                if fight:
                    fight.add_player(player)

    @staticmethod
    def _add_enemies_to_fights(enemies, fights):
        for enemy in enemies.values():
            for fight_id in enemy.fights:
                fight = fights.get(fight_id)
                if fight:
                    fight.add_enemy(enemy)

    @staticmethod
    def _add_npcs_to_fights(npcs, fights):
        for npc in npcs.values():
            for fight_id in npc.fights:
                fight = fights.get(fight_id)
                if fight:
                    fight.add_enemy(npc)

    def get_fights(self):
        url = "{}/report/fights/{code}?api_key={api_key}".format(WCLRequests.base_url(), code=self.raid_id,
                                                                 api_key=API_KEY)
        r_json = self._get_json_data_from_wcl(url)

        wcl_players = WCLRequests._get_players(r_json)
        wcl_enemies = WCLRequests._get_enemies(r_json)
        wcl_npcs = WCLRequests._get_npcs(r_json)
        wcl_fights = WCLRequests._get_fights(r_json)
        WCLRequests._add_players_to_fights(wcl_players, wcl_fights)
        WCLRequests._add_enemies_to_fights(wcl_enemies, wcl_fights)
        WCLRequests._add_npcs_to_fights(wcl_npcs, wcl_fights)

        return wcl_fights

    def get_raid_info(self):
        url = "{}/report/fights/{code}?api_key={api_key}".format(WCLRequests.base_url(), code=self.raid_id,
                                                                 api_key=API_KEY)
        r_json = self._get_json_data_from_wcl(url)
        return WCLRaid(r_json)

    @staticmethod
    def _to_url(url):
        url = url.replace(" ", "%20")
        url = url.replace("\"", "%22")
        url = url.replace("=", "%3D")
        url = url.replace("<", "%3C")
        url = url.replace(">", "%3E")
        url = url.replace("'", "%27")
        return url

    @staticmethod
    def build_single_filter_param(filter_name, filter_value):
        if isinstance(filter_value, tuple):
            return u"{}{}\"{}\"".format(filter_name, filter_value[0], filter_value[1])
        return u"{}=\"{}\"".format(filter_name, filter_value)

    @staticmethod
    def build_filter_param(filter_name, filter_value):
        if isinstance(filter_value, list):
            return "({})".format(" OR ".join([WCLRequests.build_single_filter_param(filter_name, val) for val in filter_value]))
        return WCLRequests.build_single_filter_param(filter_name, filter_value)


    @staticmethod
    def _build_filters(filters):
        if filters:
            if isinstance(filters, list):
                return u"&filter=" + u" OR ".join([u"({})".format(WCLRequests._to_url(u" AND ".join([WCLRequests.build_filter_param(filter_name, filter_value) for
                                                  filter_name, filter_value in filter.items()]))) for filter in filters])
            else:
                return u"&filter=" + WCLRequests._to_url(u" AND ".join([WCLRequests.build_filter_param(filter_name, filter_value) for
                                                  filter_name, filter_value in filters.items()]))
        return u""

    def _get_json_data_from_wcl(self, url, max_attempts=5):
        json_data = None
        attempts = max_attempts
        while not json_data and attempts > 0:
            response = requests.get(url)
            attempts -= 1
            if response.status_code != 200:
                print(datetime.now(), response.status_code, response.text)
                if attempts > 0:
                    time.sleep((max_attempts - attempts) * 60)
            else:
                json_data = response.json()
        if not json_data:
            raise Exception("Unable to get data")
        return json_data

    def _get_event_json(self, start_time, end_time, actor_id, filters):
        additional_data = u"{actor_id}{filter}".format(
            actor_id=u"&actorid={}".format(actor_id) if actor_id else "",
            filter=WCLRequests._build_filters(filters))

        url = u"{base_url}/report/events/{raid_id}?api_key={api_key}&start={start_time}&end={end_time}{additional}".format(
            base_url=WCLRequests.base_url(),
            raid_id=self.raid_id,
            api_key=API_KEY,
            start_time=start_time,
            end_time=end_time,
            additional=additional_data
        )
        return self._get_json_data_from_wcl(url)

    def _get_table_json(self, view, start_time, end_time, filters):
        additional_data = "{filter}".format(
            filter=WCLRequests._build_filters(filters))

        url = "{base_url}/report/tables/{view}/{raid_id}?api_key={api_key}&start={start_time}&end={end_time}{additional}".format(
            base_url=WCLRequests.base_url(),
            raid_id=self.raid_id,
            api_key=API_KEY,
            start_time=start_time,
            end_time=end_time,
            view=view,
            additional=additional_data
        )
        return self._get_json_data_from_wcl(url)

    def get_events(self, fight, actor_id=None, filters=None, actors_obj_dict=None, start_time=None, end_time=None):
        if start_time is None:
            start_time = fight.start_time_str
        if end_time is None:
            end_time = fight.end_time_str
        r_json = self._get_event_json(start_time, end_time, actor_id, filters)
        events = r_json.get("events")
        next_timestamp = 0
        while events:
            for event in events:
                yield create_event_obj(event, fight, actors_obj_dict=actors_obj_dict)
            if next_timestamp != r_json.get("nextPageTimestamp"):
                next_timestamp = r_json.get("nextPageTimestamp")
            else:
                next_timestamp = None

            if next_timestamp:
                r_json = self._get_event_json(next_timestamp, end_time, actor_id, filters)
                events = r_json.get("events")
            else:
                events = []

    def get_table_data(self, fight, view, filters=None, start_time=None, end_time=None):
        if start_time is None:
            start_time = fight.start_time_str
        if end_time is None:
            end_time = fight.end_time_str
        data = self._get_table_json(view, start_time, end_time, filters)

    def get_death_times(self, fight, actors_obj_dict=None):
        deaths = {}
        for event in self.get_events(fight,
                                     filters={"type": WCLEventTypes.death},
                                     actors_obj_dict=actors_obj_dict):
            if event.target_is_friendly and event.target != "Unknown" and not isinstance(event.target, int):
                deaths[event.target] = event.timestamp
        return deaths

    def get_death_order(self, fight, actors_obj_dict=None):
        deaths = self.get_death_times(fight, actors_obj_dict)
        tmp = sorted([(death_time, player) for player, death_time in deaths.items()], key=lambda x: x[0])
        return [p[1] for p in tmp]

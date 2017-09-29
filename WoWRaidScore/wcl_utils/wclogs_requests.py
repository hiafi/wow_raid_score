import requests
import time
from datetime import datetime

from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes, WCLRaid, WCLFight, WCLPlayer, WCLApplyDebuffEvent, \
    WCLDamageEvent, WCLEnemy, WCLRemoveDebuffEvent, WCLDeathEvent, WCLCastEvent, WCLPlayerFightInfo, WCLApplyDebuffStackEvent

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
    def _get_enemies(r_json):
        return WCLRequests.get_actors(r_json, "enemies", WCLEnemy, ignore_npc=False)

    @staticmethod
    def get_actors(r_json, data_category, wcl_obj, ignore_npc=True):
        actors = {}
        for actor in r_json.get(data_category):
            if ignore_npc and actor.get("type") in {'NPC', 'Unknown', 'Pet'}:
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

    def get_fights(self):
        url = "{}/report/fights/{code}?api_key={api_key}".format(WCLRequests.base_url(), code=self.raid_id,
                                                                 api_key=API_KEY)
        r_json = requests.get(url).json()

        wcl_players = WCLRequests._get_players(r_json)
        wcl_enemies = WCLRequests._get_enemies(r_json)
        wcl_fights = WCLRequests._get_fights(r_json)
        WCLRequests._add_players_to_fights(wcl_players, wcl_fights)
        WCLRequests._add_enemies_to_fights(wcl_enemies, wcl_fights)

        return wcl_fights

    def get_raid_info(self):
        url = "{}/report/fights/{code}?api_key={api_key}".format(WCLRequests.base_url(), code=self.raid_id,
                                                                 api_key=API_KEY)
        r_json = requests.get(url).json()
        return WCLRaid(r_json)

    @staticmethod
    def _to_url(url):
        url = url.replace(" ", "%20")
        url = url.replace("\"", "%22")
        url = url.replace("=", "%3D")
        return url

    @staticmethod
    def build_filter_param(filter_name, filter_value):
        if isinstance(filter_value, list):
            return "({})".format(" OR ".join(["{}=\"{}\"".format(filter_name, val) for val in filter_value]))
        return "{}=\"{}\"".format(filter_name, filter_value)


    @staticmethod
    def _build_filters(filters):
        if filters:
            if isinstance(filters, list):
                return "&filter=" + " OR ".join(["({})".format(WCLRequests._to_url(" AND ".join([WCLRequests.build_filter_param(filter_name, filter_value) for
                                                  filter_name, filter_value in filter.items()]))) for filter in filters])
            else:
                return "&filter=" + WCLRequests._to_url(" AND ".join([WCLRequests.build_filter_param(filter_name, filter_value) for
                                                  filter_name, filter_value in filters.items()]))
        return ""

    def _create_event_obj(self, data, actors_obj_dict):
        types = {
            WCLEventTypes.apply_debuff: WCLApplyDebuffEvent,
            WCLEventTypes.apply_debuff_stack: WCLApplyDebuffStackEvent,
            WCLEventTypes.remove_debuff: WCLRemoveDebuffEvent,
            WCLEventTypes.damage: WCLDamageEvent,
            WCLEventTypes.death: WCLDeathEvent,
            WCLEventTypes.cast: WCLCastEvent,
            WCLEventTypes.combatant_info: WCLPlayerFightInfo

        }
        cls = types.get(data.get("type"))
        if cls:
            return cls(data, actors_obj_dict)
        return data

    def _get_event_json(self, start_time, end_time, actor_id, filters):
        additional_data = "{actor_id}{filter}".format(
            actor_id="&actorid={}".format(actor_id) if actor_id else "",
            filter=WCLRequests._build_filters(filters))

        url = "{base_url}/report/events/{raid_id}?api_key={api_key}&start={start_time}&end={end_time}{additional}".format(
            base_url=WCLRequests.base_url(),
            raid_id=self.raid_id,
            api_key=API_KEY,
            start_time=start_time,
            end_time=end_time,
            additional=additional_data
        )
        json_data = None
        attempts = 3
        while not json_data and attempts > 0:
            response = requests.get(url)
            attempts -= 1
            if response.status_code != 200:
                print(datetime.now(), response.status_code, response.text)
                if attempts > 0:
                    time.sleep((3 - attempts) * 60)
            else:
                json_data = response.json()
        if not json_data:
            raise Exception("Unable to get event data")
        return json_data

    def get_events(self, fight, actor_id=None, filters=None, actors_obj_dict=None):
        r_json = self._get_event_json(fight.start_time_str, fight.end_time_str, actor_id, filters)
        events = r_json.get("events")
        while events:
            for event in events:
                yield self._create_event_obj(event, actors_obj_dict=actors_obj_dict)
            next_timestamp = r_json.get("nextPageTimestamp")
            if next_timestamp:
                data = self._get_event_json(next_timestamp, fight.end_time_str, actor_id, filters)
                events = data.get("events")
            else:
                events = []

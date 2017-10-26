from django.core.exceptions import ObjectDoesNotExist
from tos.analyzer_builder import tos_fights
from WoWRaidScore.models import Player, Fight, Boss
from WoWRaidScore.wcl_utils.wcl_data_objs import WCLEventTypes

raid_id_to_fight_dict = {
    13: tos_fights
}


def _get_player_objs_dict(wcl_fights):
    players_to_get = {}
    for fight in wcl_fights.values():
        for player in fight.players:
            if player.id not in players_to_get:
                try:
                    players_to_get[player.id] = Player.objects.get(guid=player.guid)
                except ObjectDoesNotExist:
                    p_obj = Player(name=player.name, server="", guid=player.guid)
                    p_obj.save()
                    players_to_get[player.id] = p_obj
    return players_to_get


def _get_boss(wcl_fight):
    try:
        return Boss.objects.get(boss_id=wcl_fight.boss_id)
    except ObjectDoesNotExist:
        boss = Boss(boss_id=wcl_fight.boss_id, zone_id=wcl_fight.zone_id, name=wcl_fight.name)
        boss.save()
        return boss


def _create_fight_obj(wcl_fight, raid):
    boss = _get_boss(wcl_fight)
    fight = Fight(raid=raid, boss=boss, killed=wcl_fight.kill, percent=wcl_fight.percent, start_time=wcl_fight.start_time, end_time=wcl_fight.end_time, fight_id=wcl_fight.id, attempt=wcl_fight.attempt)
    fight.save()
    return fight


def _get_combatant_info(wcl_client, wcl_fight, actors):
    specs = {}
    for event in wcl_client.get_events(wcl_fight, filters={"type": WCLEventTypes.combatant_info},
                                       actors_obj_dict=actors):
        specs[event.source] = event.spec_id
    return specs


def build_analyzers(wcl_fights, raid_obj, wcl_client):
    analyzers = []
    player_objs = _get_player_objs_dict(wcl_fights)
    for wcl_fight in wcl_fights.values():
        raid = raid_id_to_fight_dict.get(wcl_fight.zone_id)
        if not raid:
            continue
        analyzer = raid.get(wcl_fight.boss_id)
        if analyzer:
            fight = _create_fight_obj(wcl_fight, raid_obj)
            players = {wcl_player.id: player_objs.get(wcl_player.id) for wcl_player in wcl_fight.players}
            specs = _get_combatant_info(wcl_client, wcl_fight, players)
            score_objs = analyzer.create_raid_scores(players.values(), fight, specs)
            players.update(wcl_fight.enemies)
            analyzers.append(analyzer(wcl_fight, wcl_client, score_objs, players, fight))
    return analyzers

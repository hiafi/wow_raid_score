# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict

from django.shortcuts import render
from django.http import HttpResponse

from WoWRaidScore.models import Raid, Fight, RaidScore, Player, Boss
from WoWRaidScore.tasks import parse_task, parse_raid_task

from celery.result import AsyncResult

import json


# Create your views here.

def view_raids(request):
    raids = Raid.objects.all()
    return render(request, "raids_view.html", {"raids": raids})


def _get_avg_scores(score_objs):
    grouped_scores = defaultdict(lambda: defaultdict(list))
    for score_obj in score_objs:
        grouped_scores[score_obj.player][score_obj.fight.boss].append(score_obj.total)
    avg_scores = defaultdict(lambda: defaultdict(int))
    for player, boss_scores in grouped_scores.items():
        for boss, scores in boss_scores.items():
            avg_scores[boss][player] = sum(scores) / len(scores)
    return avg_scores


def _sort_avg_scores(avg_scores):
    new_scores = {}
    for boss, score_dict in avg_scores.items():
        new_scores[boss] = sorted([(score, player, boss) for player, score in score_dict.items()], reverse=True, key=lambda x: x[0])
    boss_order = new_scores.keys()
    transposed_table = [[b for b in boss_order]]
    for index in range(max([len(new_scores[b]) for b in boss_order])):
        transposed_table.append([])
        for boss in boss_order:
            if len(new_scores[boss]) > index:
                transposed_table[-1].append(new_scores[boss][index])
    
    return transposed_table


def view_raid(request, raid_id):
    raid = Raid.objects.get(raid_id=raid_id)
    fights = Fight.objects.filter(raid=raid)
    score_objs = RaidScore.objects.filter(fight__in=fights).select_subclasses()
    players = {score_obj.player for score_obj in score_objs}
    avg_scores = _get_avg_scores(score_objs)
    sorted_scores = _sort_avg_scores(avg_scores)

    return render(request, "raid_view.html", {"players": players, "score_objs": score_objs, "avg_scores": sorted_scores})


def view_player_details_for_raid(request, raid_id, player_id, boss_id):
    player = Player.objects.get(id=player_id)
    raid = Raid.objects.get(raid_id=raid_id)
    boss = Boss.objects.get(boss_id=boss_id)
    fights = Fight.objects.filter(raid=raid, boss=boss)
    score_objs = RaidScore.objects.filter(player=player, fight__in=fights).order_by("fight__fight_id").select_subclasses()
    total_list = [score.total for score in score_objs]
    health_list = [score.fight.percent for score in score_objs]
    totals = defaultdict(int)
    for key in score_objs[0].table_keys:
        for score_obj in score_objs:
            totals[key] += score_obj.score_dict.get(key, 0)
    for score_obj in score_objs:
        totals["Total"] += score_obj.total

    context = {"player": player, "score_objs": score_objs, "totals": total_list,
               "health": health_list, "total_dict": totals}
    return render(request, "player_raid_view.html", context)


def parse_raid(request, raid_id):
    parse_task.apply_async((raid_id,), task_id=raid_id)
    return render(request, 'parse.html', {})


def view_parse_progress(request, raid_id):
    task = AsyncResult(raid_id)
    data = task.result or task.state
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')


def parse_raid_legacy(request, raid_id):
    parse_raid_task(raid_id)
    return render(request, 'parse.html', {})

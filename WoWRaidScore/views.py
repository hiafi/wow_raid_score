# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from celery.result import AsyncResult
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render

import json
import logging

from WoWRaidScore.models import Raid, Fight, RaidScore, Player, Boss, Group
from WoWRaidScore.tasks import parse_task, parse_raid_task
from WoWRaidScore.wcl_utils.wclogs_requests import WCLRequests

logger = logging.getLogger(__name__)

# Create your views here.


def view_raids(request, player_id):
    player = User.objects.get(id=player_id)
    raids = Raid.objects.filter(user=player).order_by("time")
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


def _get_totals(score_objs):
    totals = defaultdict(lambda: defaultdict(int))
    keys_dict = {}
    final_totals = defaultdict(list)
    print(len(score_objs))
    for score_obj in score_objs:
        for name, val in score_obj.score_dict.items():
            if score_obj.fight.boss not in keys_dict:
                keys_dict[score_obj.fight.boss] = score_obj.table_keys
            totals[score_obj.fight.boss][name] += val
    print(totals)
    for boss, fight_scores_dict in totals.items():
        keys = keys_dict.get(boss)
        final_totals[boss].append(keys)
        ft = []
        for key in keys:
            ft.append(fight_scores_dict.get(key))
        final_totals[boss].append(ft)
    return dict(final_totals)


def view_raid(request, raid_id):
    raid = Raid.objects.get(raid_id=raid_id)
    fights = Fight.objects.filter(raid=raid)
    score_objs = RaidScore.objects.filter(fight__in=fights).select_subclasses()
    players = {score_obj.player for score_obj in score_objs}
    avg_scores = _get_avg_scores(score_objs)
    sorted_scores = _sort_avg_scores(avg_scores)
    final_totals = _get_totals(score_objs)

    return render(request, "raid_view.html", {"players": players, "score_objs": score_objs,
                                              "avg_scores": sorted_scores, "final_totals": final_totals})


def _get_totals_for_player(score_objs):
    totals = defaultdict(int)
    if len(score_objs) <= 0:
        return totals
    for key in score_objs[0].table_keys:
        for score_obj in score_objs:
            totals[key] += score_obj.score_dict.get(key, 0)
    for score_obj in score_objs:
        totals["Total"] += score_obj.total
    return totals


def view_player_details_for_raid(request, raid_id, player_id, boss_id):
    player = Player.objects.get(id=player_id)
    raid = Raid.objects.get(raid_id=raid_id)
    boss = Boss.objects.get(boss_id=boss_id)
    fights = Fight.objects.filter(raid=raid, boss=boss)
    score_objs = RaidScore.objects.filter(player=player, fight__in=fights).order_by("fight__fight_id").select_subclasses()
    total_list = [score.total for score in score_objs]
    health_list = [score.fight.percent for score in score_objs]
    totals = _get_totals_for_player(score_objs)

    context = {"player": player, "score_objs": score_objs, "totals": total_list,
               "health": health_list, "total_dict": totals}
    return render(request, "player_raid_view.html", context)


def view_player_death_count_times(request, raid_id):
    wcl_client = WCLRequests(raid_id)
    wcl_fights = wcl_client.get_fights()
    death_counts = defaultdict(int)
    first_three = []
    for index, fight in wcl_fights.items():
        first_three_fight = [player for player in
                             wcl_client.get_death_order(fight, actors_obj_dict={player.id: player for player in fight.players})
                             if player][:3]
        first_three.append(first_three_fight)
        for player in first_three_fight:
            death_counts[player] += 1
    sorted_deaths = sorted([(player, death_count) for (player, death_count) in death_counts.items()],
                           key=lambda x: x[1], reverse=True)
    context = {"death_counts": sorted_deaths, "first_three": first_three}
    return render(request, "death_order.html", context)

@login_required
def parse_raid(request):
    return render(request, 'parse.html', {})


def view_parse_progress(request, raid_id):
    task = AsyncResult(raid_id)
    logger.info(task.result)
    logger.info(task.status)
    if task.result:
        data = task.result
    elif task.successful():
        data = {"process_percent": 100}
    else:
        data = {"process_percent": 0}
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')

@login_required
def parse_raid_legacy(request, raid_id):
    group = None
    parse_raid_task(raid_id, request.user.id, group, overwrite=True, update_progress=False)
    return render(request, 'parse.html', {})

@login_required
def start_parse(request):
    if request.method == 'POST':
        raid_id = request.POST.get("raid_id")
        try:
            group = request.POST.get("group")
        except Exception:
            group = None
        parse_task.apply_async((raid_id, request.user.id, group), task_id=raid_id)
        return HttpResponse({}, content_type='application/json')


def change_log(request):
    return render(request, 'change_log.html')

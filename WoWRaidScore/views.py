# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from celery.result import AsyncResult
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

import json
import logging

from WoWRaidScore.models import Raid, Fight, RaidScore, Player, Boss, FightEvent
from WoWRaidScore.tasks import parse_task, parse_raid_task, update_raid_to_current, update_raid_task
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


def _get_totals(score_objs):
    totals = defaultdict(lambda: defaultdict(int))
    keys_dict = {}
    final_totals = defaultdict(list)
    for score_obj in score_objs:
        for name, val in score_obj.score_dict.items():
            if score_obj.fight.boss not in keys_dict:
                keys_dict[score_obj.fight.boss] = score_obj.table_keys
            totals[score_obj.fight.boss][name] += val
    for boss, score_dict in totals.items():
        for key in keys_dict.get(boss):
            final_totals[boss].append((key, totals[boss][key]))
    return dict(final_totals)


def view_raid(request, raid_id):
    raid = Raid.objects.get(raid_id=raid_id)
    fights = Fight.objects.filter(raid=raid)
    score_objs = RaidScore.objects.filter(fight__in=fights).select_subclasses()
    players = {score_obj.player for score_obj in score_objs}
    avg_scores = _get_avg_scores(score_objs)
    sorted_scores = defaultdict(list)
    for boss, score_dict in avg_scores.items():
        sorted_scores[boss] = sorted(sorted([(score, player, boss) for player, score in score_dict.items()], reverse=False, key=lambda x: x[1].name), key=lambda x: x[0], reverse=True)

    final_totals = _get_totals(score_objs)
    bosses = sorted(list({score_obj.fight.boss for score_obj in score_objs}), key=lambda boss: boss.ordering)

    return render(request, "raid_view.html", {"players": players, "score_objs": score_objs, "boss_order": bosses,
                                              "avg_scores": sorted_scores, "final_totals": final_totals, "raid": raid})


def player_overview(request, player_id):
    player = Player.objects.get(id=player_id)
    scores = RaidScore.objects.filter(player=player).select_subclasses()
    sorted_scores = {}
    dates = set()
    for score in scores:
        try:
            if not score.fight:
                continue
        except ObjectDoesNotExist:
            continue
        date = score.fight.raid.time
        dates.add(date)
        if score.fight.boss not in sorted_scores:
            sorted_scores[score.fight.boss] = {}
        if date not in sorted_scores[score.fight.boss]:
            sorted_scores[score.fight.boss][date] = []
        sorted_scores[score.fight.boss][date].append(score.total)

    new_sort = {}
    start_date = min(dates)
    end_date = max(dates)
    # dates = [(start_date + datetime.timedelta(days=x)) for x in range(0, (end_date - start_date).days)]
    dates = sorted(dates)

    for boss, date_scores in sorted_scores.items():
        for date in dates:
            if boss not in new_sort:
                new_sort[boss] = []
            if date not in date_scores:
                new_sort[boss].append(None)
            else:
                new_sort[boss].append(sum(date_scores[date]) / len(date_scores[date]))
    dates = [d.strftime("%Y-%m-%d") for d in dates]

    return render(request, "player_overview_view.html", {"player": player, "scores": new_sort, "dates": dates})


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
    events = FightEvent.objects.filter(fight__in=fights, player=player)

    context = {"player": player, "score_objs": score_objs, "totals": total_list, "base_score_total": sum([score.base_score for score in score_objs]),
               "health": health_list, "total_dict": totals, "events": events, "score_tooltips": score_objs[0].score_description}
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
    print("Starting parsing {}".format(raid_id))
    parse_raid_task(raid_id, request.user.id, group, overwrite=True, update_progress=False)
    print("Finished.")
    return render(request, 'parse.html', {})


@login_required
def update_raid_legacy(request, raid_id):
    group = None
    print("Starting to update {}".format(raid_id))
    update_raid_to_current(raid_id, request.user.id, group)
    print("Finished.")
    return render(request, 'parse.html', {})


@login_required
def start_parse(request):
    if request.method == 'POST':
        raid_id = request.POST.get("raid_id")
        try:
            group = request.POST.get("group")
        except Exception:
            group = None
        parse_task.apply_async(kwargs={"raid_id": raid_id, "user": request.user.id, "group": group}, task_id=raid_id)
        return HttpResponse({"test": request.user.id}, content_type='application/json')

@login_required
def live_parse(request):
    if request.method == 'POST':
        raid_id = request.POST.get("raid_id")
        try:
            group = request.POST.get("group")
        except Exception:
            group = None
        task = AsyncResult(raid_id)
        if task is None or task.ready():
            update_raid_task.apply_async(kwargs={"raid_id": raid_id, "user": request.user.id, "group": group}, task_id=raid_id)
        return HttpResponse({"test": request.user.id}, content_type='application/json')


def change_log(request):
    return render(request, 'change_log.html')

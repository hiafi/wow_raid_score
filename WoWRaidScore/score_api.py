# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from celery.result import AsyncResult
from collections import defaultdict

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

import json
import logging

from WoWRaidScore.models import Raid, Fight, RaidScore, Player, Boss, FightEvent, Group
from WoWRaidScore.tasks import parse_task, parse_raid_task, update_raid_to_current, update_raid_task
from WoWRaidScore.wcl_utils.wclogs_requests import WCLRequests

logger = logging.getLogger(__name__)


def group_overview(request, group_id):
    boss_id = request.GET.get("boss_id")
    group = Group.objects.get(id=group_id)
    raids = Raid.objects.filter(group=group)
    output = defaultdict(dict)
    for raid in raids:
        raid_scores = defaultdict(list)
        fights = Fight.objects.filter(raid=raid, boss__id=boss_id)
        for fight in fights:
            scores = RaidScore.objects.filter(fight=fight).select_subclasses()
            for score in scores:
                raid_scores[score.player.safe_name].append(score.total)
        for player, scores in raid_scores.items():
            output[player][raid.time.strftime("%Y-%m-%d")] = sum(scores) / len(scores)

    return HttpResponse(json.dumps({
        "dates": sorted([r.time.strftime("%Y-%m-%d") for r in raids]),
        "scores": output
    }), content_type='application/json')


def get_bosses(request, zone_id):

    return HttpResponse(json.dumps([
        {
            "name": b.name,
            "id": b.id,
            "order": b.ordering,
        } for b in Boss.objects.filter(zone_id=zone_id).order_by("ordering")]),
    content_type='application/json')



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
    # dates = [(start_date + datetime.timedelta(days=x)) for x in range(0, (end_date - start_date).days)]
    dates = sorted(dates)

    for boss, date_scores in sorted_scores.items():
        boss_key = boss.name
        for date in dates:
            if boss_key not in new_sort:
                new_sort[boss_key] = []
            if date not in date_scores:
                new_sort[boss_key].append(None)
            else:
                new_sort[boss_key].append(sum(date_scores[date]) / len(date_scores[date]))
    dates = [d.strftime("%Y-%m-%d") for d in dates]

    json_data = json.dumps({
        "dates": dates,
        "data": new_sort
    })

    return HttpResponse(json_data, content_type='application/json')


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
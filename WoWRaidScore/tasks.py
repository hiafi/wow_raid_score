from celery import shared_task, current_task
from WoWRaidScore.wcl_utils.wclogs_requests import WCLRequests
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from WoWRaidScore.common.analyzer_builder import build_analyzers
from WoWRaidScore.models import Raid, Fight, RaidScore, Group


@shared_task()
def parse_task(raid_id, user, group):
    parse_raid_task(raid_id, user, group)


@shared_task()
def update_raid_task(raid_id, user, group):
    update_raid_to_current(raid_id, user, group)


def update_status(progress, update_progress=True):
    if update_progress:
        current_task.update_state(state='PROGRESS', meta={'process_percent': progress})


def get_progress(current_analyzer, num_analyzers, percentage_start):
    return int(float(current_analyzer) / num_analyzers * percentage_start)


def parse_raid_task(raid_id, user_id, group_id, overwrite=True, update_progress=True):
    user = User.objects.get(id=user_id)
    if group_id:
        group = Group.objects.get(id=group_id)
    else:
        group = None
    wcl_client = WCLRequests(raid_id)
    update_status(0.0, update_progress)
    try:
        raid = Raid.objects.get(raid_id=raid_id)
        if overwrite:
            for fight in Fight.objects.filter(raid=raid):
                for raid_score in RaidScore.objects.filter(fight=fight):
                    raid_score.delete()
                fight.delete()
        else:
            raise Exception("The raid has already been parsed")
    except ObjectDoesNotExist:
        wcl_raid = wcl_client.get_raid_info()
        raid = Raid(raid_id=raid_id, time=wcl_raid.start_time, user=user, group=group)
        raid.save()
    update_status(2.0, update_progress)
    fights = wcl_client.get_fights()
    update_status(5.0, update_progress)
    analyzers = build_analyzers(fights, raid, wcl_client)
    update_status(10.0, update_progress)
    num_analyzers = len(analyzers)
    for index, analyzer in enumerate(analyzers):
        analyzer.analyze()
        progress = 10.0 + get_progress(index, num_analyzers, 90.0)
        update_status(progress, update_progress)


def update_raid_to_current(raid_id, user_id, group_id, update_progress=True):
    update_status(0, update_progress)
    try:
        raid = Raid.objects.get(raid_id=raid_id)
    except ObjectDoesNotExist:
        raise Exception("Raid has not been created")
    wcl_client = WCLRequests(raid_id)
    wcl_fights = {f.id: f for f in wcl_client.get_fights().values()}
    to_process = set(wcl_fights.values())
    for fight_obj in Fight.objects.filter(raid=raid):
        to_process.remove(wcl_fights.get(fight_obj.fight_id))

    analyzers = build_analyzers({f.id: f for f in to_process}, raid, wcl_client)
    num_analyzers = len(analyzers)
    for index, analyzer in enumerate(analyzers):
        analyzer.analyze()
        progress = get_progress(index, num_analyzers, 100.0)
        update_status(progress, update_progress)


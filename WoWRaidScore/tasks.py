from celery import shared_task, current_task
from WoWRaidScore.wcl_utils.wclogs_requests import WCLRequests
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from WoWRaidScore.common.analyzer_builder import build_analyzers
from WoWRaidScore.models import Raid, Fight, RaidScore, Group, FightEvent


@shared_task()
def parse_task(raid_id, user, group):
    parse_raid_task(raid_id, user, group)


@shared_task()
def update_raid_task(raid_id, user, group):
    update_raid_to_current(raid_id, user, group)


def update_status(progress, update_progress=True, state="", message=""):
    if update_progress:
        current_task.update_state(state='PROGRESS', meta={'process_percent': progress, "message": message})


def get_progress(current_analyzer, num_analyzers, percentage_start):
    return int(float(current_analyzer) / max(num_analyzers, 1) * percentage_start)


def _get_raid_obj(wcl_client, raid_id, user_id, group_id, delete_fights, overwrite):
    user = User.objects.get(id=user_id)
    if group_id:
        group = Group.objects.get(id=group_id)
    else:
        group = None
    try:
        raid = Raid.objects.get(raid_id=raid_id)
        if delete_fights:
            if overwrite:
                for fight in Fight.objects.filter(raid=raid):
                    for raid_score in RaidScore.objects.filter(fight=fight):
                        raid_score.delete()
                    for event in FightEvent.objects.filter(fight=fight):
                        event.delete()
                    fight.delete()

            else:
                raise Exception("The raid has already been parsed")
    except ObjectDoesNotExist:
        wcl_raid = wcl_client.get_raid_info()
        raid = Raid(raid_id=raid_id, time=wcl_raid.start_time, user=user, group=group)
        raid.save()
    return raid


def parse_raid_task(raid_id, user_id, group_id, overwrite=True, update_progress=True):
    wcl_client = WCLRequests(raid_id)
    update_status(0.0, update_progress, message="Getting Raid Data")
    raid = _get_raid_obj(wcl_client, raid_id, user_id, group_id, delete_fights=True, overwrite=overwrite)
    update_status(2.0, update_progress, message="Getting Fights")
    fights = wcl_client.get_fights()
    update_status(5.0, update_progress, message="Building Analyzers")
    analyzers = build_analyzers(fights, raid, wcl_client)
    update_status(10.0, update_progress, message="Processing Fights")
    num_analyzers = len(analyzers)
    try:
        for index, analyzer in enumerate(analyzers):
            analyzer.analyze()
            progress = 10.0 + get_progress(index, num_analyzers, 90.0)
            update_status(progress, update_progress, message="Processing Fights")
    except Exception:
        update_status(99.0, message="Unexpected Error")


def update_raid_to_current(raid_id, user_id, group_id, update_progress=True):
    update_status(0, update_progress)
    wcl_client = WCLRequests(raid_id)
    raid = _get_raid_obj(wcl_client, raid_id, user_id, group_id, delete_fights=False, overwrite=False)

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


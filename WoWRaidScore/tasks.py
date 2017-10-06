from celery import shared_task, current_task
from WoWRaidScore.wcl_utils.wclogs_requests import WCLRequests
from django.core.exceptions import ObjectDoesNotExist

from WoWRaidScore.common.analyzer_builder import build_analyzers
from WoWRaidScore.models import Raid, Fight, RaidScore

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task()
def parse_task(raid_id):
    parse_raid_task(raid_id)

def update_status(progress, update_progress=True):
    if update_progress:
        current_task.update_state(state='PROGRESS', meta={'process_percent': progress})


def get_progress(current_analyzer, num_analyzers):
    return int(float(current_analyzer) / num_analyzers * 90.0)


def parse_raid_task(raid_id, update_progress=True):
    wcl_client = WCLRequests(raid_id)
    update_status(0.0, update_progress)
    try:
        raid = Raid.objects.get(raid_id=raid_id)
        for fight in Fight.objects.filter(raid=raid):
            for raid_score in RaidScore.objects.filter(fight=fight):
                raid_score.delete()
            fight.delete()
    except ObjectDoesNotExist:
        wcl_raid = wcl_client.get_raid_info()
        raid = Raid(raid_id=raid_id, time=wcl_raid.start_time)
        raid.save()
    update_status(2.0, update_progress)
    fights = wcl_client.get_fights()
    update_status(5.0, update_progress)
    analyzers = build_analyzers(fights, raid, wcl_client)
    update_status(10.0, update_progress)
    num_analyzers = len(analyzers)
    for index, analyzer in enumerate(analyzers):
        analyzer.analyze()
        progress = 10.0 + get_progress(index, num_analyzers)
        update_status(progress, update_progress)




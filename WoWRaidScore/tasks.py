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


def parse_raid_task(raid_id):
    wcl_client = WCLRequests(raid_id)
    progress = 0.0
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
    progress = 10.0
    fights = wcl_client.get_fights()
    analyzers = build_analyzers(fights, raid, wcl_client)
    num_analyzers = len(analyzers)
    for index, analyzer in enumerate(analyzers):
        analyzer.analyze()
        current_task.update_state(state='PROGRESS', meta={'process_percent': num_analyzers})



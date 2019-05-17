from django.core.management.base import BaseCommand, CommandError

from WoWRaidScore.models import Raid, Group
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Assign all of the raids to MYA'

    def handle(self, *args, **options):
        raids = Raid.objects.all()
        group = Group.objects.get(id=1)
        for raid in raids:
            raid.group = group
            raid.save()

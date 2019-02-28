from django.core.management.base import BaseCommand, CommandError

from WoWRaidScore.models import Raid, Fight, RaidScore, Player, Boss, FightEvent
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        date_to_prune = datetime.now() - timedelta(days=180)
        fights = Fight.objects.filter(date_parsed__lte=date_to_prune)
        raids = set()
        score_objs = RaidScore.objects.filter(fight__in=fights).order_by().select_subclasses()

        self.stdout.write("Deleting score objects ({})".format(len(score_objs)))
        for so in score_objs:
            so.delete()

        self.stdout.write("Deleting fights")
        for fight in fights:
            raids.add(fight.raid)
            fight.delete()

        self.stdout.write("Deleting raids")
        for raid in raids:
            raid.delete()

        self.stdout.write(self.style.SUCCESS('Successfully purged fights before {}'.format(date_to_prune)))

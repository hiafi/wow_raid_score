from django.conf.urls import url

from . import views
from . import score_api

urlpatterns = [
    url(r'^changelog\/$', views.change_log, name="change_log"),
    url(r'^parse\/status\/(?P<raid_id>\w+)\/$', views.view_parse_progress, name="parse_progress"),
    url(r'^parse\/start\/$', views.start_parse, name="start_parse"),
    url(r'^parse\/live\/$', views.live_parse, name="live_parse"),
    url(r'^parse\/$', views.parse_raid),
    url(r'^parse_legacy\/(?P<raid_id>\w+)\/(?P<group_id>\d+)\/$', views.parse_raid_legacy),
    url(r'^parse_live_legacy\/(?P<raid_id>\w+)\/$', views.update_raid_legacy),
    url(r'^raids\/(?P<raid_id>\w+)\/(?P<player_id>[0-9]+)\/(?P<boss_id>[0-9]+)\/$', views.view_player_details_for_raid,
        name="view_raid_player_details"),
    url(r'^raids\/(?P<raid_id>\w+)\/$', views.view_raid, name="view_raid"),
    url(r'^player\/(?P<player_id>\w+)\/$', views.player_overview, name="player_overview"),
    url(r'^deaths\/(?P<raid_id>\w+)\/$', views.view_player_death_count_times),
    url(r'^raids\/player\/(?P<player_id>\d+)\/$', views.view_raids),
    url(r'^group\/(?P<group_id>\d+)\/$', views.group_overview, name="group_overview"),

    # API
    url(r'^api\/group\/(?P<group_id>\d+)\/$', score_api.group_overview, name="api_group_overview"),
    url(r'^api\/bosses\/(?P<zone_id>\d+)\/$', score_api.get_bosses, name="get_bosses"),
]

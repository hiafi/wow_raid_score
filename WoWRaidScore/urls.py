from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^changelog\/$', views.change_log, name="change_log"),
    url(r'^parse\/status\/(?P<raid_id>\w+)\/$', views.view_parse_progress, name="parse_progress"),
    url(r'^parse\/start\/$', views.start_parse, name="start_parse"),
    url(r'^parse\/$', views.parse_raid),
    url(r'^parse_legacy\/(?P<raid_id>\w+)\/$', views.parse_raid_legacy),
    url(r'^raids\/(?P<raid_id>\w+)\/(?P<player_id>[0-9]+)\/(?P<boss_id>[0-9]+)\/$', views.view_player_details_for_raid, name="view_raid_player_details"),
    url(r'^raids\/(?P<raid_id>\w+)\/$', views.view_raid, name="view_raid"),
    url(r'^deaths\/(?P<raid_id>\w+)\/$', views.view_player_death_count_times),


    url(r'^raids\/player\/(?P<player_id>\d+)\/$', views.view_raids),
]
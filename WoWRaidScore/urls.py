from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^parse\/(?P<raid_id>\w+)\/$', views.parse),
    url(r'^(?P<raid_id>\w+)\/(?P<player_id>[0-9]+)\/(?P<boss_id>[0-9]+)\/$', views.view_player_details_for_raid),
    url(r'^(?P<raid_id>\w+)\/$', views.view_raid),

    url(r'^$', views.view_raids),
]
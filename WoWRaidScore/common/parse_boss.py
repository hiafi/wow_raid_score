from WoWRaidScore.wcl_utils.wclogs_requests import WCLogsRequests


def create_fight_objs(raid_id):
    WCLogsRequests.get_fights(raid_id)
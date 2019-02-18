import calendar
from datetime import datetime


def convert_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp / 1000.0)


def convert_time_to_timestamp(time):
    return calendar.timegm(time.timetuple()) * 1000


def get_readable_time(timestamp, start_of_fight):
    time_dur = (timestamp - start_of_fight) / 1000
    return int(time_dur / 60), time_dur % 60

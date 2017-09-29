import calendar
from datetime import datetime


def convert_timestamp(timestamp):
    return datetime.utcfromtimestamp(timestamp / 1000.0)


def convert_time_to_timestamp(time):
    return calendar.timegm(time.timetuple()) * 1000

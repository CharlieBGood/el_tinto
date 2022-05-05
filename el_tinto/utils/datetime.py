from datetime import datetime, tzinfo
from dateutil import tz
import pytz

def convert_ut_to_local_datetime(utc_time):
    utc_datetime = utc_time.replace(tzinfo=pytz.UTC)
    local_zone = tz.tzlocal()
    local_datetime = utc_datetime.astimezone(local_zone)
    
    return local_datetime

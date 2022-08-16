from dateutil.tz import gettz

def convert_utc_to_local_datetime(utc_datetime):
    
    zone = "America/Bogota"

    local_datetime = utc_datetime.astimezone(gettz(zone))
    
    return local_datetime

from dateutil.tz import gettz

from el_tinto.utils.utils import SPANISH_MONTHS_DICT


def convert_utc_to_local_datetime(utc_datetime):
    zone = "America/Bogota"

    local_datetime = utc_datetime.astimezone(gettz(zone))

    return local_datetime


def get_string_date(date):
    string_date = date.strftime("%d de %B del %Y")
    for word in string_date.split(' '):
        if word in SPANISH_MONTHS_DICT.keys():
            spanish_string_date = string_date.replace(word, SPANISH_MONTHS_DICT[word])

    return spanish_string_date

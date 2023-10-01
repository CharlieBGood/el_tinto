from django.conf import settings
from pytz import timezone

from el_tinto.utils.utils import SPANISH_MONTHS_DICT


def convert_datetime_to_local_datetime(datetime, tzinfo=None):
    """
    Convert a datetime object to a datetime object in the provided
    timezone, if no tzinfo is provided, system timezone is used.

    :params:
    datetime: datetime object
    tzinfo: str

    :return:
    local_datetime: datetime object
    """
    zone = tzinfo or settings.TIME_ZONE
    local_datetime = datetime.astimezone(timezone(zone))

    return local_datetime


def get_string_date(date):
    """
    Convert a date into a string in spanish.

    :params:
    date: date object

    :return:
    spanish_string_date: date object
    """
    string_date = date.strftime("%d de %B del %Y")
    for word in string_date.split(' '):
        if word in SPANISH_MONTHS_DICT.keys():
            spanish_string_date = string_date.replace(word, SPANISH_MONTHS_DICT[word])

    return spanish_string_date

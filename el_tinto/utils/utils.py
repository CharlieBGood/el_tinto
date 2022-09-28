import re


def replace_words_in_sentence(sentence, user=None):
    """
    Replace all the words from sentence that match the replacement structure with user info.
    If no user is provided, return the same sentence

    :params:
    sentence: str
    user: User object

    :return:
    sentence: str
    """
    if user:
        matches = re.findall('\{[a-zA-Z_]+\}', sentence)

        for match in matches:
            sentence = replace_word(sentence, match, user)

        sentence = re.sub(' +', ' ', sentence)

        return sentence

    else:
        return sentence


def replace_word(sentence, word, model):
    """
    Replace a word for its model equivalent

    :params:
    sentence: str
    word: str
    model: Model Object

    :return:
    sentence: str
    """
    disallowed_characters = ['{', '}']

    attribute = word

    for character in disallowed_characters:
        attribute = attribute.replace(character, '')

    model_attribute = getattr(model, attribute)

    return sentence.replace(word, model_attribute)


def get_email_headers(headers):
    """
    Get email headers as dict

    :params:
    headers: dict

    :return:
    email_headers: dict
    """

    email_headers = {}

    for header in headers:
        if header['name'] == 'EMAIL-ID':
            email_headers['email_id'] = int(header['value'])
        if header['name'] == 'EMAIL-TYPE':
            email_headers['email_type'] = header['value']
        if header['name'] == 'To':
            email_headers['user_email'] = header['value']

    return email_headers


def get_string_days(numeric_days):
    """
    Get the string value of the days based on its numeric representation

    :params:
    numeric_days: [str]

    :return:
    string_days: str | [str]
    display_type: str
    """

    display_type = 'str'

    if numeric_days == ['0', '1', '2', '3', '4']:
        string_days = 'entre semana'

    elif numeric_days == ['5', '6']:
        string_days = 'los fines de semana'

    elif numeric_days == ['0', '1', '2', '3', '4', '5', '6']:
        string_days = 'todos los días'

    else:

        string_days = [DAY_OF_THE_WEEK_MAP.get(day) for day in numeric_days]

        display_type = 'list'

    return string_days, display_type


def get_email_provider(email):
    """
    Get the email provider of an email

    :params:
    email: str

    :return:
    email_provider: str
    """
    email_provider = email.split('@')[1].split('.')[0].lower()

    if email_provider == 'hotmail':
        email_provider = 'outlook'

    return email_provider


def get_email_provider_link(email, is_mobile, device_family):
    """
    Get the link of the email provider service

    :params:
    email: str
    is_mobile: bool
    device_family: str

    :return:
    email_provider_link: str
    """
    email_provider = get_email_provider(email)

    if is_mobile and device_family == 'iPhone':
        email_provider_link = MOBILE_EMAIL_PROVIDERS.get(email_provider)

    else:
        email_provider_link = EMAIL_PROVIDERS.get(email_provider)
        if email_provider == 'gmail':
            email_provider_link += f'{email}/#search/from%3A%40eltinto.xyz+in%3Aanywhere+newer_than%3A1d'
        elif email_provider == 'yahoo':
            email_provider_link += 'search/keyword=from%253Aeltinto.xyz'

    return email_provider_link


# Constants

EVENT_TYPE_CLICK = 'Click'
EVENT_TYPE_OPEN = 'Open'

EVENT_TYPES = [EVENT_TYPE_CLICK, EVENT_TYPE_OPEN]

DAY_OF_THE_WEEK_MAP = {
    '0': 'lunes',
    '1': 'martes',
    '2': 'miércoles',
    '3': 'jueves',
    '4': 'viernes',
    '5': 'sábado',
    '6': 'domingo'
}

SPANISH_MONTHS_DICT = {
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April': 'Abril',
    'May': 'Mayo',
    'June': 'Junio',
    'July': 'Julio',
    'August': 'Agosto',
    'September': 'Septiembre',
    'October': 'Octubre',
    'November': 'Noviembre',
    'December': 'Diciembre'
}

EMAIL_PROVIDERS = {
    'gmail': 'https://mail.google.com/mail/u/',
    'outlook': 'https://outlook.live.com/mail/0/',
    'yahoo': 'https://mail.yahoo.com/d/'
}

MOBILE_EMAIL_PROVIDERS = {
    'gmail': 'googlegmail://',
    'outlook': 'ms-outlook://',
    'yahoo': 'ymail://'
}

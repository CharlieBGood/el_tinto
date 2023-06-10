import os
import re


def get_env_value():
    """
    Returns the environment on which the code is being executed.
    """
    return 'dev.' if os.getenv('DJANGO_CONFIGURATION') == 'Development' else ''


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
    model: Model Instance Object

    :return:
    sentence: str
    """
    disallowed_characters = ['{', '}']

    attribute = word

    for character in disallowed_characters:
        attribute = attribute.replace(character, '')

    try:
        model_attribute = getattr(model, attribute)

    except AttributeError:
        raise AttributeError(f'Attribute {attribute} does not exist on model {model._meta.model.__name__}')

    return sentence.replace(word, str(model_attribute))


def replace_info_in_share_news_buttons(html, tinto_block_entry):
    """
    Replace the TintoBlockEntry info in the
    share news buttons html

    :params:
    html: str
    tinto_block_entry: TintoBlockEntry Object

    :return:
    html: str
    """
    change_words_dict = {
        '{{env}}': 'dev.' if os.getenv('DJANGO_CONFIGURATION') == 'Development' else '',
        '{{id}}': str(tinto_block_entry.id),
        '{{title}}': tinto_block_entry.tinto_block.title
    }

    for word in change_words_dict.keys():
        html = html.replace(word, change_words_dict[word])

    return html


def replace_gmail_links_color_tinymce(pl, o):
    o.content = o.content.replace("/color: #1155cc;/gi", "")


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


def replace_special_characters_for_url_use(tweet):
    """
    Replace special characters with their corresponding encoding for url use

    :params:
    tweet: str

    :return:
    tweet: str
    """
    for key, val in URL_SPECIAL_CHARACTERS.items():
        tweet = tweet.replace(key, val)

    return tweet


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

URL_SPECIAL_CHARACTERS = {
    ' ': '%20',
    '"': "%22",
    '#': '%23'
}

MILESTONES = {
    1: {"price": "stickers", "price_description": "Stickers de Whatsapp", "pre_price_string": "acceso a", "mail_id": 1562},
    3: {"price": "sunday_email", "price_description": "El Tinto Dominguero", "pre_price_string": "acceso a", "mail_id": 1563},
    5: {"price": "coffee_shop", "price_description": "La Cafeteria (Comunidad)", "pre_price_string": "acceso a", "mail_id": 1564},
    10: {"price": "talks", "price_description": "Charlas con El Tinto", "pre_price_string": "acceso a", "mail_id": 1565},
    17: {"price": "mug", "price_description": "Mug", "pre_price_string": "un", "mail_id": 1566},
    25: {"price": "hat", "price_description": "Gorra", "pre_price_string": "una", "mail_id": 1567},
    50: {"price": "coffee", "price_description": "Bolsa de Café", "pre_price_string": "una", "mail_id": 1568},
}

ONBOARDING_EMAIL_NAME = 'onboarding'
CHANGE_PREFERRED_DAYS = 'change_preferred_days'

UTILITY_MAILS = {
    ONBOARDING_EMAIL_NAME: 1912,
    CHANGE_PREFERRED_DAYS: 1962
}

NEWS_TYPE_CULTURE_ID = 1
NEWS_TYPE_ECONOMICS_ID = 2
NEWS_TYPE_INTERNATIONAL_POLITICS_ID = 3
NEWS_TYPE_NATIONAL_POLITICS_ID = 4
NEWS_TYPE_SPORTS_ID = 5
NEWS_TYPE_INTERNATIONAL_ID = 6
NEWS_TYPE_NATIONAL_ID = 7
NEWS_TYPE_SCIENCE = 8

TINTO_BLOCK_TYPE_NEWS_ID = 1
TINTO_BLOCK_TYPE_INTRO_ID = 2
TINTO_BLOCK_TYPE_ADVERTISEMENT_ID = 3
TINTO_BLOCK_TYPE_RECOMMENDATION_ID = 4
TINTO_BLOCK_TYPE_OTHERS_ID = 5
TINTO_BLOCK_TYPE_COLOMBIANISM_ID = 6

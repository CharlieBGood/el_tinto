import os
import re

from django.conf import settings

from el_tinto.users.models import UserTier


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

    return sentence.replace(word, str(model_attribute), 2)


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

MILESTONES = {
    1: {"prize": "stickers", "prize_description": "Stickers de Whatsapp", "pre_prize_string": "acceso a", "mail_id": 1562},
    3: {"prize": "sunday_email", "prize_description": "El Tinto Dominguero x 6 meses", "pre_prize_string": "acceso a", "mail_id": 1563},
    5: {"prize": "coffee_shop", "prize_description": "La Cafeteria (Comunidad)", "pre_prize_string": "acceso a", "mail_id": 1564},
    10: {"prize": "talks", "prize_description": "Charlas con El Tinto", "pre_prize_string": "acceso a", "mail_id": 1565},
    17: {"prize": "mug", "prize_description": "Mug", "pre_prize_string": "un", "mail_id": 1566},
    25: {"prize": "hat", "prize_description": "Gorra", "pre_prize_string": "una", "mail_id": 1567},
    50: {"prize": "coffee", "prize_description": "Bolsa de Café", "pre_prize_string": "una", "mail_id": 1568},
}

TASTE_CLUB_PRODUCTS = {
    settings.COFFEE_BEAN_STRIPE_CODE: UserTier.TIER_COFFEE_BEAN,
    settings.GROUND_COFFEE_STRIPE_CODE: UserTier.TIER_GROUND_COFFEE,
    settings.TINTO_STRIPE_CODE: UserTier.TIER_TINTO,
    settings.EXPORTATION_COFFEE_STRIPE_CODE: UserTier.TIER_EXPORTATION_COFFEE
}

TASTE_CLUB_TIER_COFFEE_BEAN_WELCOME_MAIL_ID = 2178
TASTE_CLUB_TIER_GROUND_COFFEE_WELCOME_MAIL_ID = 2179
TASTE_CLUB_TIER_TINTO_WELCOME_MAIL_ID = 2180
TASTE_CLUB_TIER_EXPORTATION_COFFEE_WELCOME_MAIL_ID = 2181
TASTE_CLUB_TIER_TINTO_INVITATION_MAIL = 2182
TASTE_CLUB_TIER_EXPORTATION_COFFEE_INVITATION_MAIL = 2183
TASTE_CLUB_BENEFICIARY_CANCELATION_MAIL = 2184
TASTE_CLUB_OWNER_CANCELATION_MAIL = 2185

TASTE_CLUB_TIER_UTILS = {
    UserTier.TIER_COFFEE_BEAN: {
        'welcome_mail': TASTE_CLUB_TIER_COFFEE_BEAN_WELCOME_MAIL_ID, 'sunday_mails': 1, 'invitation_mail': None
    },
    UserTier.TIER_GROUND_COFFEE: {
        'welcome_mail': TASTE_CLUB_TIER_GROUND_COFFEE_WELCOME_MAIL_ID, 'sunday_mails': 2, 'invitation_mail': None
    },
    UserTier.TIER_TINTO: {
        'welcome_mail': TASTE_CLUB_TIER_TINTO_WELCOME_MAIL_ID,
        'sunday_mails': 3,
        'invitation_mail': TASTE_CLUB_TIER_TINTO_INVITATION_MAIL
    },
    UserTier.TIER_EXPORTATION_COFFEE: {
        'welcome_mail': TASTE_CLUB_TIER_EXPORTATION_COFFEE_WELCOME_MAIL_ID,
        'sunday_mails': 5,
        'invitation_mail': TASTE_CLUB_TIER_EXPORTATION_COFFEE_INVITATION_MAIL
    },
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
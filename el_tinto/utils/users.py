import math
import random
import string

from django.db import connection

from el_tinto.mails.models import SentEmails
from el_tinto.users.models import User
from el_tinto.utils.utils import MILESTONES


def create_user_referral_code(user):
    """
    Create a unique user referral code base on its email name without punctuation marks
    and two random alphanumeric values

    :params:
    user: User object

    :return:
    referral_code: str
    """
    user_email_name = user.email.split('@')[0]
    user_email_name_no_marks = user_email_name.translate(str.maketrans('', '', string.punctuation))

    base = user_email_name_no_marks[0:4]

    complement = ''.join(random.choices(string.ascii_letters + string.digits, k=6-len(base)))

    referral_code_exists = False

    while not referral_code_exists:
        referral_code = base + complement

        if User.objects.filter(referral_code=referral_code).exists():
            complement = ''.join(random.choices(string.ascii_letters + string.digits, k=6-len(base)))
        else:
            referral_code_exists = True

    return referral_code.upper()


def calculate_referral_race_parameters(user):
    """
    Calculates in what percentage of the total users the current user is
    based on the amount of users he/she has referred. Also, calculates
    what is the position in the referral race.

    :params:
    user: User object

    :return:
    referred_users_percentage: float
    user_referral_race_position: int
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            select numer_referrals, count(distinct referred_by_id) as numer_users
            from (
              select referred_by_id,
                     count(0) as numer_referrals
              from public.users_user
              where referred_by_id is not null
              group by 1
            ) t0
            group by 1
            order by numer_referrals
        """)

        referred_users_count_list = cursor.fetchall()

    user_referral_count = user.referred_users.count()

    users_gte_current_user = 0
    user_referral_race_position = 1
    total_users = 0

    for referred_users_count in referred_users_count_list:

        if referred_users_count[0] >= user_referral_count:
            users_gte_current_user += referred_users_count[1]

        if referred_users_count[0] > user_referral_count:
            user_referral_race_position += 1

        total_users += referred_users_count[1]

    total_users = total_users if total_users != 0 else 1

    # calculate percentile
    percentile = (users_gte_current_user / total_users) * 100

    return math.ceil(percentile), user_referral_race_position


def get_next_price_info(user):
    """
    Get the information about the next price in the referral hub.

    :params:
    user: User obj

    :retyrn:
    price_description: str
    pre_price_string: str
    missing_referred_users_for_next_price: int

    """
    referral_count = user.referred_users_count

    milestones_list = list(MILESTONES)
    milestones_list.sort()

    for milestone in milestones_list:
        if milestone > referral_count:
            next_milestone = MILESTONES[milestone]
            return (
                next_milestone['price_description'],
                next_milestone['pre_price_string'],
                milestone - referral_count
            )


def get_milestones_status(user):
    """
    Get the status of each milestone. Show whether it has been already obtained or claimed. 
    
    :params:
    user: User obj

    :retyrn:
    milestone_status: dict
    
    """
    milestones_status = dict()

    for milestone in MILESTONES.keys():
        milestones_status[milestone] = {
            "obtained": user.referred_users_count >= milestone,
            "claimed": SentEmails.objects.filter(user=user, mail_id=MILESTONES[milestone]['mail_id']).exists()
        }

    return milestones_status

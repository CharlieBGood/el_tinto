import random
import string

from el_tinto.users.models import User


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
from django.contrib import messages

from functools import wraps


def only_one_instance(admin_action):
    """
    Decorator to make sure only one instance of the object is updated at the time.
    If more than one instance is selected returns an error message.

    :params:
    admin_action: func

    :return:
    inner: func
    """
    @wraps(admin_action)
    def inner(*args, **kwargs):
        if len(args[2]) == 1:
            messages.error(args[1], f"Only one {args[0].model.__name__} at the time is allowed")
        else:
            return admin_action(*args, **kwargs)

    return inner

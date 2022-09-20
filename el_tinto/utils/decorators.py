from django.contrib import messages


def only_one_instance(action_name):
    """
    Decorator to make sure only one instance of the object is updated at the time.
    If more than one instance is selected returns an error message.

    params:
    :action_name: [str]

    return: decorator [func]
    """
    def decorator(admin_action):
        def wrapper(*args, **kwargs):
            if len(args[2]) > 1:
                messages.error(args[1], "Only one email at the time is allowed")
            else:
                return admin_action(*args, **kwargs)

        wrapper.__name__ = action_name
        return wrapper

    return decorator

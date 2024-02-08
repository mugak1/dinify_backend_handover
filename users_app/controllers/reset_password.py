"""
implementation to reset a user's password
"""
from users_app.models import User
from dinify_backend.configs import MESSAGES


def reset_password(username):
    """
    reset a user's password
    """
    # check if the user exists
    if not User.objects.filter(username=username).exists():
        return {
            'status': 400,
            'message': MESSAGES.get('NO_PHONE_NUMBER')
        }

    user = User.objects.get(username=username)
    password = User.objects.make_random_password()
    password = 'password'  # for testing purposes since emails are not sent out
    user.set_password(password)
    user.prompt_password_change = True
    user.save()

    # TODO save the action performed

    #  TODO send out the email with the new password

    return {
        'status': 200,
        'message': MESSAGES.get('OK_PASSWORD_RESET'),
    }

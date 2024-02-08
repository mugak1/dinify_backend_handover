"""
implementation to handle user login i.e. authentication
"""
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from users_app.models import User
from users_app.serializers import SerGetUserProfile
from dinify_backend.configs import MESSAGES


def login(username: str, password: str) -> dict:
    """
    handle the login of a user
    """
    username = username.strip()
    password = password.strip()

    # in case one has supplied the email,
    # then get the corresponding username
    # to use for authentication
    consider_email = User.objects.filter(email=username.lower()).exists()
    if consider_email:
        username = User.objects.get(phone_number=username).username

    # authenticate the user
    username = username.strip()
    auth_user = authenticate(
        username=username,
        password=password
    )

    if auth_user is None:
        failure_reason = "Invalid password"
        # check if the username exists
        if not User.objects.filter(username=username).exists():
            failure_reason = "No matching username"
            return {
                'status': 401,
                'message': MESSAGES.get('NO_USERNAME')
            }
        # check if the user account is not active
        if not User.objects.get(username=username).is_active:
            failure_reason = "Account not active"
            # TODO save to indicate that the user account is not active
            return {
                'status': 401,
                'message': MESSAGES.get('ACCOUNT_NOT_ACTIVE')
            }
        # TODO save to the action log indicating that the user failed to login

        return {
            'status': 401,
            'message': MESSAGES.get('WRONG_PASSWORD')
        }

    # when the login is successful
    auth_user = User.objects.get(username=username)
    auth_user.last_login = timezone.now()
    auth_user.save()
    token = RefreshToken.for_user(auth_user)

    # TODO save action

    return {
        'status': 200,
        'message': MESSAGES.get('OK_LOGIN'),
        'data': {
            'token': str(token.access_token),
            'refresh': str(token),
            'profile': SerGetUserProfile(auth_user).data
        }
    }

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from users_app.controllers.self_register import self_register


class UsersAuthenticationEndpoint(APIView):
    """
    endpoint for authenticating users
    """
    permission_classes = (AllowAny,)

    def post(self, request, action):
        """
        handle the POST method
        """

        if action == 'register':
            response = self_register(
                request.data
            )
            return Response(
                response,
                status=response['status']
            )

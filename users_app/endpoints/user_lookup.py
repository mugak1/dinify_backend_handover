from rest_framework.response import Response
from rest_framework.views import APIView
from users_app.models import User


class UserLookupEndpoint(APIView):
    def get(self, request):
        try:
            # TODO internationalise the phone number
            phone_number = request.GET.get('phone')
            user = User.objects.values('id', 'phone_number').get(
                phone_number=phone_number
            )
            response = {
                'status': 200,
                'message': 'User found',
                'data': {
                    'id': str(user.get('id'))
                }
            }
            return Response(response, status=200)
        except Exception as error:
            print(f"Error while looking up user: {error}")
            response = {
                'status': 400,
                'message': 'User not found'
            }
            return Response(response, status=200)

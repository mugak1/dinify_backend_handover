from rest_framework.response import Response
from rest_framework.views import APIView
from notifications_app.controllers.notifications import (
    get_notifications, flag_notification_as_read
)


class NotificationsEndpoint(APIView):
    def get(self, request):
        notifications = get_notifications(
            email=request.user.email,
            phone=request.user.phone_number,
            skip_read=request.query_params.get('skip_read', False),
            skip_archived=request.query_params.get('skip_archived', True)
        )
        response = {
            'status': 200,
            'message': "Successfully retrieved the notifications",
            'data': notifications
        }
        return Response(response, status=200)

    def put(self, request):
        flagged = flag_notification_as_read(request.data['notification_id'])
        response = {
            'status': 200 if flagged else 400,
            'message': "Successfully flagged the notification as read" if flagged else "Failed to flag the notification as read"  # noqa
        }
        return Response(response, status=response['status'])

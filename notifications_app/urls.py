from django.urls import path
from notifications_app.endpoints.notifications import NotificationsEndpoint

urlpatterns = [
    path('', NotificationsEndpoint.as_view()),
]

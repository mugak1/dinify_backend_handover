from django.urls import path
from users_app.endpoints.auth import UsersAuthenticationEndpoint

urlpatterns = [
    path('auth/<str:action>/', UsersAuthenticationEndpoint.as_view()),
]

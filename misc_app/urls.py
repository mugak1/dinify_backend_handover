from django.urls import path
from misc_app.endpoints.health import HealthCheckView

urlpatterns = [
    path('', HealthCheckView.as_view()),
]

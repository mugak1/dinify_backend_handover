from django.urls import path
from restaurants_app.endpoints.restaurant_setup import RestaurantSetupEndpoint
from restaurants_app.endpoints.misc_public import MiscPublicEndpoint


urlpatterns = [
    path('<str:config_detail>/', RestaurantSetupEndpoint.as_view()),
    path('misc-public/<str:config_detail>/', MiscPublicEndpoint.as_view()),
]

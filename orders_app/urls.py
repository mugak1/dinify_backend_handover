from django.urls import path
from orders_app.endpoints.orders import OrdersEndpoint
from restaurants_app.endpoints.order_journey import OrderJourneyEndpoint


urlpatterns = [
    path('<str:action>/', OrdersEndpoint.as_view()),
    path('journey/<str:stage>/', OrderJourneyEndpoint.as_view())
]

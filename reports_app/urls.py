from django.urls import path
from reports_app.endpoints.restaurant_reports import RestaurantReportsEndpoint
from reports_app.endpoints.dinify_reports import DinifyReportsEndpoint


urlpatterns = [
    path('restaurant/<str:report_name>/', RestaurantReportsEndpoint.as_view()),
    path('dinify/<str:report_name>/', DinifyReportsEndpoint.as_view())
]

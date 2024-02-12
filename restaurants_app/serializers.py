"""
the serializers for the restaurant app
"""
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from restaurants_app.models import Restaurant, RestaurantEmployee


class SerializerPutRestaurant(ModelSerializer):
    """
    seriailizer for adding and editing restaurant details
    """
    class Meta:
        """
        the meta class for the serializers
        """
        model = Restaurant
        fields = '__all__'


class SerializerPutRestaurantEmployee(ModelSerializer):
    """
    serializer for adding and editing restaurant employees
    """
    class Meta:
        model = RestaurantEmployee
        fields = '__all__'

        
"""
serializers for the users_app
"""
from rest_framework.serializers import SerializerMethodField, ModelSerializer
from users_app.models import User


class SerGetUserProfile(ModelSerializer):
    """
    the serializer for the user profile
    """
    class Meta:
        """
        the metadata for the serializer
        """
        model = User
        fields = [
            'id', 'first_name', 'last_name',
            'email', 'phone_number', 'country', 'roles'
        ]

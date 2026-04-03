"""
serializers for the users_app
"""
from rest_framework.serializers import SerializerMethodField, ModelSerializer
from users_app.models import User
from restaurants_app.models import RestaurantEmployee


class SerGetUserProfile(ModelSerializer):
    """
    the serializer for the user profile
    """
    restaurant_roles = SerializerMethodField()

    class Meta:
        """
        the metadata for the serializer
        """
        model = User
        fields = [
            'id', 'first_name', 'last_name',
            'email', 'phone_number', 'country', 'roles',
            'prompt_password_change', 'restaurant_roles'
        ]

    def get_restaurant_roles(self, user):
        if 'restaurant_roles' in self.context:
            return self.context['restaurant_roles']
        res_roles = RestaurantEmployee.objects.select_related('restaurant').filter(
            restaurant__status__in=['active'],
            user=user,
            deleted=False
        )
        return [
            {
                'restaurant_id': str(res_role.restaurant.id),
                'restaurant': res_role.restaurant.name,
                'roles': res_role.roles
            }
            for res_role in res_roles
        ]


class SerPutUserProfile(ModelSerializer):
    class Meta:
        model = User
        fields = ('__all__')
"""
a user creating a restaurant on their own
"""
from django.db import transaction
from restaurants_app.models import Restaurant
from dinify_backend.configs import MESSAGES, REQUIRED_INFORMATION, ROLES
from restaurants_app.serializers import SerializerPutRestaurant, SerializerPutRestaurantEmployee
from misc_app.controllers.check_required_information import check_required_information


def create_restaurant(data: dict, auth_info: dict) -> dict:
    """
    When a user is creating a restaurant by themselves
    """

    # check that the required information is provided
    info_check = check_required_information(
        REQUIRED_INFORMATION.get('restaurant_registration'),
        data
    )
    if not info_check.get('status'):
        return {
            'status': 400,
            'message': info_check.get('message')
        }

    # check if the user has a restaurant with the same name
    duplicate_name = Restaurant.objects.filter(
        owner=data['owner'],
        name=data['name'].strip().lower()
    )
    if duplicate_name:
        return {
            'status': 400,
            'message': MESSAGES.get('DUPLICATE_RESTAURANT_NAME')
        }

    # construct the info to submit to the database
    record_data = data.copy()
    record_data['name'] = data['name'].strip().title()
    record_data['created_by'] = auth_info['user_id']

    record = SerializerPutRestaurant(data=record_data)
    if record.is_valid():
        with transaction.atomic():
            record.save()

            # save the restaurant-employee mapping
            employee = {
                'user': record.data['owner'],
                'restaurant': record.data['id'],
                'roles': [ROLES.get('RESTAURANT_OWNER')],
                'created_by': auth_info['user_id']
            }
            employee_record = SerializerPutRestaurantEmployee(data=employee)
            if employee_record.is_valid():
                employee_record.save()

                return {
                    'status': 200,
                    'message': MESSAGES.get('OK_CREATE_RESTAURANT'),
                    'data': record.data
                }

            raise Exception('Failed to create restaurant employee')

    # TODO show the actual errors from the serializer
    raise Exception('Something went wrong')

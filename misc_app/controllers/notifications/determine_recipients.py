from dinify_backend.configss.string_definitions import (
    RESTAURANT_OWNER, RESTAURANT_MANAGER
)
from restaurants_app.models import MenuSection, RestaurantEmployee


def determine_receipients(msg_data: dict):
    tos = []
    ccs = []

    print(f"\n\n{msg_data}\n\n")

    if msg_data.get('msg_type') == 'new-menu-section':
        employees = RestaurantEmployee.objects.filter(restaurant_id=msg_data['restaurant_id'])
        owners = [employee.user.email for employee in employees if RESTAURANT_OWNER in employee.roles]
        managers = [employee.user.email for employee in employees if RESTAURANT_MANAGER in employee.roles]
        tos = owners + managers

    return {
        'tos': tos,
        'ccs': ccs
    }

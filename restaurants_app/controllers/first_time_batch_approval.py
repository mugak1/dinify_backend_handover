from typing import Optional
from django.db import transaction
from restaurants_app.models import (
    Restaurant,
    MenuSection,
    SectionGroup,
    MenuItem,
)
from misc_app.controllers.save_action_log import save_action


def first_time_batch_approval(
    restaurant_id: str,
    approval_decision: str,
    auth: dict,
    rejection_reason: Optional[str] = None
) -> dict:
    """
    handling the first time batch approvals
    """
    response = {
        'status': 400,
        'message': 'Sorry an occurred. Please try again later.'
    }

    # TODO check that the user has the necessary rights

    # get the restaurant
    restaurant = Restaurant.objects.get(id=restaurant_id)

    if approval_decision not in ['approve', 'reject']:
        return {
            'status': 400,
            'message': 'Invalid decision. Please try again.'
        }

    with transaction.atomic():
        if approval_decision == 'approve':
            # flag the restaurant detail to indicate that a first time memenu approval has been done
            restaurant.first_time_menu_approval = True
            restaurant.save()

            # bulk update the menu sections
            sections = MenuSection.objects.filter(restaurant=restaurant)
            sections.update(approved=True, enabled=True)

            # bulk update the section groups
            groups = SectionGroup.objects.filter(section__restaurant=restaurant)
            groups.update(approved=True, enabled=True)

            # bulk update the menu items
            items = MenuItem.objects.filter(section__restaurant=restaurant)
            items.update(approved=True, enabled=True)

            response = {
                'status': 200,
                'message': 'The menu has been approved.'
            }

        else:
            # check if one has provided a reason
            if rejection_reason is None:
                return {
                    'status': 400,
                    'message': 'Please provide a reason for rejecting the menu.'
                }

            #  log the reason for not accepting the menu
            save_action(
                affected_model='',
                affected_record='',
                action='Reviewed restaurant menu',
                narration='',
                result='success',
                user_id=auth.get('user_id'),
                username=auth.get('username'),
                submitted_data={
                    'approval_decision': approval_decision,
                    'rejection_reason': rejection_reason,
                },
                changes=None,
                filter_information=None
            )

            # TODO send a notification to the the various personnel who
            # created the menu sections

            response = {
                'status': 200,
                'message': 'Your decision has been acknowledged'
            }
    return response

import logging

from django.db import transaction

from restaurants_app.models import MenuSection
from users_app.controllers.permissions_check import (
    is_dinify_admin,
    get_user_restaurant_roles,
)
from users_app.models import User
from dinify_backend.configss.string_definitions import (
    RESTAURANT_OWNER,
    RESTAURANT_MANAGER,
)


logger = logging.getLogger(__name__)


class ConMenuSection:
    def __init__(self):
        pass

    def reorder_listing(self, ordered_ids: list, user: User) -> dict:
        """
        Reorder menu sections by writing a fresh listing_position to each
        section in the list. The first id in `ordered_ids` becomes position 0,
        the second becomes 1, and so on.

        ordered_ids: list[str] - section UUIDs in the desired final order.
        All ids must belong to the same restaurant, and the user must have
        owner/manager permission on that restaurant.
        """
        if not ordered_ids or not isinstance(ordered_ids, list):
            return {
                'status': 400,
                'message': 'ordered_ids must be a non-empty list of section ids'
            }

        # Reject duplicate ids - the caller is asserting a total ordering, so
        # the same id appearing twice is a malformed request.
        if len(set(str(x) for x in ordered_ids)) != len(ordered_ids):
            return {
                'status': 400,
                'message': 'ordered_ids must not contain duplicate ids'
            }

        sections = list(MenuSection.objects.filter(id__in=ordered_ids))
        if len(sections) != len(ordered_ids):
            return {
                'status': 400,
                'message': 'One or more section ids do not exist'
            }

        restaurant_ids = {str(s.restaurant_id) for s in sections}
        if len(restaurant_ids) != 1:
            return {
                'status': 400,
                'message': 'All sections must belong to the same restaurant'
            }
        restaurant_id = restaurant_ids.pop()

        if not self._user_can_manage_restaurant(user, restaurant_id):
            return {
                'status': 403,
                'message': 'You do not have permission to reorder sections for this restaurant'
            }

        by_id = {str(s.id): s for s in sections}

        with transaction.atomic():
            for index, section_id in enumerate(ordered_ids):
                section = by_id[str(section_id)]
                if section.listing_position != index:
                    section.listing_position = index
                    section.save(update_fields=['listing_position'])

        return {
            'status': 200,
            'message': 'Menu sections reordered successfully'
        }

    @staticmethod
    def _user_can_manage_restaurant(user: User, restaurant_id: str) -> bool:
        if is_dinify_admin(user):
            return True
        roles = get_user_restaurant_roles(
            user_id=str(user.id),
            restaurant_id=restaurant_id,
        )
        return any(role in (RESTAURANT_OWNER, RESTAURANT_MANAGER) for role in roles)

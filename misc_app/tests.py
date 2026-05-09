from django.test import TestCase, RequestFactory
from misc_app.controllers.check_required_information import check_required_information
from misc_app.controllers.secretary import Secretary
from misc_app.controllers.determine_changes import determine_changes
from restaurants_app.serializers import SerializerPutRestaurantEmployee, SerializerPutRestaurant
from restaurants_app.tests import seed_restaurant, TEST_RESTAURANT_NAME
from restaurants_app.models import Restaurant
from dinify_backend.configs import ROLES
from dinify_backend.configss.edit_information import EDIT_INFORMATION
from users_app.tests import seed_user, TEST_PHONE
from users_app.models import User
from misc_app.controllers.notifications.notification import Notification


# Create your tests here.
class MiscAppTestFunctions(TestCase):
    """
    the test functions for the Misc app
    """
    def setUp(self):
        """
        setup the test
        """
        seed_user()
        seed_restaurant(seed_owner=False)

    def test_check_required_information(self):
        """
        test the function to check for required information
        """
        required_information = [
            {
                "key": "key1",
                "label": "Key 1",
                "min_length": 5
            },
            {
                "key": "key2",
                "label": "Key 2",
                "min_length": 5
            }
        ]

        # missing key2
        provided_information1 = {'key1': 'value1'}
        result = check_required_information(
            required_information,
            provided_information1
        )
        self.assertEqual(result['status'], False)

        # all requirements met
        provided_information2 = {
            'key1': 'value1',
            'key2': 'value2'
        }
        result = check_required_information(
            required_information,
            provided_information2
        )
        self.assertEqual(result['status'], True)

        # key2 is not long enough
        provided_information3 = {
            'key1': 'value1',
            'key2': 'valu'
        }
        result = check_required_information(
            required_information,
            provided_information3
        )
        self.assertEqual(result['status'], False)

    def test_secretary(self):
        """
        test the Secretary
        """
        user = User.objects.get(username=TEST_PHONE)
        restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)

        def test_create():
            """
            testing secretary create
            """
            data = {
                'request': None,
                'serializer': SerializerPutRestaurantEmployee,
                'required_information': [],
                'data': {
                    'user': str(user.id),
                    'restaurant': str(restaurant.id),
                    'roles': [ROLES.get('RESTAURANT_OWNER')]
                },
                'user_id': str(User.objects.get(username=TEST_PHONE).id),
                'username': TEST_PHONE,
                'success_message': 'The restaurant employee has been added successfully.',
                'error_message': 'An error occurred while adding the restaurant employee.'
            }
            result = Secretary(data).create()
            self.assertEqual(result.get('status'), 200)

        def test_read():
            """
            testing secretary read
            """
            # test without pagination
            data = {
                'request': None,
                'serializer': SerializerPutRestaurantEmployee,
                'filter': {'deleted': False},
                'paginate': False,
                'user_id': str(user.id),
                'username': TEST_PHONE,
                'success_message': 'Successfully retrieved the restaurant employees.',
                'error_message': 'Error while retrieving the list of restaurant employees.'
            }
            result = Secretary(data).read()
            self.assertEqual(result['status'], 200)

            # test with pagination
            request = RequestFactory().get('/?page=1&page_size=10')
            data = {
                'request': request,
                'serializer': SerializerPutRestaurantEmployee,
                'filter': {'deleted': False},
                'paginate': True,
                'user_id': TEST_PHONE,
                'username': TEST_PHONE,
                'success_message': 'Successfully retrieved the restaurant employees.',
                'error_message': 'Error while retrieving the list of restaurant employees.'
            }
            result = Secretary(data).read()
            self.assertEqual(result.get('status'), 200)
            data = result.get('data')
            self.assertEqual(data.get('pagination').get('page_size'), str(10))

        def test_update():
            """
            test record update
            """
            data = {
                'request': None,
                'serializer': SerializerPutRestaurant,
                'data': {
                    'id': str(restaurant.id),
                    'name': 'new Restaurant name',
                },
                'edit_considerations': EDIT_INFORMATION.get('restaurants'),
                'user_id': str(user.id),
                'username': TEST_PHONE,
                'success_message': 'The details of the restaurant have been updated successfully.',
                'error_message': 'An error occurred while updating the details of the restaurant.'
            }
            result = Secretary(data).update()
            self.assertEqual(result.get('status'), 200)
            restaurant.refresh_from_db()
            self.assertEqual(restaurant.name, 'New Restaurant Name')

        def test_delete():
            """
            test record deletion
            """
            data = {
                'request': None,
                'serializer': SerializerPutRestaurant,
                'data': {
                    'id': str(restaurant.id),
                    'deletion_reason': 'Test deletion'
                },
                'user_id': str(user.id),
                'username': TEST_PHONE,
            }
            result = Secretary(data).delete()
            self.assertEqual(result.get('status'), 200)
            restaurant.refresh_from_db()
            self.assertEqual(restaurant.deleted, True)

        test_create()
        test_read()
        test_update()
        test_delete()

    def test_determine_changes(self):
        """
        test the function to determine changes
        """
        old_data = {
            'name': 'old name',
            'location': 'old location',
        }
        new_data = {
            'name': 'new name',
            'location': 'old location',
        }
        consider = ['name', 'location']
        result = determine_changes({
            'old_info': old_data,
            'new_info': new_data,
            'consider': consider
        })
        self.assertEqual(len(result), 1)

    def test_notification(self):
        """
        test the notification class
        """
        data = {
            'msg_type': 'new-restaurant',
            'first_name': 'John',
            'restaurant_name': 'Test Restaurant'
        }
        notification = Notification(msg_data=data)
        notification.create_notification()
        self.assertIsNotNone(notification)


class SecretaryAbsentVsNullSemanticTests(TestCase):
    """
    Locks in the absent-vs-None contract for Secretary.update():

      - key absent from payload → field is left untouched on the model
      - key present with explicit None → field is cleared on the model

    Pre-fix, secretary.py:316 used `if self.data.get(key) is not None`
    which collapsed both cases into "skip", forcing the Bug 6
    `clear_<field>: true` sentinel workaround. The fix replaces it with
    `if key in self.data` and adds a None-guard around the
    `text_presentation` char block so a null payload to a name/status
    field doesn't blow up `str.title(None)`.
    """

    def setUp(self):
        from decimal import Decimal
        from restaurants_app.models import (
            Restaurant, MenuSection, MenuItem,
        )
        from dinify_backend.configss.string_definitions import (
            RestaurantStatus_Active,
        )
        self.owner = User.objects.create_user(
            first_name='Secretary', last_name='Tester',
            email='secretary_tester@test.com', phone_number='256700000070',
            username='256700000070', country='Uganda', password='password',
            roles=[],
        )
        self.restaurant = Restaurant.objects.create(
            name='Secretary Test Restaurant', location='loc',
            status=RestaurantStatus_Active, owner=self.owner,
        )
        self.section = MenuSection.objects.create(
            name='Mains', restaurant=self.restaurant, listing_position=0,
        )
        self.item = MenuItem.objects.create(
            name='Burger', section=self.section,
            primary_price=Decimal('10.00'),
            calories=200,
            discounted_price=Decimal('5.00'),
            listing_position=0,
        )

    def _menu_item_args(self, data):
        from restaurants_app.serializers import SerializerPutMenuItem
        return {
            'serializer': SerializerPutMenuItem,
            'data': data,
            'edit_considerations': EDIT_INFORMATION.get('menu_item'),
            'user_id': str(self.owner.id),
            'username': self.owner.username,
            'success_message': 'ok',
            'error_message': 'err',
        }

    def test_explicit_null_clears_field(self):
        """Explicit None in payload clears the field (was a no-op pre-fix)."""
        result = Secretary(self._menu_item_args({
            'id': str(self.item.id),
            'calories': None,
        })).update()
        self.assertEqual(result.get('status'), 200)
        self.item.refresh_from_db()
        self.assertIsNone(self.item.calories)

    def test_absent_field_skipped(self):
        """Keys not present in payload leave the model field untouched."""
        result = Secretary(self._menu_item_args({
            'id': str(self.item.id),
            'name': 'Burger Renamed',
        })).update()
        self.assertEqual(result.get('status'), 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.calories, 200)

    def test_text_presentation_guarded_against_null(self):
        """
        Regression guard for the char-block landmine: a null payload to a
        text_presentation-bearing field (e.g. name → str.title) must not
        raise TypeError. Whether the underlying serializer accepts None on
        a non-nullable field is a separate concern; what matters here is
        that Secretary itself doesn't crash before the serializer runs.
        """
        try:
            result = Secretary(self._menu_item_args({
                'id': str(self.item.id),
                'name': None,
            })).update()
        except TypeError as exc:
            self.fail(f"Secretary raised TypeError on null name: {exc}")
        # Whatever the serializer decides (likely 400 validation), the
        # important thing is no exception escaped Secretary.
        self.assertIn(result.get('status'), (200, 400))

    def test_determine_changes_records_null_transitions(self):
        """A null transition is now an audit-log change row."""
        from misc_app.controllers.determine_changes import determine_changes
        old_info = {'name': 'Burger', 'calories': 200}
        new_info = {'name': 'Burger Renamed', 'calories': None}
        changes = determine_changes({
            'old_info': old_info,
            'new_info': new_info,
            'consider': ['name', 'calories'],
        })
        self.assertEqual(len(changes), 2)
        calories_change = next(c for c in changes if c['field'] == 'calories')
        self.assertEqual(calories_change['old_value'], 200)
        self.assertIsNone(calories_change['new_value'])

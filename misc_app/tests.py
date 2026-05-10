from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from misc_app.controllers.check_required_information import check_required_information
from misc_app.controllers.secretary import (
    Secretary, make_notification_for_new_entry,
)
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
            self.assertEqual(data.get('pagination').get('page_size'), 10)

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


class BackendTechDebtBundleTests(TestCase):
    """Regression guards for the DinifyPaginator robustness fixes:
    string-vs-int page coercion and out-of-range graceful handling."""

    def setUp(self):
        self.factory = RequestFactory()

    def _paginate(self, query_string, records):
        from misc_app.controllers.paginator import DinifyPaginator
        request = self.factory.get(f'/?{query_string}')
        return DinifyPaginator({
            'request': request,
            'records': records,
        }).paginate()

    def test_paginator_handles_string_page_param(self):
        # request.GET values are always strings; the paginator must coerce
        # rather than passing the raw string through to Paginator.page().
        records = list(range(1, 11))
        response = self._paginate('page=1&page_size=5', records)
        pagination = response['pagination']
        self.assertEqual(list(response['records']), [1, 2, 3, 4, 5])
        self.assertEqual(pagination['current_page'], 1)
        self.assertEqual(pagination['page_size'], 5)
        self.assertEqual(pagination['number_of_pages'], 2)
        self.assertTrue(pagination['has_next'])
        self.assertFalse(pagination['has_previous'])

    def test_paginator_handles_invalid_page_param(self):
        # ?page=abc previously bubbled a ValueError out of Paginator.page().
        # Should fall back to page 1 instead of 500-ing.
        records = list(range(1, 6))
        response = self._paginate('page=abc&page_size=5', records)
        pagination = response['pagination']
        self.assertEqual(list(response['records']), [1, 2, 3, 4, 5])
        self.assertEqual(pagination['current_page'], 1)

    def test_paginator_handles_out_of_range_page(self):
        # ?page=999 against a 1-page dataset previously raised EmptyPage.
        # Should return an empty records list with the same pagination shape.
        records = list(range(1, 6))
        response = self._paginate('page=999&page_size=5', records)
        pagination = response['pagination']
        self.assertEqual(list(response['records']), [])
        self.assertEqual(pagination['current_page'], 999)
        self.assertEqual(pagination['number_of_pages'], 1)
        self.assertFalse(pagination['has_next'])
        self.assertFalse(pagination['has_previous'])
        self.assertTrue(pagination['paginated'])
        self.assertEqual(pagination['total_records'], 5)


class MsgBuilderContractTests(TestCase):
    """
    Locks in the dual-contract msg_data shape produced by
    `make_notification_for_new_entry`:

      - **Recipient-greeted** (msg_type='new-restaurant-employee'):
        the new entity's owner is the recipient; msg_data carries
        first_name + user_id derived from record.instance.user.
      - **Restaurant-greeted** (default, e.g. 'new-menu-section'):
        the restaurant is the greetee; msg_data carries the actor's
        full name as `user` plus item_name.

    Pre-fix, the helper produced only the restaurant-greeted shape,
    so the restaurant builder's `msg_data['first_name']` lookup raised
    KeyError (silently swallowed) for 'new-restaurant-employee' — and
    the recipient lookup downstream broke too because user_id wasn't
    set. Also pins the msg_builder_menu_groups.py alignment to read
    `item_name` instead of the outlier `group_name`.
    """

    def setUp(self):
        self.actor = User.objects.create_user(
            first_name='Bob', last_name='Actor',
            email='bob_actor@test.com', phone_number='256700000080',
            username='256700000080', country='Uganda', password='password',
            roles=[],
        )
        self.recipient = User.objects.create_user(
            first_name='Alice', last_name='Recipient',
            email='alice_recipient@test.com', phone_number='256700000081',
            username='256700000081', country='Uganda', password='password',
            roles=[],
        )
        self.restaurant = Restaurant.objects.create(
            name='Contract Test Restaurant', location='loc',
            owner=self.actor,
        )

    def _patch_notification(self):
        return patch('misc_app.controllers.secretary.Notification')

    def test_recipient_greeted_contract_for_new_employee(self):
        record = MagicMock()
        record.instance.user = self.recipient
        with self._patch_notification() as mock_notification:
            make_notification_for_new_entry(
                restaurant_id=str(self.restaurant.id),
                user=self.actor,
                item_name=None,
                msg_type='new-restaurant-employee',
                record=record,
            )
        mock_notification.assert_called_once()
        msg_data = mock_notification.call_args.args[0]
        self.assertEqual(msg_data['msg_type'], 'new-restaurant-employee')
        self.assertEqual(msg_data['first_name'], 'Alice')
        self.assertEqual(msg_data['user_id'], str(self.recipient.id))
        self.assertEqual(msg_data['restaurant_name'], 'Contract Test Restaurant')
        self.assertNotIn('user', msg_data)
        self.assertNotIn('item_name', msg_data)

    def test_restaurant_greeted_contract_for_menu_section(self):
        with self._patch_notification() as mock_notification:
            make_notification_for_new_entry(
                restaurant_id=str(self.restaurant.id),
                user=self.actor,
                item_name='Starters',
                msg_type='new-menu-section',
                record=None,
            )
        mock_notification.assert_called_once()
        msg_data = mock_notification.call_args.args[0]
        self.assertEqual(msg_data['msg_type'], 'new-menu-section')
        self.assertEqual(msg_data['user'], 'Bob Actor')
        self.assertEqual(msg_data['item_name'], 'Starters')
        self.assertEqual(msg_data['restaurant_name'], 'Contract Test Restaurant')
        self.assertNotIn('first_name', msg_data)
        self.assertNotIn('user_id', msg_data)

    def test_recipient_greeted_skips_when_record_missing(self):
        with self._patch_notification() as mock_notification, \
                self.assertLogs('misc_app.controllers.secretary', level='WARNING') as logs:
            make_notification_for_new_entry(
                restaurant_id=str(self.restaurant.id),
                user=self.actor,
                item_name=None,
                msg_type='new-restaurant-employee',
                record=None,
            )
        mock_notification.assert_not_called()
        self.assertTrue(any(
            'recipient-greeted contract requires record.instance' in msg
            for msg in logs.output
        ), f"Expected warning not found in: {logs.output}")

    def test_menu_group_uses_item_name(self):
        from misc_app.controllers.notifications.msg_builder_menu_groups import (
            make_menu_group_messages,
        )
        msg_data = {
            'msg_type': 'new-menu-group',
            'restaurant_name': 'Contract Test Restaurant',
            'user': 'Bob Actor',
            'item_name': 'Spicy Sides',
        }
        # Pre-fix this raised KeyError on 'group_name'. Post-fix the
        # builder reads item_name and embeds it in the rendered email.
        message = make_menu_group_messages(msg_data, footer='')
        self.assertIn('Spicy Sides', message['email'])
        self.assertEqual(message['subject'], 'Menu Group Created')

    def test_create_employee_notification_succeeds_end_to_end(self):
        """
        Reproduces the catch-all endpoint flow at
        restaurants_app/endpoints/restaurant_setup.py:596 — POST
        /restaurant-setup/employees/ — which is the user-facing path
        that sets msg_type='new-restaurant-employee' on Secretary args
        and triggers `make_notification_for_new_entry`. Pre-fix this
        raised KeyError('first_name') in
        msg_builder_restaurant.py:65 (silently swallowed by the
        Secretary try/except as ERROR-log noise).
        """
        secretary_args = {
            'serializer': SerializerPutRestaurantEmployee,
            'data': {
                'user': str(self.recipient.id),
                'restaurant': str(self.restaurant.id),
                'roles': [ROLES.get('RESTAURANT_KITCHEN')],
            },
            'required_information': [],
            'user_id': str(self.actor.id),
            'username': self.actor.username,
            'user': self.actor,
            'msg_type': 'new-restaurant-employee',
            'success_message': 'ok',
            'error_message': 'err',
        }
        secretary_logger = 'misc_app.controllers.secretary'
        with self.assertLogs(secretary_logger, level='DEBUG') as captured:
            # Drop a benign DEBUG to satisfy assertLogs (it requires
            # at least one record). Then assert no ERROR records fire
            # — pre-fix the KeyError swallow logged ERROR here.
            import logging
            logging.getLogger(secretary_logger).debug('test marker')
            result = Secretary(secretary_args).create()
        self.assertEqual(result.get('status'), 200)
        error_records = [
            line for line in captured.output
            if line.startswith(f'ERROR:{secretary_logger}')
        ]
        self.assertEqual(
            error_records, [],
            f"Unexpected ERROR log on {secretary_logger}: {error_records}",
        )

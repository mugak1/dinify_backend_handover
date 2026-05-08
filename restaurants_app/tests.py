from cgi import test
from django.db import transaction
from django.test import TestCase
from dinify_backend.configs import ROLES
from dinify_backend.configss.messages import MESSAGES
from dinify_backend.configss.string_definitions import RestaurantStatus_Active
from misc_app.controllers.secretary import Secretary
from users_app.tests import TEST_PHONE, seed_user
from users_app.models import User
from restaurants_app.controllers.create_restaurant import (
    create_restaurant, admin_register_restaurant
)
from restaurants_app.controllers.create_employee import create_employee
from restaurants_app.controllers.menu_sections import ConMenuSection
from restaurants_app.endpoints.restaurant_setup import normalize_ordered_section_ids
from restaurants_app.models import (
    Restaurant, RestaurantEmployee, MenuSection, MenuItem, Table,
    SectionGroup, DiningArea,
)
from users_app.controllers.otp_manager import OtpManager


TEST_RESTAURANT_NAME = 'Seed Test Restaurant'
TEST_MENU_SECTION_NAME = 'Seed Test Menu Section'
TEST_MENU_ITEM1_NAME = 'Seed Test Menu Item1'
TEST_MENU_ITEM2_NAME = 'Seed Test Menu Item2'
TEST_MENU_ITEM3_NAME = 'Seed Test Menu Item3'
TEST_MENU_ITEM4_NAME = 'Seed Test Menu Item4'
TEST_MENU_ITEM5_NAME = 'Seed Test Menu Item5'
TEST_UNAVAILABLE_MENU_ITEM_NAME = 'Seed Unavailable Test Menu Item'
TEST_DISCOUNTED_MENU_ITEM_NAME = 'Seed Test Discounted Menu Item'
TEST_EXTRA_DISCOUNTED_MENU_ITEM_NAME = 'Seed Test Extra Discounted Menu Item'
TEST_OPTION_MENU_ITEM_NAME = 'Seed Test Options Menu Item'
TEST_TABLE_NUMBER1 = 1
TEST_TABLE_NUMBER2 = 2
TEST_TABLE_NUMBER3 = 3
TEST_TABLE_NUMBER4 = 4

TEST_OPTION_GROUP_ID = 'grp-size'
TEST_OPTION_CHOICE_SMALL_ID = 'choice-small'
TEST_OPTION_CHOICE_LARGE_ID = 'choice-large'
TEST_OPTION_CHOICE_SMALL_COST = 1100
TEST_OPTION_CHOICE_LARGE_COST = 1500


def seed_restaurant(seed_owner=True):
    """
    seed the restaurant
    """
    owner = User.objects.get(username=TEST_PHONE)
    with transaction.atomic():
        restaurant = Restaurant.objects.create(
            name=TEST_RESTAURANT_NAME,
            location='Seed Test location',
            owner=owner
        )
        if seed_owner:
            RestaurantEmployee.objects.create(
                user=owner,
                restaurant=restaurant,
                roles=[ROLES.get('RESTAURANT_OWNER')]
            )


def seed_menu_section():
    """
    seed the menu section
    """
    restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)
    MenuSection.objects.create(
        name=TEST_MENU_SECTION_NAME,
        restaurant=restaurant
    )


def seed_menu_items():
    """
    seed menu items to use
    """
    menu_section = MenuSection.objects.get(name=TEST_MENU_SECTION_NAME)
    # bulk create menu items
    menu_items = [
        MenuItem(name=TEST_MENU_ITEM1_NAME, section=menu_section, primary_price=1000.0, discounted_price=900.0, running_discount=False),  # noqa
        MenuItem(name=TEST_MENU_ITEM2_NAME, section=menu_section, primary_price=1000.0, discounted_price=900.0, running_discount=False),  # noqa
        MenuItem(name=TEST_MENU_ITEM3_NAME, section=menu_section, primary_price=1000.0, discounted_price=900.0, running_discount=False),  # noqa
        MenuItem(name=TEST_MENU_ITEM4_NAME, section=menu_section, primary_price=1000.0, discounted_price=900.0, running_discount=False),  # noqa
        MenuItem(name=TEST_MENU_ITEM5_NAME, section=menu_section, primary_price=1000.0, discounted_price=900.0, running_discount=False),  # noqa
        MenuItem(name=TEST_UNAVAILABLE_MENU_ITEM_NAME, section=menu_section, primary_price=1000.0, discounted_price=900.0, running_discount=False, available=False),  # noqa
        MenuItem(name=TEST_DISCOUNTED_MENU_ITEM_NAME, section=menu_section, primary_price=1000.0, discounted_price=900.0, running_discount=True),  # noqa
        MenuItem(
            name=TEST_EXTRA_DISCOUNTED_MENU_ITEM_NAME,
            section=menu_section,
            primary_price=1000.0,
            discounted_price=900.0,
            running_discount=True,
            consider_discount_object=True,
            # CANONICAL discount_details schema (must match restaurants_app/models.py:234-242):
            #   discount_type:        'percentage' | 'fixed'
            #   discount_percentage:  0..100 (subtract this % of primary_price)
            #   discount_amount:      UGX amount to subtract from primary_price
            #   recurring_days:       list[int 1..7] ISO weekday filter
            #   start_date/end_date:  'YYYY-MM-DD' strings, '' for unbounded
            #   start_time/end_time:  'HH:MM' strings, '' for unbounded
            # Never add raw_discount_value / raw_discount_type — those are the
            # pre-0042 buggy schema and were migrated out of all production rows.
            discount_details={
                'recurring_days': [1, 2, 3, 4, 5, 6, 7],
                'start_date': '2021-01-01',
                'end_date': '2030-12-31',
                'start_time': '00:00',
                'end_time': '23:59',
                'discount_percentage': 20.0,
                'discount_amount': 0.0
            }
        ),  # noqa
        MenuItem(
            name=TEST_OPTION_MENU_ITEM_NAME,
            section=menu_section,
            primary_price=1000.0,
            discounted_price=900.0,
            running_discount=True,
            options={
                'hasModifiers': True,
                'groups': [
                    {
                        'id': TEST_OPTION_GROUP_ID,
                        'name': 'Size',
                        'required': True,
                        'selectionType': 'single',
                        'minSelections': 1,
                        'maxSelections': 1,
                        'choices': [
                            {
                                'id': TEST_OPTION_CHOICE_SMALL_ID,
                                'name': 'Small',
                                'additionalCost': TEST_OPTION_CHOICE_SMALL_COST,
                                'available': True
                            },
                            {
                                'id': TEST_OPTION_CHOICE_LARGE_ID,
                                'name': 'Large',
                                'additionalCost': TEST_OPTION_CHOICE_LARGE_COST,
                                'available': True
                            }
                        ]
                    }
                ]
            }
        ),
    ]
    MenuItem.objects.bulk_create(menu_items)


def seed_tables():
    """
    seed the table
    """
    restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)
    Table.objects.create(
        number=TEST_TABLE_NUMBER1,
        restaurant=restaurant,
        prepayment_required=False
    )
    Table.objects.create(
        number=TEST_TABLE_NUMBER2,
        restaurant=restaurant,
        prepayment_required=True
    )
    Table.objects.create(
        number=TEST_TABLE_NUMBER3,
        restaurant=restaurant,
        prepayment_required=True
    )
    Table.objects.create(
        number=TEST_TABLE_NUMBER4,
        restaurant=restaurant,
        prepayment_required=True
    )


# Create your tests here.
class RestaurantAppTestFunctions(TestCase):
    """
    test the functions for restaurant app
    """

    def setUp(self) -> None:
        """
        set up for the tests
        """
        seed_user()
        seed_restaurant()

    def test_create_restaurant(self):
        """
        test the restaurant self register function
        """
        user_id = str(User.objects.get(username=TEST_PHONE).pk)
        auth_info = {
            'user_id': user_id,
            'first_name': 'First',
            'email': 'dummy@email.com'
        }

        def test_missing_info():
            data = {
                'name': 'Test Restaurant',
                'owner': user_id
            }
            result = create_restaurant(data, auth_info)
            self.assertEqual(result['status'], 400)

        def test_ok():
            data = {
                'name': 'Test Restaurant',
                'location': 'Test location',
                'owner': user_id
            }
            result = create_restaurant(data, auth_info)
            self.assertEqual(result['status'], 200)
            self.assertEqual(result['message'], MESSAGES.get('OK_CREATE_RESTAURANT'))

        def test_create_employee():
            restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)
            result = create_employee(
                first_name='Test',
                last_name='Employee',
                email='dummy@email.com',
                phone_number='256777777777',
                restaurant=restaurant,
                roles=[ROLES.get('RESTAURANT_KITCHEN')],
                creator=restaurant.owner,
                skip_otp=True
            )
            print(f'employee result: {result}')
            self.assertEqual(result['status'], 200)

            print('editing the employee')
            employee = RestaurantEmployee.objects.get(
                user__phone_number='256777777777',
                restaurant=restaurant
            )
            # secretary_args = {
            #     'serializer': serializer,
            #     'data': put_data,
            #     'edit_considerations': EDIT_INFORMATION.get('restaurant_employee'),
            #     'user_id': auth['id'],
            #     'username': auth['username'],
            #     'success_message': success_message,
            #     'error_message': error_message
            # }
            
            # Secretary



        test_missing_info()
        test_ok()
        test_create_employee()

    def test_admin_register_restaurant(self):
        user = User.objects.get(username=TEST_PHONE)
        user_id = str(user.pk)
        # get the otp for the user
        # OtpManager().make_otp(user=user)
        auth_info = {
            'user_id': user_id,
            'first_name': 'First',
            'email': 'dummy@email.com'
        }

        data = {
            'name': 'Test Restaurant',
            'location': 'Test location',

            'first_name': 'Test',
            'last_name': 'Owner',
            'email': 'sample@org.org',
            'phone_number': '256777777777',
            'country': 'UG',
            # 'otp': '1234'
        }

        result = admin_register_restaurant(data, auth_info)
        print(f'admin result: {result}')
        self.assertEqual(result['status'], 200)


def _seed_two_sections(restaurant):
    """Helper: seed two sections at positions 0 and 1, return them."""
    s1 = MenuSection.objects.create(
        name='Starters', restaurant=restaurant, listing_position=0,
    )
    s2 = MenuSection.objects.create(
        name='Mains', restaurant=restaurant, listing_position=1,
    )
    return s1, s2


class MenuSectionReorderTests(TestCase):
    """Tests for ConMenuSection.reorder_listing and the dispatch slug."""

    def setUp(self):
        seed_user()
        seed_restaurant()
        self.admin_user = User.objects.get(username=TEST_PHONE)
        self.restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)

    def test_reorder_flips_two_sections(self):
        s1, s2 = _seed_two_sections(self.restaurant)
        result = ConMenuSection().reorder_listing(
            ordered_ids=[str(s2.id), str(s1.id)],
            user=self.admin_user,
        )
        self.assertEqual(result['status'], 200)
        s1.refresh_from_db()
        s2.refresh_from_db()
        self.assertEqual(s2.listing_position, 0)
        self.assertEqual(s1.listing_position, 1)

    def test_reorder_rejects_cross_restaurant(self):
        s1, _ = _seed_two_sections(self.restaurant)
        other_restaurant = Restaurant.objects.create(
            name='Other Restaurant',
            location='elsewhere',
            owner=self.admin_user,
        )
        other_section = MenuSection.objects.create(
            name='Drinks', restaurant=other_restaurant, listing_position=0,
        )
        result = ConMenuSection().reorder_listing(
            ordered_ids=[str(s1.id), str(other_section.id)],
            user=self.admin_user,
        )
        self.assertEqual(result['status'], 400)
        self.assertIn('same restaurant', result['message'])

    def test_reorder_rejects_unknown_id(self):
        s1, _ = _seed_two_sections(self.restaurant)
        bogus_id = '00000000-0000-0000-0000-000000000000'
        result = ConMenuSection().reorder_listing(
            ordered_ids=[str(s1.id), bogus_id],
            user=self.admin_user,
        )
        self.assertEqual(result['status'], 400)

    def test_reorder_rejects_empty_list(self):
        result = ConMenuSection().reorder_listing(
            ordered_ids=[],
            user=self.admin_user,
        )
        self.assertEqual(result['status'], 400)

    def test_reorder_rejects_duplicate_ids(self):
        s1, s2 = _seed_two_sections(self.restaurant)
        result = ConMenuSection().reorder_listing(
            ordered_ids=[str(s1.id), str(s2.id), str(s1.id)],
            user=self.admin_user,
        )
        self.assertEqual(result['status'], 400)
        self.assertIn('duplicate', result['message'])

    def test_reorder_rejects_unauthorized_user(self):
        # User who is neither dinify admin nor owner/manager of the restaurant.
        outsider = User.objects.create_user(
            first_name='No', last_name='Access',
            email='outsider@test.com', phone_number='256700000001',
            username='256700000001', country='Uganda', password='password',
            roles=['diner'],
        )
        s1, s2 = _seed_two_sections(self.restaurant)
        result = ConMenuSection().reorder_listing(
            ordered_ids=[str(s2.id), str(s1.id)],
            user=outsider,
        )
        self.assertEqual(result['status'], 403)

    def test_reorder_allows_owner_role(self):
        # Activate the seeded restaurant so role-lookup matches the
        # `restaurant__status__in=['active']` filter in get_user_restaurant_roles.
        self.restaurant.status = RestaurantStatus_Active
        self.restaurant.save(update_fields=['status'])
        owner = User.objects.create_user(
            first_name='Restaurant', last_name='Owner',
            email='owner@test.com', phone_number='256700000002',
            username='256700000002', country='Uganda', password='password',
            roles=['diner'],
        )
        RestaurantEmployee.objects.create(
            user=owner, restaurant=self.restaurant,
            roles=[ROLES.get('RESTAURANT_OWNER')],
        )
        s1, s2 = _seed_two_sections(self.restaurant)
        result = ConMenuSection().reorder_listing(
            ordered_ids=[str(s2.id), str(s1.id)],
            user=owner,
        )
        self.assertEqual(result['status'], 200)


class NormalizeOrderedSectionIdsTests(TestCase):
    """Unit tests for the legacy/new shape resolver used by the dispatch."""

    def test_new_shape_passes_through(self):
        ids = ['a', 'b', 'c']
        self.assertEqual(
            normalize_ordered_section_ids({'ordered_ids': ids}),
            ids,
        )

    def test_legacy_dict_shape_extracted(self):
        legacy = {
            'ordering': [
                {'id': 'a', 'listing_position': 0},
                {'id': 'b', 'listing_position': 1},
            ],
        }
        self.assertEqual(
            normalize_ordered_section_ids(legacy),
            ['a', 'b'],
        )

    def test_legacy_string_shape_passes_through(self):
        self.assertEqual(
            normalize_ordered_section_ids({'ordering': ['a', 'b']}),
            ['a', 'b'],
        )

    def test_no_payload_returns_none(self):
        self.assertIsNone(normalize_ordered_section_ids({}))


class NewSectionListingPositionTests(TestCase):
    """Tests that a newly-POSTed section gets a clean listing_position."""

    def setUp(self):
        seed_user()
        seed_restaurant()
        self.admin_user = User.objects.get(username=TEST_PHONE)
        self.restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)

    def _post_section(self, name):
        from rest_framework_simplejwt.tokens import RefreshToken
        token = str(RefreshToken.for_user(self.admin_user).access_token)
        return self.client.post(
            f'/api/v1/restaurant-setup/menusections/',
            data={'name': name, 'restaurant': str(self.restaurant.id)},
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    def test_new_section_assigned_next_position(self):
        MenuSection.objects.create(
            name='First', restaurant=self.restaurant, listing_position=0,
        )
        MenuSection.objects.create(
            name='Second', restaurant=self.restaurant, listing_position=1,
        )
        response = self._post_section('Drinks')
        self.assertEqual(response.status_code, 200)
        created = MenuSection.objects.get(name='Drinks', restaurant=self.restaurant)
        self.assertEqual(created.listing_position, 2)

    def test_first_section_assigned_position_zero(self):
        response = self._post_section('Brunch')
        self.assertEqual(response.status_code, 200)
        created = MenuSection.objects.get(name='Brunch', restaurant=self.restaurant)
        self.assertEqual(created.listing_position, 0)


class NewMenuItemListingPositionTests(TestCase):
    """Tests that a newly-POSTed menu item gets a clean listing_position
    relative to the section it's added to."""

    def setUp(self):
        seed_user()
        seed_restaurant()
        seed_menu_section()
        self.admin_user = User.objects.get(username=TEST_PHONE)
        self.section = MenuSection.objects.get(name=TEST_MENU_SECTION_NAME)

    def _post_item(self, name, section_id=None):
        from rest_framework_simplejwt.tokens import RefreshToken
        token = str(RefreshToken.for_user(self.admin_user).access_token)
        return self.client.post(
            f'/api/v1/restaurant-setup/menuitems/',
            data={
                'name': name,
                'section': str(section_id or self.section.id),
                'primary_price': '1000.00',
            },
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    def test_first_item_in_section_gets_position_zero(self):
        response = self._post_item('First Item')
        self.assertEqual(response.status_code, 200)
        created = MenuItem.objects.get(name='First Item', section=self.section)
        self.assertEqual(created.listing_position, 0)

    def test_subsequent_items_assigned_next_position(self):
        MenuItem.objects.create(
            name='Existing 1', section=self.section,
            primary_price=1000, listing_position=0,
        )
        MenuItem.objects.create(
            name='Existing 2', section=self.section,
            primary_price=1000, listing_position=1,
        )
        response = self._post_item('Newcomer')
        self.assertEqual(response.status_code, 200)
        created = MenuItem.objects.get(name='Newcomer', section=self.section)
        self.assertEqual(created.listing_position, 2)

    def test_position_is_per_section_not_per_restaurant(self):
        """A new item in section B should get position 0 even if section A
        has items at higher positions."""
        restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)
        section_b = MenuSection.objects.create(
            name='Second Section', restaurant=restaurant,
        )
        MenuItem.objects.create(
            name='A Item 1', section=self.section,
            primary_price=1000, listing_position=0,
        )
        MenuItem.objects.create(
            name='A Item 2', section=self.section,
            primary_price=1000, listing_position=1,
        )
        response = self._post_item('B First Item', section_id=section_b.id)
        self.assertEqual(response.status_code, 200)
        created = MenuItem.objects.get(name='B First Item', section=section_b)
        self.assertEqual(created.listing_position, 0)


class MenuItemReorderTests(TestCase):
    """Tests for ConMenuItem.reorder_listing — the item-reorder controller."""

    def setUp(self):
        seed_user()
        seed_restaurant()
        seed_menu_section()
        self.admin_user = User.objects.get(username=TEST_PHONE)
        self.restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)
        self.section = MenuSection.objects.get(name=TEST_MENU_SECTION_NAME)

        # Three items in the section, positions 0/1/2.
        self.item_a = MenuItem.objects.create(
            name='Alpha', section=self.section,
            primary_price=1000, listing_position=0,
        )
        self.item_b = MenuItem.objects.create(
            name='Bravo', section=self.section,
            primary_price=1000, listing_position=1,
        )
        self.item_c = MenuItem.objects.create(
            name='Charlie', section=self.section,
            primary_price=1000, listing_position=2,
        )

    def _put_reorder(self, section_id, ordered_ids, user=None):
        from rest_framework_simplejwt.tokens import RefreshToken
        actor = user or self.admin_user
        token = str(RefreshToken.for_user(actor).access_token)
        return self.client.put(
            f'/api/v1/restaurant-setup/reorder-section-items/',
            data={'section_id': str(section_id), 'ordered_ids': ordered_ids},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    def test_reorder_flips_two_items(self):
        # Swap A and C: target order [C, B, A]
        ordered = [str(self.item_c.id), str(self.item_b.id), str(self.item_a.id)]
        response = self._put_reorder(self.section.id, ordered)
        self.assertEqual(response.status_code, 200)
        self.item_a.refresh_from_db()
        self.item_b.refresh_from_db()
        self.item_c.refresh_from_db()
        self.assertEqual(self.item_c.listing_position, 0)
        self.assertEqual(self.item_b.listing_position, 1)
        self.assertEqual(self.item_a.listing_position, 2)

    def test_reorder_rejects_cross_section(self):
        # Create another section with one item; include its id in our reorder.
        other_section = MenuSection.objects.create(
            name='Other', restaurant=self.restaurant,
        )
        other_item = MenuItem.objects.create(
            name='Other Item', section=other_section,
            primary_price=1000, listing_position=0,
        )
        ordered = [
            str(self.item_a.id),
            str(self.item_b.id),
            str(self.item_c.id),
            str(other_item.id),  # belongs to a different section
        ]
        response = self._put_reorder(self.section.id, ordered)
        self.assertEqual(response.status_code, 400)
        # Item C should still have its original position.
        self.item_c.refresh_from_db()
        self.assertEqual(self.item_c.listing_position, 2)

    def test_reorder_rejects_unknown_item_id(self):
        bogus = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
        ordered = [str(self.item_a.id), str(self.item_b.id), bogus]
        response = self._put_reorder(self.section.id, ordered)
        self.assertEqual(response.status_code, 400)

    def test_reorder_rejects_unknown_section_id(self):
        bogus = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
        ordered = [str(self.item_a.id), str(self.item_b.id), str(self.item_c.id)]
        response = self._put_reorder(bogus, ordered)
        self.assertEqual(response.status_code, 404)

    def test_reorder_rejects_empty_list(self):
        response = self._put_reorder(self.section.id, [])
        self.assertEqual(response.status_code, 400)

    def test_reorder_rejects_duplicate_ids(self):
        ordered = [str(self.item_a.id), str(self.item_b.id), str(self.item_a.id)]
        response = self._put_reorder(self.section.id, ordered)
        self.assertEqual(response.status_code, 400)

    def test_reorder_rejects_partial_set(self):
        # Section has three items; sending only two is a partial reorder.
        ordered = [str(self.item_a.id), str(self.item_b.id)]
        response = self._put_reorder(self.section.id, ordered)
        self.assertEqual(response.status_code, 400)
        self.item_a.refresh_from_db()
        self.assertEqual(self.item_a.listing_position, 0)  # unchanged

    def test_reorder_rejects_unauthorized_user(self):
        # Create a user with no restaurant role.
        outsider = User.objects.create(
            username='outsider_phone', first_name='Out', last_name='Sider',
        )
        ordered = [str(self.item_c.id), str(self.item_b.id), str(self.item_a.id)]
        response = self._put_reorder(self.section.id, ordered, user=outsider)
        # check_permission gate at the dispatch level rejects users without
        # owner/manager roles on any restaurant — returns 403.
        self.assertEqual(response.status_code, 403)
        self.item_c.refresh_from_db()
        self.assertEqual(self.item_c.listing_position, 2)  # unchanged

    def test_reorder_allows_owner_role(self):
        # The admin user seeded by seed_restaurant has the OWNER role.
        # Just a sanity check that owner-roled users succeed end-to-end.
        ordered = [str(self.item_b.id), str(self.item_a.id), str(self.item_c.id)]
        response = self._put_reorder(self.section.id, ordered)
        self.assertEqual(response.status_code, 200)
        self.item_b.refresh_from_db()
        self.assertEqual(self.item_b.listing_position, 0)


class MenuItemDiscountMathTests(TestCase):
    """Regression tests for the canonical discount_details schema and the
    order pipeline's effective-unit-price calculation."""

    def setUp(self):
        seed_user()
        seed_restaurant()
        seed_menu_section()
        self.section = MenuSection.objects.get(name=TEST_MENU_SECTION_NAME)

    def _make_item(self, name, primary, discount_details, discounted_price):
        return MenuItem.objects.create(
            name=name,
            section=self.section,
            primary_price=primary,
            discounted_price=discounted_price,
            running_discount=True,
            consider_discount_object=True,
            discount_details=discount_details,
        )

    @staticmethod
    def _always_active_temporal():
        # recurring_days covers every weekday and the date/time fields are
        # left blank so the temporal gates in con_orders.py don't fire.
        return {
            'recurring_days': [1, 2, 3, 4, 5, 6, 7],
            'start_date': '',
            'end_date': '',
            'start_time': '',
            'end_time': '',
        }

    def test_percentage_discount_serializer_and_pipeline(self):
        from decimal import Decimal
        from orders_app.controllers.con_orders import ConOrder
        from restaurants_app.serializers import SerializerPublicGetMenuItem

        details = {
            'discount_type': 'percentage',
            'discount_percentage': 20.0,
            'discount_amount': 0.0,
            **self._always_active_temporal(),
        }
        item = self._make_item('Pct Item', Decimal('10000'), details, Decimal('8000.00'))

        data = SerializerPublicGetMenuItem(item).data
        self.assertEqual(data['discount_percentage'], 20.0)

        result = ConOrder.determine_effective_unit_price(item)
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['price'], Decimal('8000.00'))

    def test_fixed_discount_serializer_and_pipeline(self):
        from decimal import Decimal
        from orders_app.controllers.con_orders import ConOrder
        from restaurants_app.serializers import SerializerPublicGetMenuItem

        details = {
            'discount_type': 'fixed',
            'discount_percentage': 0.0,
            'discount_amount': 2000.0,
            **self._always_active_temporal(),
        }
        item = self._make_item('Fixed Item', Decimal('10000'), details, Decimal('8000.00'))

        data = SerializerPublicGetMenuItem(item).data
        self.assertEqual(data['discount_percentage'], 20.0)

        result = ConOrder.determine_effective_unit_price(item)
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['price'], Decimal('8000.00'))

    def test_no_discount_returns_primary_price(self):
        from decimal import Decimal
        from orders_app.controllers.con_orders import ConOrder
        from restaurants_app.serializers import SerializerPublicGetMenuItem

        item = MenuItem.objects.create(
            name='Plain Item',
            section=self.section,
            primary_price=Decimal('5000'),
            discounted_price=None,
            running_discount=False,
            consider_discount_object=False,
            discount_details={},
        )

        data = SerializerPublicGetMenuItem(item).data
        self.assertEqual(data['discount_percentage'], 0)

        result = ConOrder.determine_effective_unit_price(item)
        self.assertEqual(result['status'], 200)
        self.assertEqual(result['price'], Decimal('5000.00'))

    def test_canonical_shape_has_no_raw_keys(self):
        # Regression guard: the canonical schema must never include
        # raw_discount_value or raw_discount_type. The pre-0042 buggy keys
        # are migrated out and must not be reintroduced.
        from decimal import Decimal

        details = {
            'discount_type': 'percentage',
            'discount_percentage': 15.0,
            'discount_amount': 0.0,
            **self._always_active_temporal(),
        }
        item = self._make_item('Guard Item', Decimal('10000'), details, Decimal('8500.00'))
        item.refresh_from_db()
        self.assertNotIn('raw_discount_value', item.discount_details)
        self.assertNotIn('raw_discount_type', item.discount_details)


class TenantIsolationTests(TestCase):
    """
    Cross-restaurant authorization tests for the RestaurantSetupEndpoint
    permission gate. Owner of restaurant A must NOT be able to mutate
    resources belonging to restaurant B; only dinify admins or active
    owner/manager employees of the *target* restaurant may write.

    Headline security property: update/delete resolvers walk FK chains
    server-side from the record's id and ignore any client-supplied
    `restaurant` field. Spoofing `{id: <victim's record>, restaurant:
    <attacker's own>}` must not authorize.
    """

    def setUp(self):
        from rest_framework_simplejwt.tokens import RefreshToken  # noqa: F401
        # Two unrelated restaurants, two unrelated owners.
        self.owner_a = User.objects.create_user(
            first_name='Owner', last_name='A',
            email='owner_a@test.com', phone_number='256700000010',
            username='256700000010', country='Uganda', password='password',
            roles=[],  # not a dinify admin
        )
        self.restaurant_a = Restaurant.objects.create(
            name='Restaurant A', location='loc-a',
            status=RestaurantStatus_Active, owner=self.owner_a,
        )
        self.employment_a = RestaurantEmployee.objects.create(
            user=self.owner_a, restaurant=self.restaurant_a,
            roles=[ROLES.get('RESTAURANT_OWNER')],
        )

        self.owner_b = User.objects.create_user(
            first_name='Owner', last_name='B',
            email='owner_b@test.com', phone_number='256700000020',
            username='256700000020', country='Uganda', password='password',
            roles=[],
        )
        self.restaurant_b = Restaurant.objects.create(
            name='Restaurant B', location='loc-b',
            status=RestaurantStatus_Active, owner=self.owner_b,
        )
        RestaurantEmployee.objects.create(
            user=self.owner_b, restaurant=self.restaurant_b,
            roles=[ROLES.get('RESTAURANT_OWNER')],
        )

        # Resources living in restaurant B that owner_a may try to attack.
        self.section_b = MenuSection.objects.create(
            name='B Mains', restaurant=self.restaurant_b, listing_position=0,
        )
        self.item_b = MenuItem.objects.create(
            name='B Item', section=self.section_b, primary_price=1000,
            listing_position=0,
        )
        self.group_b = SectionGroup.objects.create(
            name='B Group', section=self.section_b,
        )
        self.dining_area_b = DiningArea.objects.create(
            name='B Patio', restaurant=self.restaurant_b,
        )
        self.table_b = Table.objects.create(
            number=1, str_number='1', restaurant=self.restaurant_b,
        )
        self.section_a = MenuSection.objects.create(
            name='A Mains', restaurant=self.restaurant_a, listing_position=0,
        )

        # Outsider with zero employments.
        self.outsider = User.objects.create_user(
            first_name='Out', last_name='Sider',
            email='outsider@test.com', phone_number='256700000030',
            username='256700000030', country='Uganda', password='password',
            roles=[],
        )

        # Independent dinify admin (no employments at either restaurant).
        self.dinify_admin = User.objects.create_user(
            first_name='Dinify', last_name='Admin',
            email='admin@test.com', phone_number='256700000040',
            username='256700000040', country='Uganda', password='password',
            roles=['dinify_admin'],
        )

    def _token_for(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        return str(RefreshToken.for_user(user).access_token)

    def _request(self, user, method, config_detail, body):
        path = f'/api/v1/restaurant-setup/{config_detail}/'
        token = self._token_for(user)
        kwargs = {
            'data': body,
            'content_type': 'application/json',
            'HTTP_AUTHORIZATION': f'Bearer {token}',
        }
        return getattr(self.client, method)(path, **kwargs)

    # -- admin bypass --------------------------------------------------------

    def test_dinify_admin_can_create_in_any_restaurant(self):
        # Admin has no employment at restaurant B but should still be allowed.
        response = self._request(
            self.dinify_admin, 'post', 'menusections',
            {'name': 'Admin Section', 'restaurant': str(self.restaurant_b.id)},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(MenuSection.objects.filter(
            name='Admin Section', restaurant=self.restaurant_b,
        ).exists())

    def test_inactive_dinify_admin_is_denied(self):
        self.dinify_admin.is_active = False
        self.dinify_admin.save(update_fields=['is_active'])
        response = self._request(
            self.dinify_admin, 'post', 'menusections',
            {'name': 'Should Fail', 'restaurant': str(self.restaurant_b.id)},
        )
        # JWT auth itself rejects inactive users; the contract is "not 200".
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(MenuSection.objects.filter(name='Should Fail').exists())

    # -- happy path ----------------------------------------------------------

    def test_owner_can_update_own_menusection(self):
        response = self._request(
            self.owner_a, 'put', 'menusections',
            {'id': str(self.section_a.id), 'name': 'A Mains Renamed',
             'restaurant': str(self.restaurant_a.id)},
        )
        self.assertEqual(response.status_code, 200)
        self.section_a.refresh_from_db()
        self.assertEqual(self.section_a.name, 'A Mains Renamed')

    # -- cross-restaurant rejection: menusections ----------------------------

    def test_owner_of_a_cannot_create_menusection_in_b(self):
        response = self._request(
            self.owner_a, 'post', 'menusections',
            {'name': 'Hostile', 'restaurant': str(self.restaurant_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(MenuSection.objects.filter(name='Hostile').exists())

    def test_owner_of_a_cannot_update_menusection_in_b_via_spoof(self):
        # Spoof payload: id points at B's section, restaurant points at A.
        # Resolver must walk FK from id to detect the real target is B.
        original_name = self.section_b.name
        response = self._request(
            self.owner_a, 'put', 'menusections',
            {'id': str(self.section_b.id), 'name': 'pwned',
             'restaurant': str(self.restaurant_a.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.section_b.refresh_from_db()
        self.assertEqual(self.section_b.name, original_name)

    def test_owner_of_a_cannot_delete_menusection_in_b(self):
        response = self._request(
            self.owner_a, 'delete', 'menusections',
            {'id': str(self.section_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.section_b.refresh_from_db()
        self.assertFalse(self.section_b.deleted)

    # -- cross-restaurant rejection: menuitems (two-hop FK) ------------------

    def test_owner_of_a_cannot_create_menuitem_in_b(self):
        response = self._request(
            self.owner_a, 'post', 'menuitems',
            {'name': 'Hostile Item', 'section': str(self.section_b.id),
             'primary_price': '1000.00'},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(MenuItem.objects.filter(name='Hostile Item').exists())

    def test_owner_of_a_cannot_update_menuitem_in_b_via_spoof(self):
        original_name = self.item_b.name
        response = self._request(
            self.owner_a, 'put', 'menuitems',
            {'id': str(self.item_b.id), 'name': 'pwned',
             'restaurant': str(self.restaurant_a.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.item_b.refresh_from_db()
        self.assertEqual(self.item_b.name, original_name)

    def test_owner_of_a_cannot_delete_menuitem_in_b(self):
        response = self._request(
            self.owner_a, 'delete', 'menuitems',
            {'id': str(self.item_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.item_b.refresh_from_db()
        self.assertFalse(self.item_b.deleted)

    # -- cross-restaurant rejection: sectiongroups (two-hop FK) --------------

    def test_owner_of_a_cannot_create_sectiongroup_in_b(self):
        response = self._request(
            self.owner_a, 'post', 'sectiongroups',
            {'name': 'Hostile Group', 'section': str(self.section_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(SectionGroup.objects.filter(name='Hostile Group').exists())

    def test_owner_of_a_cannot_delete_sectiongroup_in_b(self):
        response = self._request(
            self.owner_a, 'delete', 'sectiongroups',
            {'id': str(self.group_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.group_b.refresh_from_db()
        self.assertFalse(self.group_b.deleted)

    # -- cross-restaurant rejection: tables ----------------------------------

    def test_owner_of_a_cannot_create_table_in_b(self):
        response = self._request(
            self.owner_a, 'post', 'tables',
            {'number': 99, 'restaurant': str(self.restaurant_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Table.objects.filter(
            number=99, restaurant=self.restaurant_b,
        ).exists())

    def test_owner_of_a_cannot_delete_table_in_b(self):
        response = self._request(
            self.owner_a, 'delete', 'tables',
            {'id': str(self.table_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.table_b.refresh_from_db()
        self.assertFalse(self.table_b.deleted)

    # -- cross-restaurant rejection: diningareas -----------------------------

    def test_owner_of_a_cannot_create_diningarea_in_b(self):
        response = self._request(
            self.owner_a, 'post', 'diningareas',
            {'name': 'Hostile Patio', 'restaurant': str(self.restaurant_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(DiningArea.objects.filter(name='Hostile Patio').exists())

    def test_owner_of_a_cannot_delete_diningarea_in_b(self):
        response = self._request(
            self.owner_a, 'delete', 'diningareas',
            {'id': str(self.dining_area_b.id)},
        )
        self.assertEqual(response.status_code, 403)
        self.dining_area_b.refresh_from_db()
        self.assertFalse(self.dining_area_b.deleted)

    # -- cross-restaurant rejection: employees -------------------------------

    def test_owner_of_a_cannot_create_employee_in_b_via_create_employee(self):
        response = self._request(
            self.owner_a, 'post', 'create-employee',
            {'first_name': 'Mole', 'last_name': 'Spy',
             'email': 'mole@test.com', 'phone_number': '256700000099',
             'restaurant': str(self.restaurant_b.id),
             'roles': [ROLES.get('RESTAURANT_KITCHEN')]},
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.filter(phone_number='256700000099').exists())

    def test_owner_of_a_cannot_create_employee_in_b_via_employees_shortcut(self):
        # The /employees/ shortcut path bypassed the gate before the fix —
        # it now has its own check_permission call.
        response = self._request(
            self.owner_a, 'post', 'employees',
            {'user': str(self.owner_b.id),
             'restaurant': str(self.restaurant_b.id),
             'roles': [ROLES.get('RESTAURANT_MANAGER')]},
        )
        self.assertEqual(response.status_code, 403)
        # owner_b should still have only their original owner row.
        self.assertEqual(
            RestaurantEmployee.objects.filter(
                user=self.owner_b, restaurant=self.restaurant_b,
            ).count(),
            1,
        )

    def test_owner_of_a_cannot_delete_employee_in_b(self):
        b_employee = RestaurantEmployee.objects.get(
            user=self.owner_b, restaurant=self.restaurant_b,
        )
        response = self._request(
            self.owner_a, 'delete', 'employees',
            {'id': str(b_employee.id)},
        )
        self.assertEqual(response.status_code, 403)
        b_employee.refresh_from_db()
        self.assertTrue(b_employee.active)

    # -- role gating ---------------------------------------------------------

    def test_outsider_with_no_employment_denied_for_all_resources(self):
        cases = [
            ('post', 'menusections',
             {'name': 'X', 'restaurant': str(self.restaurant_a.id)}),
            ('post', 'menuitems',
             {'name': 'X', 'section': str(self.section_a.id), 'primary_price': '1000'}),
            ('post', 'sectiongroups',
             {'name': 'X', 'section': str(self.section_a.id)}),
            ('post', 'tables',
             {'number': 50, 'restaurant': str(self.restaurant_a.id)}),
            ('post', 'diningareas',
             {'name': 'X', 'restaurant': str(self.restaurant_a.id)}),
            ('delete', 'menusections', {'id': str(self.section_a.id)}),
            ('delete', 'menuitems', {'id': str(self.item_b.id)}),
            ('delete', 'tables', {'id': str(self.table_b.id)}),
        ]
        for method, resource, body in cases:
            with self.subTest(method=method, resource=resource):
                response = self._request(self.outsider, method, resource, body)
                self.assertEqual(
                    response.status_code, 403,
                    f'Expected 403 for outsider {method} {resource}, got {response.status_code}',
                )

    def test_waiter_role_at_own_restaurant_denied(self):
        waiter = User.objects.create_user(
            first_name='W', last_name='aiter',
            email='waiter@test.com', phone_number='256700000050',
            username='256700000050', country='Uganda', password='password',
            roles=[],
        )
        RestaurantEmployee.objects.create(
            user=waiter, restaurant=self.restaurant_a,
            roles=[ROLES.get('RESTAURANT_WAITER')],
        )
        response = self._request(
            waiter, 'post', 'menusections',
            {'name': 'Waiter section', 'restaurant': str(self.restaurant_a.id)},
        )
        self.assertEqual(response.status_code, 403)

    def test_inactive_employee_record_denied(self):
        # Owner role at the right restaurant, but the employee row is inactive.
        self.employment_a.active = False
        self.employment_a.save(update_fields=['active'])
        response = self._request(
            self.owner_a, 'post', 'menusections',
            {'name': 'Should Fail', 'restaurant': str(self.restaurant_a.id)},
        )
        self.assertEqual(response.status_code, 403)

    def test_soft_deleted_employee_record_denied(self):
        self.employment_a.deleted = True
        self.employment_a.save(update_fields=['deleted'])
        response = self._request(
            self.owner_a, 'post', 'menusections',
            {'name': 'Should Fail', 'restaurant': str(self.restaurant_a.id)},
        )
        self.assertEqual(response.status_code, 403)

    # -- resolver failure modes (deny by default) ----------------------------

    def test_delete_with_unknown_record_id_returns_403(self):
        response = self._request(
            self.owner_a, 'delete', 'menuitems',
            {'id': '00000000-0000-0000-0000-000000000000'},
        )
        self.assertEqual(response.status_code, 403)

    def test_put_with_missing_id_returns_403(self):
        response = self._request(
            self.owner_a, 'put', 'menusections',
            {'name': 'no id here'},
        )
        self.assertEqual(response.status_code, 403)

    def test_post_menusection_missing_restaurant_returns_403(self):
        response = self._request(
            self.owner_a, 'post', 'menusections',
            {'name': 'no restaurant here'},
        )
        self.assertEqual(response.status_code, 403)

    def test_post_menuitem_missing_section_returns_403(self):
        response = self._request(
            self.owner_a, 'post', 'menuitems',
            {'name': 'no section here', 'primary_price': '1000'},
        )
        self.assertEqual(response.status_code, 403)


class MenuSectionScheduleTests(TestCase):
    """Tests for is_section_currently_active and the diner show-menu filter."""

    @staticmethod
    def _make_section(availability='scheduled', schedules=None):
        from types import SimpleNamespace
        return SimpleNamespace(
            availability=availability,
            schedules=[] if schedules is None else schedules,
        )

    @staticmethod
    def _at(year, month, day, hour, minute):
        import pytz
        from datetime import datetime as real_dt
        return pytz.timezone('Africa/Nairobi').localize(
            real_dt(year, month, day, hour, minute)
        )

    # 2026-01-05 is Monday, 2026-01-06 Tuesday, ..., 2026-01-11 Sunday.

    def test_availability_always_returns_true(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(availability='always', schedules=[])
        self.assertTrue(is_section_currently_active(section))

    def test_scheduled_with_empty_schedules_returns_true(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(availability='scheduled', schedules=[])
        self.assertTrue(is_section_currently_active(section))

    def test_scheduled_in_window_active(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(schedules=[
            {'days': ['mon', 'tue'], 'startTime': '07:00', 'endTime': '11:00'},
        ])
        # Monday 10:00 -> inside window.
        self.assertTrue(
            is_section_currently_active(section, now=self._at(2026, 1, 5, 10, 0))
        )

    def test_scheduled_wrong_day_inactive(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(schedules=[
            {'days': ['mon', 'tue'], 'startTime': '07:00', 'endTime': '11:00'},
        ])
        # Wednesday 10:00 -> day not in slot.
        self.assertFalse(
            is_section_currently_active(section, now=self._at(2026, 1, 7, 10, 0))
        )

    def test_scheduled_in_day_outside_window_inactive(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(schedules=[
            {'days': ['mon'], 'startTime': '07:00', 'endTime': '11:00'},
        ])
        # Monday 13:00 -> outside window.
        self.assertFalse(
            is_section_currently_active(section, now=self._at(2026, 1, 5, 13, 0))
        )

    def test_overnight_window_late_evening_active(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(schedules=[
            {'days': ['mon'], 'startTime': '22:00', 'endTime': '02:00'},
        ])
        # Monday 23:30 -> past start of overnight window.
        self.assertTrue(
            is_section_currently_active(section, now=self._at(2026, 1, 5, 23, 30))
        )

    def test_overnight_window_early_morning_active(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        # Slot anchored to Monday but with overnight 22:00-02:00 window.
        # The frontend considers Tuesday 01:00 still inside the Monday slot's
        # overnight tail. Backend mirrors the frontend by treating "current
        # day" as the slot day and accepting times before end_min.
        section = self._make_section(schedules=[
            {'days': ['tue'], 'startTime': '22:00', 'endTime': '02:00'},
        ])
        # Tuesday 01:00 -> before end of overnight window for the Tuesday slot.
        self.assertTrue(
            is_section_currently_active(section, now=self._at(2026, 1, 6, 1, 0))
        )

    def test_overnight_window_outside_inactive(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(schedules=[
            {'days': ['mon'], 'startTime': '22:00', 'endTime': '02:00'},
        ])
        # Monday 05:00 -> outside the overnight window (after end, before start).
        self.assertFalse(
            is_section_currently_active(section, now=self._at(2026, 1, 5, 5, 0))
        )

    def test_malformed_days_string_instead_of_list_skipped(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(schedules=[
            {'days': 'mon', 'startTime': '07:00', 'endTime': '11:00'},
        ])
        self.assertFalse(
            is_section_currently_active(section, now=self._at(2026, 1, 5, 10, 0))
        )

    def test_malformed_days_numeric_skipped(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        # Legacy int-day shape: 'mon' is not in [1, 2, 3] so slot is rejected.
        section = self._make_section(schedules=[
            {'days': [1, 2, 3], 'startTime': '07:00', 'endTime': '11:00'},
        ])
        self.assertFalse(
            is_section_currently_active(section, now=self._at(2026, 1, 5, 10, 0))
        )

    def test_malformed_time_string_skipped(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(schedules=[
            {'days': ['mon'], 'startTime': '25:99', 'endTime': '11:00'},
        ])
        self.assertFalse(
            is_section_currently_active(section, now=self._at(2026, 1, 5, 10, 0))
        )

    def test_multiple_slots_any_match_active(self):
        from restaurants_app.controllers.utils.schedule_utils import (
            is_section_currently_active,
        )
        section = self._make_section(schedules=[
            {'days': ['tue'], 'startTime': '07:00', 'endTime': '11:00'},
            {'days': ['mon'], 'startTime': '12:00', 'endTime': '14:00'},
        ])
        # Monday 13:00 -> matches the second slot only.
        self.assertTrue(
            is_section_currently_active(section, now=self._at(2026, 1, 5, 13, 0))
        )

    def test_handle_show_menu_filters_inactive_scheduled_sections(self):
        from unittest.mock import patch
        from restaurants_app.controllers.handle_diner_journey import (
            handle_show_menu,
        )

        seed_user()
        seed_restaurant()
        restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)

        always_section = MenuSection.objects.create(
            name='Always Section', restaurant=restaurant,
            availability='always', schedules=[],
            approved=True, enabled=True, available=True,
        )
        # Scheduled for Tuesday only; "now" will be Monday 10:00 -> inactive.
        MenuSection.objects.create(
            name='Scheduled Inactive', restaurant=restaurant,
            availability='scheduled',
            schedules=[
                {'days': ['tue'], 'startTime': '07:00', 'endTime': '11:00'},
            ],
            approved=True, enabled=True, available=True,
        )

        monday_10am = self._at(2026, 1, 5, 10, 0)
        with patch(
            'restaurants_app.controllers.utils.schedule_utils.datetime'
        ) as mock_datetime:
            mock_datetime.now.return_value = monday_10am
            response = handle_show_menu(str(restaurant.id), 'false')

        self.assertEqual(response['status'], 200)
        returned_ids = [section['id'] for section in response['data']]
        self.assertEqual(returned_ids, [str(always_section.id)])


class NullableFieldClearingTests(TestCase):
    """
    Verifies the `clear_<field>: true` sentinel pattern wired into
    RestaurantSetupEndpoint.put. The Secretary skips payload values that
    are None (misc_app/controllers/secretary.py:316), so nullable scalar
    fields cannot be cleared via the normal update path. The sentinel is
    intercepted before Secretary runs and writes None directly via a
    queryset .update(), mirroring the clear_image precedent.
    """

    def setUp(self):
        from decimal import Decimal
        self.owner = User.objects.create_user(
            first_name='Null', last_name='Clearer',
            email='nullclearer@test.com', phone_number='256700000050',
            username='256700000050', country='Uganda', password='password',
            roles=[],
        )
        self.restaurant = Restaurant.objects.create(
            name='Null Clearing Restaurant', location='loc',
            status=RestaurantStatus_Active, owner=self.owner,
        )
        RestaurantEmployee.objects.create(
            user=self.owner, restaurant=self.restaurant,
            roles=[ROLES.get('RESTAURANT_OWNER')],
        )
        self.section = MenuSection.objects.create(
            name='Mains', restaurant=self.restaurant, listing_position=0,
        )
        # Item starts with both clearable fields set so we can verify
        # they actually flip to None.
        self.item = MenuItem.objects.create(
            name='Burger', section=self.section,
            primary_price=Decimal('10.00'),
            calories=200,
            discounted_price=Decimal('5.00'),
            listing_position=0,
        )

    def _token_for(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        return str(RefreshToken.for_user(user).access_token)

    def _put(self, body):
        path = '/api/v1/restaurant-setup/menuitems/'
        token = self._token_for(self.owner)
        return self.client.put(
            path,
            data=body,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    def test_clear_calories_sets_to_none(self):
        response = self._put({
            'id': str(self.item.id),
            'clear_calories': True,
        })
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertIsNone(self.item.calories)

    def test_clear_discounted_price_sets_to_none(self):
        response = self._put({
            'id': str(self.item.id),
            'clear_discounted_price': True,
        })
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertIsNone(self.item.discounted_price)

    def test_clear_with_companion_null_value(self):
        # Frontend sends only the sentinel, but a programmatic caller
        # might send both. Should still clear, no error from companion.
        response = self._put({
            'id': str(self.item.id),
            'clear_calories': True,
            'calories': None,
        })
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertIsNone(self.item.calories)

    def test_clear_false_does_not_clear(self):
        # `clear_calories: false` is not a clear request — the field
        # should retain its existing value.
        response = self._put({
            'id': str(self.item.id),
            'clear_calories': False,
            'name': 'Burger Renamed',
        })
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.calories, 200)

    def test_clear_does_not_affect_other_fields(self):
        from decimal import Decimal
        original_name = self.item.name
        original_price = self.item.primary_price
        response = self._put({
            'id': str(self.item.id),
            'clear_calories': True,
        })
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertIsNone(self.item.calories)
        self.assertEqual(self.item.name, original_name)
        self.assertEqual(self.item.primary_price, Decimal(original_price))

    def test_multiple_clears_in_one_request(self):
        response = self._put({
            'id': str(self.item.id),
            'clear_calories': True,
            'clear_discounted_price': True,
        })
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertIsNone(self.item.calories)
        self.assertIsNone(self.item.discounted_price)

    def test_clear_unknown_field_is_ignored(self):
        # Unregistered clear_<field> sentinels must not cause a 500 or
        # affect any field. The handler only iterates the registered
        # NULLABLE_CLEARABLE_FIELDS list.
        response = self._put({
            'id': str(self.item.id),
            'clear_nonexistent_field': True,
            'name': 'Burger Renamed',
        })
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.calories, 200)

    def test_clear_wins_over_explicit_value(self):
        # Sentinel contract: `clear_<field>` always takes precedence over
        # a competing value in the same payload, even non-null. Without
        # this guarantee, Secretary would write 999 *after* our
        # UPDATE-to-None ran and silently override the clear.
        response = self._put({
            'id': str(self.item.id),
            'clear_calories': True,
            'calories': 999,
        })
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertIsNone(self.item.calories)


class PresetTagsEndpointTests(TestCase):
    """
    Locks in the contract for PUT /api/v1/restaurant-setup/preset-tags/.
    The endpoint expects `tags` to be a native JSON array; a stringified
    array (the historical frontend bug) must be rejected with 400 so the
    bug cannot regress unnoticed.
    """

    def setUp(self):
        self.owner = User.objects.create_user(
            first_name='Preset', last_name='Owner',
            email='preset_owner@test.com', phone_number='256700000060',
            username='256700000060', country='Uganda', password='password',
            roles=[],
        )
        self.restaurant = Restaurant.objects.create(
            name='Preset Tags Restaurant', location='loc',
            status=RestaurantStatus_Active, owner=self.owner,
        )
        RestaurantEmployee.objects.create(
            user=self.owner, restaurant=self.restaurant,
            roles=[ROLES.get('RESTAURANT_OWNER')],
        )

    def _token_for(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        return str(RefreshToken.for_user(user).access_token)

    def _put(self, body):
        token = self._token_for(self.owner)
        return self.client.put(
            '/api/v1/restaurant-setup/preset-tags/',
            data=body,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    def _tag(self, tid, name):
        return {
            'id': tid, 'name': name, 'icon': 'tag',
            'color': 'gray', 'filterable': True,
        }

    def test_put_with_native_array_succeeds(self):
        tags = [self._tag('a', 'vegan'), self._tag('b', 'spicy')]
        response = self._put({
            'restaurant': str(self.restaurant.id),
            'tags': tags,
        })
        self.assertEqual(response.status_code, 200)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.preset_tags, tags)

    def test_put_with_stringified_json_returns_400(self):
        import json
        tags = [self._tag('a', 'vegan')]
        response = self._put({
            'restaurant': str(self.restaurant.id),
            'tags': json.dumps(tags),
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'status': 400, 'message': 'tags (list) is required',
        })
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.preset_tags, [])

    def test_put_with_missing_tags_returns_400(self):
        response = self._put({'restaurant': str(self.restaurant.id)})
        self.assertEqual(response.status_code, 400)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.preset_tags, [])

    def test_put_with_empty_list_succeeds(self):
        self.restaurant.preset_tags = [self._tag('x', 'old')]
        self.restaurant.save(update_fields=['preset_tags'])
        response = self._put({
            'restaurant': str(self.restaurant.id),
            'tags': [],
        })
        self.assertEqual(response.status_code, 200)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.preset_tags, [])


class DedicatedEndpointAuthorizationTests(TestCase):
    """
    Locks in the tightened authorization filters (`active=True, deleted=False`)
    on the two permission helpers used outside the catch-all PUT path:

    - users_app.controllers.permissions_check.get_user_restaurant_roles
    - restaurants_app.controllers.first_time_batch_approval.check_permissions

    These helpers gate every dedicated endpoint (preset_tags, upsell_config,
    reservations, waitlist, table_actions) and the first-time-menu-review
    manager action. The catch-all PUT path is already covered by
    TenantIsolationTests; this class is its analogue for the dedicated
    endpoints, plus a cross-tenant regression guard at preset_tags.
    """

    def setUp(self):
        self.owner_a = User.objects.create_user(
            first_name='Owner', last_name='A',
            email='owner_a_dedicated@test.com', phone_number='256700000110',
            username='256700000110', country='Uganda', password='password',
            roles=[],
        )
        self.restaurant_a = Restaurant.objects.create(
            name='Dedicated A', location='loc-a',
            status=RestaurantStatus_Active, owner=self.owner_a,
        )
        self.employment_a = RestaurantEmployee.objects.create(
            user=self.owner_a, restaurant=self.restaurant_a,
            roles=[ROLES.get('RESTAURANT_OWNER')],
        )

        self.owner_b = User.objects.create_user(
            first_name='Owner', last_name='B',
            email='owner_b_dedicated@test.com', phone_number='256700000120',
            username='256700000120', country='Uganda', password='password',
            roles=[],
        )
        self.restaurant_b = Restaurant.objects.create(
            name='Dedicated B', location='loc-b',
            status=RestaurantStatus_Active, owner=self.owner_b,
        )
        RestaurantEmployee.objects.create(
            user=self.owner_b, restaurant=self.restaurant_b,
            roles=[ROLES.get('RESTAURANT_OWNER')],
        )

        # first-time-menu-review bails with 400 if the restaurant has no
        # menu sections (see first_time_batch_approval.py:75-82), so seed one.
        MenuSection.objects.create(
            name='A Section', restaurant=self.restaurant_a, listing_position=0,
        )

    def _token_for(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        return str(RefreshToken.for_user(user).access_token)

    def _tag(self, tid, name):
        return {
            'id': tid, 'name': name, 'icon': 'tag',
            'color': 'gray', 'filterable': True,
        }

    def _preset_tags_put(self, user, body):
        token = self._token_for(user)
        return self.client.put(
            '/api/v1/restaurant-setup/preset-tags/',
            data=body,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    def _first_time_menu_review_post(self, user, body):
        token = self._token_for(user)
        return self.client.post(
            '/api/v1/restaurant-setup/manager-actions/first-time-menu-review/',
            data=body,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    # -- unit: get_user_restaurant_roles --------------------------------

    def test_get_user_restaurant_roles_excludes_deactivated_employee(self):
        from users_app.controllers.permissions_check import (
            get_user_restaurant_roles,
        )
        self.employment_a.active = False
        self.employment_a.save(update_fields=['active'])
        roles = get_user_restaurant_roles(
            user_id=str(self.owner_a.id),
            restaurant_id=str(self.restaurant_a.id),
        )
        self.assertEqual(roles, [])

    def test_get_user_restaurant_roles_excludes_soft_deleted_employee(self):
        from users_app.controllers.permissions_check import (
            get_user_restaurant_roles,
        )
        self.employment_a.deleted = True
        self.employment_a.save(update_fields=['deleted'])
        roles = get_user_restaurant_roles(
            user_id=str(self.owner_a.id),
            restaurant_id=str(self.restaurant_a.id),
        )
        self.assertEqual(roles, [])

    # -- unit: first_time_batch_approval.check_permissions --------------

    def test_first_time_batch_check_excludes_deactivated_employee(self):
        from restaurants_app.controllers.first_time_batch_approval import (
            check_permissions,
        )
        self.employment_a.active = False
        self.employment_a.save(update_fields=['active'])
        self.assertFalse(check_permissions(
            restaurant_id=str(self.restaurant_a.id),
            user_id=str(self.owner_a.id),
        ))

    def test_first_time_batch_check_excludes_soft_deleted_employee(self):
        from restaurants_app.controllers.first_time_batch_approval import (
            check_permissions,
        )
        self.employment_a.deleted = True
        self.employment_a.save(update_fields=['deleted'])
        self.assertFalse(check_permissions(
            restaurant_id=str(self.restaurant_a.id),
            user_id=str(self.owner_a.id),
        ))

    # -- integration: preset_tags ---------------------------------------

    def test_deactivated_employee_blocked_from_preset_tags_put(self):
        self.employment_a.active = False
        self.employment_a.save(update_fields=['active'])
        response = self._preset_tags_put(
            self.owner_a,
            {
                'restaurant': str(self.restaurant_a.id),
                'tags': [self._tag('a', 'vegan')],
            },
        )
        self.assertEqual(response.status_code, 403)
        self.restaurant_a.refresh_from_db()
        self.assertEqual(self.restaurant_a.preset_tags, [])

    def test_cross_tenant_blocked_from_preset_tags_put(self):
        # owner_a has an active employment at A but none at B.
        response = self._preset_tags_put(
            self.owner_a,
            {
                'restaurant': str(self.restaurant_b.id),
                'tags': [self._tag('a', 'vegan')],
            },
        )
        self.assertEqual(response.status_code, 403)
        self.restaurant_b.refresh_from_db()
        self.assertEqual(self.restaurant_b.preset_tags, [])

    # -- integration: first-time-menu-review ----------------------------

    def test_deactivated_employee_blocked_from_first_time_menu_review(self):
        self.employment_a.active = False
        self.employment_a.save(update_fields=['active'])
        response = self._first_time_menu_review_post(
            self.owner_a,
            {
                'restaurant': str(self.restaurant_a.id),
                'decision': 'submit',
            },
        )
        # The controller returns status 401 in the body when permission is
        # denied (see first_time_batch_approval.py:67-71).
        self.assertEqual(response.json().get('status'), 401)
        self.restaurant_a.refresh_from_db()
        self.assertNotEqual(
            self.restaurant_a.first_time_menu_approval_decision, 'submit',
        )


class MenuItemAllergensToTagsMigrationTests(TestCase):
    """
    Locks in the data migration in
    restaurants_app/migrations/0043_migrate_menuitem_allergens_to_tags.py.
    The migration moves every saved value out of MenuItem.allergens and
    into MenuItem.tags, deduplicating while preserving order. allergens
    is reset to [] for the future allergen-warning feature.

    The migration function is invoked directly with django's live app
    registry — no schema changes are exercised.
    """

    def setUp(self):
        owner = User.objects.create_user(
            first_name='AllergenMig', last_name='Owner',
            email='allergen_mig_owner@test.com',
            phone_number='256700000080',
            username='256700000080', country='Uganda', password='password',
            roles=[],
        )
        self.restaurant = Restaurant.objects.create(
            name='Allergen Migration Restaurant', location='loc',
            status=RestaurantStatus_Active, owner=owner,
        )
        self.section = MenuSection.objects.create(
            name='Mains', restaurant=self.restaurant,
        )

    def _item(self, name, allergens=None, tags=None):
        kwargs = {
            'name': name,
            'section': self.section,
            'primary_price': 1000.0,
        }
        if allergens is not None:
            kwargs['allergens'] = allergens
        if tags is not None:
            kwargs['tags'] = tags
        return MenuItem.objects.create(**kwargs)

    def _run_migration(self):
        # Migration module names start with a digit, so import via importlib.
        import importlib
        from django.apps import apps as global_apps
        mig = importlib.import_module(
            'restaurants_app.migrations'
            '.0043_migrate_menuitem_allergens_to_tags'
        )
        mig.migrate_allergens_to_tags(global_apps, None)

    def test_migration_moves_allergens_to_tags_when_tags_empty(self):
        item = self._item(
            'Plain', allergens=['vegan', 'spicy'], tags=[],
        )
        self._run_migration()
        item.refresh_from_db()
        self.assertEqual(item.tags, ['vegan', 'spicy'])
        self.assertEqual(item.allergens, [])

    def test_migration_merges_when_tags_already_populated(self):
        item = self._item(
            'Both', allergens=['vegan'], tags=['popular'],
        )
        self._run_migration()
        item.refresh_from_db()
        # Existing tags first, then allergens entries appended.
        self.assertEqual(item.tags, ['popular', 'vegan'])
        self.assertEqual(item.allergens, [])

    def test_migration_dedupes_overlapping_values(self):
        item = self._item(
            'Overlap', allergens=['vegan', 'spicy'], tags=['vegan'],
        )
        self._run_migration()
        item.refresh_from_db()
        # 'vegan' appears once; 'spicy' is appended after.
        self.assertEqual(item.tags, ['vegan', 'spicy'])
        self.assertEqual(item.allergens, [])

    def test_migration_skips_empty_allergens(self):
        item = self._item(
            'Skip', allergens=[], tags=['existing'],
        )
        self._run_migration()
        item.refresh_from_db()
        self.assertEqual(item.tags, ['existing'])
        self.assertEqual(item.allergens, [])

from django.test import TestCase
from users_app.models import User
from users_app.tests import TEST_PHONE, seed_user
from finance_app.models import DinifyAccount
from restaurants_app.models import Restaurant, Table
from dinify_backend.configs import AccountType_Restaurant
from orders_app.tests import seed_order
from orders_app.models import Order
from restaurants_app.tests import (
    seed_restaurant, seed_menu_section, seed_menu_items, seed_tables,
    TEST_RESTAURANT_NAME, TEST_TABLE_NUMBER1
)
from finance_app.controllers.initiate_order_payment import initiate_order_payment
from dinify_backend.configs import PaymentMode_MobileMoney


def seed_account():
    """
    seed the account for the test
    """
    seed_user()
    seed_restaurant(seed_owner=True)
    restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)
    DinifyAccount.objects.create(
        account_type=AccountType_Restaurant,
        restaurant=restaurant
    )


# Create your tests here.
class FinanceAppTestFunctions(TestCase):
    """
    the test functions for the Misc app
    """
    def setUp(self):
        """
        setup the test
        """
        seed_account()
        # seed_user()
        # seed_restaurant(seed_owner=False)
        seed_menu_section()
        seed_menu_items()
        seed_tables()
        seed_order()

    def test_initiate_order_payment(self):
        restaurant = Restaurant.objects.get(name=TEST_RESTAURANT_NAME)
        table = Table.objects.get(number=TEST_TABLE_NUMBER1)
        user = User.objects.get(username=TEST_PHONE)

        order = Order.objects.get(
            restaurant=restaurant,
            table=table,
            customer=user
        )

        result = initiate_order_payment(
            order=order,
            payment_mode=PaymentMode_MobileMoney,
            msisdn='256706087495'
        )

        self.assertEqual(result['status'], 200)

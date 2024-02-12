from django.test import TestCase
from dinify_backend.configs import MESSAGES
from users_app.tests import TEST_PHONE, seed_user
from users_app.models import User
from restaurants_app.controllers.create_restaurant import create_restaurant


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

    def test_create_restaurant(self):
        """
        test the restaurant self register function
        """
        user_id = str(User.objects.get(username=TEST_PHONE).pk)
        auth_info = {
            'user_id': user_id
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

        test_missing_info()
        test_ok()

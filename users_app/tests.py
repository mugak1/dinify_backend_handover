from django.test import TestCase
from dinify_backend.configs import MESSAGES
from users_app.controllers.self_register import self_register
from users_app.controllers.login import login
from users_app.models import User


def seed_user():
    """
    seed a user to work with for tests
    """
    User.objects.create_user(
        first_name='Test',
        last_name='User',
        email='test@user.com',
        phone_number='123456789',
        username='123456789',
        country='Uganda',
        password='password'
    )

# Create your tests here.
class UsersAppTestFunctions(TestCase):
    """
    the test functions for the Users app
    """
    def setUp(self):
        """
        set up for the tests
        """
        seed_user()

    def test_self_registration(self):
        """
        test self_registration
        """
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@doe.com',
            'phone_number': '256712345678',
            'password': 'password',
            'country': 'Uganda'
        }

        def test_success():
            """ when the registration is successful """
            response = self_register(data)
            self.assertEqual(response.get('status'), 200)
            self.assertEqual(
                response.get('message'),
                MESSAGES.get('OK_SELF_REGISTER')
            )

        def test_duplicate_phone_number():
            response = self_register(data)
            self.assertEqual(response.get('status'), 400)
            self.assertEqual(
                response.get('message'),
                MESSAGES.get('PHONE_NUMBER_EXISTS')
            )

        def test_duplicate_email():
            data['phone_number'] = '256712345679'
            response = self_register(data)            
            self.assertEqual(response.get('status'), 400)
            self.assertEqual(
                response.get('message'),
                MESSAGES.get('EMAIL_EXISTS')
            )

        test_success()
        test_duplicate_phone_number()
        test_duplicate_email()

    def test_login(self):
        """
        test login
        """
        def test_success():
            """ when the login is successful """
            response = login('123456789', 'password')
            self.assertEqual(response.get('status'), 200)
            self.assertEqual(response.get('message'), MESSAGES.get('OK_LOGIN'))

        def test_wrong_password():
            """ when the password is wrong """
            response = login('123456789', 'wrong_password')
            self.assertEqual(response.get('status'), 401)
            self.assertEqual(response.get('message'), MESSAGES.get('WRONG_PASSWORD'))

        def test_no_username():
            """ when the username does not exist """
            response = login('123456780', 'password')
            self.assertEqual(response.get('status'), 401)
            self.assertEqual(response.get('message'), MESSAGES.get('NO_USERNAME'))

        test_success()
        test_wrong_password()
        test_no_username()

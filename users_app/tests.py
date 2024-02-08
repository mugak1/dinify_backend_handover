from django.test import TestCase
from dinify_backend.configs import MESSAGES
from users_app.controllers.self_register import self_register


# Create your tests here.
class UsersAppTestFunctions(TestCase):
    """
    the test functions for the Users app
    """
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

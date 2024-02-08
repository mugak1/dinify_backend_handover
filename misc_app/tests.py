from django.test import TestCase
from misc_app.controllers.check_required_information import check_required_information


# Create your tests here.
class MiscAppTestFunctions(TestCase):
    """
    the test functions for the Misc app
    """
    def test_check_required_information(self):
        """
        test the function to check for required information
        """
        required_information = [
            {
                "key": "key1",
                "label": "Key 1",
                "minimum_length": 5
            },
            {
                "key": "key2",
                "label": "Key 2",
                "minimum_length": 5
            }
        ]

        provided_information1 = {
            'key1': 'value1',
        }
        result = check_required_information(
            required_information,
            provided_information1
        )
        self.assertEqual(result['status'], False)

        provided_information2 = {
            'key1': 'value1',
            'key2': 'value2'
        }
        result = check_required_information(
            required_information,
            provided_information2
        )
        self.assertEqual(result['status'], True)

from django.test import TestCase
from payment_integrations_app.controllers.dpo import DpoIntegration


# Create your tests here.
class PaymentIntegrationsTestFunctions(TestCase):
    """
    the test functions for the payment integrations app
    """
    def test_verify_token(self):
        dpo_response = DpoIntegration(
            amount=None,
            currency=None,
            msisdn=None,
            transaction_reference=None,
            timestamp=None,
            dpo_transaction_token="CF63B58B-C2C7-473F-A938-50FA956DB346"
        ).verify_token()
        self.assertEquals(dpo_response['status'], 200)

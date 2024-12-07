import uuid
from typing import Any
from django.test import TestCase
from payment_integrations_app.controllers.dpo import DpoIntegration
from payment_integrations_app.controllers.pesapal import Pesapal
from payment_integrations_app.controllers.yo_integrations import YoIntegration


# Create your tests here.
class PaymentIntegrationsTestFunctions(TestCase):
    """
    the test functions for the payment integrations app
    """
    # def test_verify_token(self):
    #     dpo_response = DpoIntegration(
    #         amount=None,
    #         currency=None,
    #         msisdn=None,
    #         transaction_reference=None,
    #         timestamp=None,
    #         dpo_transaction_token="CF63B58B-C2C7-473F-A938-50FA956DB346"
    #     ).verify_token()
    #     self.assertEquals(dpo_response['status'], 200)

    def ttest_pesapal_authenticate(self):
        pesapal_response = Pesapal().authenticate()
        self.assertEquals(pesapal_response['status'], 200)

    def test_yo(self):
        yo_response = YoIntegration().momo_collect(
            transaction_amount=100,
            msisdn='256706087495',
            transaction_id=str(uuid.uuid4())
        )
        self.assertTrue(yo_response)

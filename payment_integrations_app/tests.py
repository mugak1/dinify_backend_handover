from typing import Any
import uuid
from django.utils import timezone
from decouple import config
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
        # dpo_response = DpoIntegration(
        #     amount=None,
        #     currency=None,
        #     msisdn=None,
        #     transaction_reference=None,
        #     timestamp=None,
        #     dpo_transaction_token=''
        # ).verify_token()
        # self.assertEquals(dpo_response['status'], 200)

    def otest_pesapal_authenticate(self):
        pesapal_response = Pesapal().authenticate()
        self.assertEquals(pesapal_response['status'], 200)

    def test_yo(self):
        momo_collect = YoIntegration().momo_collect(
            transaction_amount=100000,
            msisdn=config('TEST_MSISDN'),
            transaction_id=str(uuid.uuid4())
        )
        self.assertTrue(momo_collect)

        momo_check_transaction = YoIntegration().momo_check_transaction(
            yo_transaction_reference=''
        )
        self.assertTrue(momo_check_transaction)

        momo_disburse = YoIntegration().momo_disburse(
            transaction_amount=100,
            msisdn=config('TEST_MSISDN'),
            transaction_id=str(uuid.uuid4())
        )
        self.assertTrue(momo_disburse)

        bank_create_account = YoIntegration().bank_create_verified_account(
            arg_account_name='',
            arg_account_number='',
            arg_bank_name='',
            arg_address_line1='',
            arg_address_line2='',
            arg_city='',
            arg_country='',
        )
        self.assertTrue(bank_create_account)

        bank_disburse = YoIntegration().bank_disburse(
            arg_transaction_id=str(uuid.uuid4()),
            arg_amount=100000,
            arg_account_number='',
            arg_account_identifier='',
            arg_transfer_type=''
        )
        self.assertTrue(bank_disburse)

        bank_check_disbursement = YoIntegration().bank_check_disbursement_status(
            arg_settlement_id=''
        )
        self.assertTrue(bank_check_disbursement)

        send_sms = YoIntegration().send_sms(
            to=config('TEST_SMS_RECIPIENT'),
            message='Dinify SMS test'
        )
        self.assertTrue(send_sms)

    def test_dpo(self):
        dpo_transaction_token = ''
        create_token = DpoIntegration().create_token(
            amount=50000,
            currency='UGX',
            timestamp=str(timezone.now()),
            transaction_reference=str(uuid.uuid4())
        )
        self.assertIsNotNone(create_token)

        verify_token = DpoIntegration().verify_token(
            transaction_reference=str(uuid.uuid4()),
            dpo_token=dpo_transaction_token
        )
        self.assertIsNotNone(verify_token)

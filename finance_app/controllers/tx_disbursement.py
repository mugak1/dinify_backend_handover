from typing import Optional
from restaurants_app.models import Restaurant
from users_app.models import User
from finance_app.models import DinifyAccount, DinifyTransaction
from dinify_backend.configss.string_definitions import (
    TransactionType_Disbursement,
    PaymentMode_MobileMoney, PaymentMode_Bank,
    TransactionPlatform_Web
)
from payment_integrations_app.controllers.yo_integrations import YoIntegration


class DisbursementTransaction:
    def __init__(self):
        pass

    def initiate(
        self,
        user: User,
        amount: int,
        payment_mode: str,
        restaurant_id: Optional[str] = None,
        msisdn: Optional[str] = None,
        bank_account_id: Optional[str] = None,
        otp: Optional[str] = None,
    ) -> dict:
        notes = "tip disbursement"
        account = None

        # TODO check if the user has rights to perform the action
        if restaurant_id is not None:
            restaurant = Restaurant.objects.get(id=restaurant_id)
            account = DinifyAccount.objects.get(restaurant=restaurant)
            notes = "restaurant disbursement"
        else:  # consider that a user is withdrawing their tip collections
            account = DinifyAccount.objects.get(user=user)

        if payment_mode == PaymentMode_MobileMoney:
            msisdn = restaurant.owner.phone_number

        if payment_mode == PaymentMode_Bank:
            if int(amount) < 50000:
                return {
                    'status': 400,
                    'message': 'Sorry, the minimum amount for bank disbursement is UGX 50,000'
                }

        # check if the account has enough balance
        if account.momo_available_balance < amount and account.card_available_balance < amount:
            return {
                'status': 400,
                'message': 'Sorry, you have insufficient funds to make the payment'
            }

        if account is None:
            return {
                'status': 400,
                'message': 'Sorry, an error occurred while processing the transaction'
            }

        disbursement_transaction = DinifyTransaction.objects.create(
            restaurant=restaurant,
            account=account,
            transaction_type=TransactionType_Disbursement,
            transaction_platform=TransactionPlatform_Web,
            transaction_amount=amount,
            msisdn=msisdn,
            payment_mode=payment_mode,
            transaction_notes=notes,
            created_by=user
        )

        if payment_mode == PaymentMode_MobileMoney:
            disbursement = YoIntegration().momo_disburse(
                transaction_amount=amount,
                msisdn=msisdn,
                transaction_id=str(disbursement_transaction.id)
            )
            if disbursement:
                return {
                    'status': 200,
                    'message': 'The disbursement has been initiated successfully.',
                    'data': {
                        "transaction_id": str(disbursement_transaction.id)
                    }
                }
            else:
                return {
                    'status': 400,
                    'message': 'Sorry, an error occurred while initiating the disbursement. Please try again later.',
                    'data': {
                        "transaction_id": str(disbursement_transaction.id)
                    }
                }
        elif payment_mode == PaymentMode_Bank:
            pass
            # TODO determine the account to use i.e UGWARIDMM or UGMTNMM

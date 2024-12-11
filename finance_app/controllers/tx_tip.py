from decimal import Decimal
from django.db import transaction
from psycopg import Transaction
from finance_app.models import DinifyAccount, DinifyTransaction
from orders_app.models import Order
from misc_app.controllers.clean_amount import clean_amount
from users_app.models import User
from dinify_backend.configss.string_definitions import (
    TransactionStatus_Success,
    AccountType_User,
    TransactionType_Tip,
    ProcessingStatus_Done
)
from finance_app.controllers.update_wallet_balance import update_wallet_balance


class TipTransaction:
    def __init__(self):
        pass

    def initiate(self, waiter: User, order_payment: DinifyTransaction, amount: Decimal) -> bool:
        waiter_account = None
        try:
            waiter_account = DinifyAccount.objects.select_for_update().get(
                user=waiter,
            )
        except DinifyAccount.DoesNotExist:
            waiter_account = DinifyAccount.objects.create(
                user=waiter,
                account_type=AccountType_User
            )

        if waiter_account is None:
            raise Exception('No waiter account found')

        balance_update = update_wallet_balance(
            id=str(waiter_account.id),
            mode=order_payment.payment_mode,
            credit=amount
        )

        # record tip transaction
        DinifyTransaction.objects.create(
            account=waiter_account,
            order=order_payment.order,
            transaction_type=TransactionType_Tip,
            transaction_status=TransactionStatus_Success,
            transaction_platform=order_payment.transaction_platform,
            processing_status=ProcessingStatus_Done,

            transaction_amount=amount,
            tip_amount=amount,
            transaction_collected_amount=amount,
            msisdn=order_payment.msisdn,
            payment_form=order_payment.payment_form,
            parent_transaction=order_payment,

            aggregator='Dinify',
            payment_mode=order_payment.payment_mode,
            account_balances=balance_update,

            processed=ProcessingStatus_Done
        )

        return True

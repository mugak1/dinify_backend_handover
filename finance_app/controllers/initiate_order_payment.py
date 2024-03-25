from typing import Optional
from decimal import Decimal
from orders_app.models import Order
from finance_app.models import DinifyAccount, DinifyTransaction
from misc_app.controllers.clean_amount import clean_amount
from dinify_backend.configs import (
    TransactionStatus_Initiated, TransactionType_OrderPayment,
    TransactionPlatform_Web, PaymentMode_Cash, PaymentMode_Card,
    PaymentMode_MobileMoney
)


def initiate_order_payment(
    order: Order,
    payment_mode: str,
    transaction_platform=TransactionPlatform_Web,
    msisdn: Optional[str] = None,
) -> dict:
    """
    Initiates the payment process for an order
    """
    # get the account to consider for the transaction
    account = DinifyAccount.objects.get(restaurant=order.restaurant)

    amount = clean_amount(Decimal(order.actual_cost))

    # determine the amount to collect based on the aggregator charges
    amount_collectable = amount
    if payment_mode is PaymentMode_MobileMoney:
        amount_collectable = amount

    # make a transaction record for the payment
    order_payment = DinifyTransaction.objects.create(
        account=account,
        order=order,
        restaurant=order.restaurant,
        transaction_type=TransactionType_OrderPayment,
        transaction_status=TransactionStatus_Initiated,
        transaction_platform=transaction_platform,
        transaction_amount=amount,
        transaction_collected_amount=amount_collectable,
        msisdn=msisdn,
        payment_mode=payment_mode
    )

    # once created, send out a payment prompt
    if payment_mode == PaymentMode_MobileMoney:
        # send a mobile money prompt
        pass

    return {
        'status': 200,
        'message': 'Order payment has been initiated. Please confirm once prompted.'
    }


from django.core.management.base import BaseCommand
from finance_app.models import DinifyTransaction
from dinify_backend.configss.string_definitions import (
    TransactionType_OrderPayment,
    Aggregator_DPO,
    TransactionStatus_Pending,
    TransactionStatus_Initiated,
    ProcessingStatus_Pending,
    ProcessingStatus_Confirmed,
    ProcessingStatus_Failed
)
from payment_integrations_app.controllers.dpo import DpoIntegration


class Command(BaseCommand):
    help = """
    - Process none pending transactions
    """

    def handle(self, *args, **options):
        pending_transactions = DinifyTransaction.objects.values(
            'id',
            'transaction_type',
            'processing_status',
        ).filter(
            transaction_type=TransactionType_OrderPayment,
            transaction_status__in=[
                TransactionStatus_Pending,
                TransactionStatus_Initiated
            ],
            processing_status__in=[
                ProcessingStatus_Confirmed,
                ProcessingStatus_Failed
            ]
        )

        for txs in pending_transactions:
            if txs.transaction_type == TransactionType_OrderPayment:
                



            dpo_token = txs.aggregator_misc_details['transaction_token']
            DpoIntegration(
                amount=None,
                currency=None,
                msisdn=None,
                transaction_reference=str(txs.id),
                timestamp=None,
                dpo_transaction_token=dpo_token
            ).verify_token()

import logging
from django.db import transaction
from django.db.models import Q
from datetime import date
from restaurants_app.models import Restaurant
from orders_app.models import Order, OrderItem
from finance_app.models import DinifyAccount, DinifyTransaction
from finance_app.serializers import SerializerPutDinifyTransaction

from orders_app.serializers import SerializerPutOrder, SerializerPutOrderItem
from misc_app.controllers.save_to_mongo import save_to_mongodb
import concurrent.futures


def snapshot_daily_orders(restaurant_id: str, eod_date: date) -> dict:
    print(f"Taking snapshot for {restaurant_id} on {eod_date}...")
    with transaction.atomic():
        restaurant = Restaurant.objects.select_for_update().get(id=restaurant_id)
        logging.info(f"Taking snapshot for {restaurant.name}: {restaurant_id}.")
        restaurant_orders = Order.objects.select_for_update().filter(
            restaurant=restaurant,
            eod_record_date=None,
        )

        restaurant_order_items = OrderItem.objects.select_for_update().filter(
            order__in=[order.id for order in restaurant_orders],
        )

        # not used to avod nullable outer joins error
        # restaurant_transactions = DinifyTransaction.objects.select_for_update().filter(
        #     (Q(restaurant=restaurant) | Q(order__restaurant=restaurant)),
        #     eod_record_date=None,
        # )

        res_order_transactions = DinifyTransaction.objects.select_for_update().filter(
            order__in=[order.id for order in restaurant_orders],
            eod_record_date=None,
        )
        res_transactions = DinifyTransaction.objects.select_for_update().filter(
            restaurant=restaurant,
            eod_record_date=None,
        )

        restaurant_transactions = res_order_transactions | res_transactions

        # restaurant_accounts = 
        logging.info(f"{restaurant.name}={restaurant_orders.count()}={restaurant_order_items.count()}={restaurant_transactions.count()}.")

        #  bulk update the restaurant records with the eod date
        for x in restaurant_orders:
            x.eod_record_date = eod_date
        for x in restaurant_order_items:
            x.eod_record_date = eod_date
        for x in restaurant_transactions:
            x.eod_record_date = eod_date

        logging.info('after setting eod_record_date')

        # save each order to the archive i.e. mongo
        for order in restaurant_orders:
            data = SerializerPutOrder(order).data
            save_to_mongodb(
                collection='archive_orders',
                data=data,
                return_id=True
            )
        logging.info(f"Saved {restaurant_orders.count()} orders to archive.")

        # save each order item to the archive
        for order_item in restaurant_order_items:
            data = SerializerPutOrderItem(order_item).data
            save_to_mongodb(
                collection='archive_order_items',
                data=data,
                return_id=True
            )

        # save each transaction to the archive
        for tx in restaurant_transactions:
            data = SerializerPutDinifyTransaction(tx).data
            save_to_mongodb(
                collection='archive_transactions',
                data=data,
                return_id=True
            )

        # save each account to the archive.

        logging.info(f"archived records.")

        Order.objects.bulk_update(
            restaurant_orders,
            fields=['eod_record_date']
        )
        OrderItem.objects.bulk_update(
            restaurant_order_items,
            fields=['eod_record_date']
        )
        DinifyTransaction.objects.bulk_update(
            restaurant_transactions,
            fields=['eod_record_date']
        )

        logging.info('sss')
        # set new system date for the restaurant to allow new orders


def run_restaurant_eod(eod_date: date):
    all_restaurants = Restaurant.objects.all()
    print(all_restaurants.count())

    with concurrent.futures.ThreadPoolExecutor(thread_name_prefix='DinifyEOD') as executor:
        futures = [
            executor.submit(
                snapshot_daily_orders,
                restaurant_id=str(restaurant.id),
                eod_date=eod_date
            )
            for restaurant in all_restaurants
        ]
        # Wait for all threads to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                # Optionally log result
                logging.warning(f"Thread completed with result: {result}")
            except Exception as exc:
                logging.error(f"Thread generated an exception: {exc}")

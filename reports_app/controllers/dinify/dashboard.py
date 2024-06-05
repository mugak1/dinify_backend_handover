# This report gives the Dinify business owners an overview of the performance of the business for the specified time period. It displays:
# Number of restaurants
# New restaurants (during the current calendar month)
# Cumulative Number of Orders 
# Cumulative Order Amount 
# Cumulative Dinify revenue (from restaurant subscriptions and surcharges on the menu items)
# Number of diners
# Monthly active diners (diners who have used Dinify in the last 30 days)
from datetime import datetime, timedelta
from restaurants_app.models import Restaurant
from finance_app.models import DinifyTransaction
from orders_app.models import Order
from django.db.models import Sum
from dinify_backend.configss.string_definitions import TransactionType_Subscription, TransactionType_OrderCharge


def generate_dinify_dashboard():
    restaurants = Restaurant.objects.all()
    orders = Order.objects.all()
    dinify_revenue = DinifyTransaction.objects.filter(
        transaction_type__in=[TransactionType_Subscription, TransactionType_OrderCharge]
    ).aggregate(Sum('transaction_amount'))['transaction_amount__sum']

    new_restaurants = Restaurant.objects.filter(
        time_created__month=datetime.now().month
    )
    cum_num_orders = orders.count()
    cum_order_amount = orders.aggregate(Sum('total_cost'))['total_cost__sum']

    no_diners = orders.values('customer').distinct().count()
    monthly_active_diners = orders.filter(
        time_created__gte=datetime.now() - timedelta(days=30)
    ).values('customer').distinct().count()

    stats = {
        'no_restaurants': restaurants.count(),
        'monthly_new_restaurants': new_restaurants.count(),
        'cum_num_orders': cum_num_orders,
        'cum_order_amount': cum_order_amount,
        'dinify_revenue': dinify_revenue if dinify_revenue else 0.0,
        'no_diners': no_diners,
        'monthly_active_diners': monthly_active_diners
    }
    return {
        'status': 200,
        'message': 'Dinify Dashboard details generated successfully',
        'data': stats
    }

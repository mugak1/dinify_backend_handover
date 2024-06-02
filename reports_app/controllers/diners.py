from datetime import timedelta
from django.db.models import Count, Avg, Sum
from misc_app.controllers.clean_dates import clean_dates
from orders_app.models import Order
from misc_app.controllers.report_support_functions import (
    make_graph_series_data,
    make_month_range,
    make_quarter_range,
    make_annual_range
)


def generate_restaurant_diners_summary(
    restaurant_id: str,
    date_from: str,
    date_to: str,
) -> dict:
    dates = clean_dates(date_from=date_from, date_to=date_to)
    if dates.get('status') != 200:
        return dates
    date_from = dates.get('date_from')
    date_to = dates.get('date_to')

    orders = None

    if date_from == date_to:
        orders = Order.objects.filter(
            restaurant=restaurant_id,
            time_created__date=date_from
        )
    else:
        orders = Order.objects.filter(
            restaurant=restaurant_id,
            time_created__gte=date_from,
            time_created__lte=date_to
        )

    new_diners = orders.values('customer').distinct().count()
    repeat_diners = orders.values('customer').annotate(order_count=Count('id')).filter(order_count__gt=1).count()  # noqa
    most_active_diner = orders.values('customer__first_name').annotate(order_count=Count('id')).order_by('-total_cost').first()  # noqa
    # exclude orders with no customer
    customer_orders = orders.exclude(customer__isnull=True)
    average_sales_amount_per_diner = customer_orders.exclude(
        customer__isnull=True
    ).aggregate(Avg('total_cost'))  # noqa

    stats = {
        'new_diners': new_diners,
        'repeat_diners': repeat_diners,
        'most_active_diner': most_active_diner,
        'average_sales_amount_per_diners': average_sales_amount_per_diner
    }

    return {
        'status': 200,
        'message': 'Diners summary generated successfully',
        'data': stats
    }


def generate_restaurant_diners_listing(
    restaurant_id: str,
    date_from: str,
    date_to: str,
) -> dict:
    dates = clean_dates(date_from=date_from, date_to=date_to)
    if dates.get('status') != 200:
        return dates

    date_from = dates.get('date_from')
    date_to = dates.get('date_to')

    if (date_to - date_from).days > 31:
        return {
            'status': 400,
            'message': 'Date range cannot be greater than 31 days.'
        }

    # get the list of diners
    orders = Order.objects.filter(
        restaurant=restaurant_id,
        time_created__date__gte=date_from,
        time_created__date__lte=date_to
    ).exclude(customer__isnull=True).values('customer').distinct()

    diners = []
    for order in orders:
        customer = order.get('customer')
        customer_orders = Order.objects.filter(
            restaurant=restaurant_id,
            customer=customer
        )
        diner = {
            'id': customer,
            'name': f"{customer.first_name} {customer.last_name}",
            'phone_number': customer.phone_number,
            'email': customer.email,
            'no_orders': customer_orders.count(),
            'total_spend': customer_orders.aggregate(total_spend=Sum('total_cost')).get('total_spend'),
            'average_spend': customer_orders.aggregate(average_spend=Avg('total_cost')).get('average_spend'),
        }
        diners.append(diner)

    return {
        'status': 200,
        'message': 'Diners listing generated successfully',
        'data': diners
    }


def generate_restaurant_diners_trends(
    restaurant_id: str,
    date_from: str,
    date_to: str,
    trend_category: str,
    trend_result: str
) -> dict:
    dates = clean_dates(date_from=date_from, date_to=date_to)
    if dates.get('status') != 200:
        return dates

    date_from = dates.get('date_from')
    date_to = dates.get('date_to')

    if trend_category == 'daily':
        return get_daily_trends(
            restaurant_id=restaurant_id,
            date_from=date_from,
            date_to=date_to,
            trend_result=trend_result
        )
    if trend_category == 'monthly':
        return get_monthly_trends(
            restaurant_id=restaurant_id,
            date_from=date_from,
            date_to=date_to,
            trend_result=trend_result
        )
    if trend_category == 'quarterly':
        return get_quarterly_trends(
            restaurant_id=restaurant_id,
            date_from=date_from,
            date_to=date_to,
            trend_result=trend_result
        )
    if trend_category == 'annual':
        return get_annual_trends(
            restaurant_id=restaurant_id,
            date_from=date_from,
            date_to=date_to,
            trend_result=trend_result
        )


def get_daily_trends(
    restaurant_id: str,
    date_from: str,
    date_to: str,
    trend_result: str
) -> dict:
    x_categories = []
    days = []
    trend_table = []
    trend_graph = []

    day0 = date_from
    while day0 <= date_to:
        days.append(day0)
        x_categories.append(str(day0))
        day0 += timedelta(days=1)

    def get_tabular_trend_data(days: list):
        for day in days:
            summary = generate_restaurant_diners_summary(
                restaurant_id=restaurant_id,
                date_from=day,
                date_to=day
            ).get('data')
            summary['date'] = str(day)
            # remove the most active diner
            summary.pop('most_active_diner')
            trend_table.append(summary)

    def get_graph_trend_data(days: list):
        for day in days:
            summary = generate_restaurant_diners_summary(
                restaurant_id=restaurant_id,
                date_from=day,
                date_to=day
            ).get('data')
            summary['date'] = str(day)
            # remove the most active diner
            summary.pop('most_active_diner')
            trend_graph.append(summary)

    if trend_result == 'table':
        get_tabular_trend_data(days)
        return {
            'status': 200,
            'message': 'Successfully retrieved the daily trend data in tabular format.',
            'data': trend_table
        }
    if trend_result == 'graph':
        get_graph_trend_data(days)
        data = make_graph_series_data(
            x_title='Days',
            y_values=trend_graph,
            x_detail='date'
        )
        return {
            'status': 200,
            'message': 'Successfully retrieved the daily trend data in graph series.',
            'data': data
        }


def get_monthly_trends(
    restaurant_id: str,
    date_from: str,
    date_to: str,
    trend_result: str
) -> dict:
    trend_table = []
    trend_graph = []
    month_range = make_month_range(
        start=date_from,
        end=date_to
    )

    def get_tabular_trend_data():
        for month in month_range:
            summary = generate_restaurant_diners_summary(
                restaurant_id=restaurant_id,
                date_from=month.get('start'),
                date_to=month.get('end')
            ).get('data')
            summary['month'] = month.get('month')
            trend_table.append(summary)

    def get_graph_trend_data():
        for month in month_range:
            summary = generate_restaurant_diners_summary(
                restaurant_id=restaurant_id,
                date_from=month.get('start'),
                date_to=month.get('end')
            ).get('data')
            summary['month'] = month.get('month')
            # remove the most active diner
            summary.pop('most_active_diner')
            trend_graph.append(summary)

    if trend_result == 'table':
        get_tabular_trend_data()
        return {
            'status': 200,
            'message': 'Successfully retrieved the monthly trend data in tabular format.',
            'data': trend_table
        }
    if trend_result == 'graph':
        get_graph_trend_data()
        data = make_graph_series_data(
            x_title='Months',
            y_values=trend_graph,
            x_detail='month'
        )
        return {
            'status': 200,
            'message': 'Successfully retrieved the monthly trend data in graph series.',
            'data': data
        }


def get_quarterly_trends(
    restaurant_id: str,
    date_from: str,
    date_to: str,
    trend_result: str
) -> dict:
    trend_table = []
    trend_graph = []
    quarter_range = make_quarter_range(
        start=date_from,
        end=date_to
    )

    def get_tabular_trend_data():
        for quarter in quarter_range:
            summary = generate_restaurant_diners_summary(
                restaurant_id=restaurant_id,
                date_from=quarter.get('start'),
                date_to=quarter.get('end')
            ).get('data')
            summary['quarter'] = quarter.get('quarter')
            trend_table.append(summary)

    def get_graph_trend_data():
        for quarter in quarter_range:
            summary = generate_restaurant_diners_summary(
                restaurant_id=restaurant_id,
                date_from=quarter.get('start'),
                date_to=quarter.get('end')
            ).get('data')
            summary['quarter'] = quarter.get('quarter')
            # remove the most active diner
            summary.pop('most_active_diner')
            trend_graph.append(summary)

    if trend_result == 'table':
        get_tabular_trend_data()
        return {
            'status': 200,
            'message': 'Successfully retrieved the quarterly trend data in tabular format.',
            'data': trend_table
        }
    if trend_result == 'graph':
        get_graph_trend_data()
        data = make_graph_series_data(
            x_title='Quarters',
            y_values=trend_graph,
            x_detail='quarter'
        )
        return {
            'status': 200,
            'message': 'Successfully retrieved the quarterly trend data in graph series.',
            'data': data
        }

def get_annual_trends(
    restaurant_id: str,
    date_from: str,
    date_to: str,
    trend_result: str
) -> dict:
    trend_table = []
    trend_graph = []
    annual_range = make_annual_range(
        start=date_from,
        end=date_to
    )

    def get_tabular_trend_data():
        for year in annual_range:
            summary = generate_restaurant_diners_summary(
                restaurant_id=restaurant_id,
                date_from=year.get('start'),
                date_to=year.get('end')
            ).get('data')
            summary['year'] = year.get('year')
            trend_table.append(summary)

    def get_graph_trend_data():
        for year in annual_range:
            summary = generate_restaurant_diners_summary(
                restaurant_id=restaurant_id,
                date_from=year.get('start'),
                date_to=year.get('end')
            ).get('data')
            summary['year'] = year.get('year')
            # remove the most active diner
            summary.pop('most_active_diner')
            trend_graph.append(summary)

    if trend_result == 'table':
        get_tabular_trend_data()
        return {
            'status': 200,
            'message': 'Successfully retrieved the annual trend data in tabular format.',
            'data': trend_table
        }
    if trend_result == 'graph':
        get_graph_trend_data()
        data = make_graph_series_data(
            x_title='Years',
            y_values=trend_graph,
            x_detail='year'
        )
        return {
            'status': 200,
            'message': 'Successfully retrieved the annual trend data in graph series.',
            'data': data
        }

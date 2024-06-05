from misc_app.controllers.clean_dates import clean_dates
from orders_app.models import OrderItem
from django.db.models import Count, Sum
from restaurants_app.models import MenuSection, SectionGroup, MenuItem


def generate_restaurant_menu_summary(
    restaurant_id: str,
    grouping: str,
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
            'message': 'Date range should not be greater than 31 days.'
        }

    order_items = None
    sections = None
    groups = None
    items = None
    report = []

    filters = {
        'order__restaurant': restaurant_id
    }

    if date_from == date_to:
        filters['order__time_created__date'] = date_from
    else:
        filters['order__time_created__date__gte'] = date_from
        filters['order__time_created__date__lte'] = date_to

    order_items = OrderItem.objects.filter(**filters)
    # depending on the grouping, get the name, number of orders, order amount,
    # order quantity, peak hours
    if grouping == 'sections':
        # exclude order items that belong to the same order,
        sections = order_items.values('item__section').distinct()
    elif grouping == 'groups':
        groups = order_items.values('item__section_group').distinct()
    else:
        items = order_items.values('item').distinct()

    def handle_section_reports():
        for section in sections:
            if section['item__section'] is not None:
                section = MenuSection.objects.get(id=section['item__section'])
                record = {}
                record['name'] = section.name
                record['number_of_orders_entries'] = order_items.filter(item__section=section).count()
                record['order_amount'] = order_items.filter(
                    item__section=section
                ).aggregate(Sum('total_cost')).get('total_cost__sum')
                record['order_quantity'] = order_items.filter(
                    item__section=section
                ).aggregate(Sum('quantity')).get('quantity__sum')
                record['peak_hours'] = order_items.filter(
                    item__section=section
                ).values('order__time_created__hour').annotate(
                    Count('order__time_created__hour')
                ).order_by('-order__time_created__hour__count').first().get('order__time_created__hour')
                record['most_order_item'] = order_items.filter(
                    item__section=section
                ).values('item__name').annotate(
                    total_quantity=Sum('quantity')
                ).order_by('-total_quantity').first().get('item__name')
                report.append(record)
        return {
            'status': 200,
            'message': 'Menu summary generated successfully',
            'data': report
        }

    def handle_group_reports():
        for group in groups:
            if group['item__section_group'] is not None:
                group = SectionGroup.objects.get(id=group['item__section_group'])
                record = {}
                record['name'] = group.name
                record['number_of_orders_entries'] = order_items.filter(item__section_group=group).count()
                record['order_amount'] = order_items.filter(
                    item__section_group=group
                ).aggregate(Sum('total_cost')).get('total_cost__sum')
                record['order_quantity'] = order_items.filter(
                    item__section_group=group
                ).aggregate(Sum('quantity')).get('quantity__sum')
                record['peak_hours'] = order_items.filter(
                    item__section_group=group
                ).values('order__time_created__hour').annotate(
                    Count('order__time_created__hour')
                ).order_by('-order__time_created__hour__count').first().get('order__time_created__hour')
                record['most_order_item'] = order_items.filter(
                    item__section_group=group
                ).values('item__name').annotate(
                    total_quantity=Sum('quantity')
                ).order_by('-total_quantity').first().get('item__name')
                report.append(record)
        return {
            'status': 200,
            'message': 'Menu summary generated successfully',
            'data': report
        }

    def handle_item_reports():
        for item in items:
            if item['item'] is not None:
                item = MenuItem.objects.get(id=item['item'])
                record = {}
                record['name'] = item.name
                record['number_of_orders_entries'] = order_items.filter(item=item).count()
                record['order_amount'] = order_items.filter(
                    item=item
                ).aggregate(Sum('total_cost')).get('total_cost__sum')
                record['order_quantity'] = order_items.filter(
                    item=item
                ).aggregate(Sum('quantity')).get('quantity__sum')
                record['peak_hours'] = order_items.filter(
                    item=item
                ).values('order__time_created__hour').annotate(
                    Count('order__time_created__hour')
                ).order_by('-order__time_created__hour__count').first().get('order__time_created__hour')
                report.append(record)
        return {
            'status': 200,
            'message': 'Menu summary generated successfully',
            'data': report
        }

    if grouping == 'sections':
        return handle_section_reports()
    elif grouping == 'groups':
        return handle_group_reports()
    else:
        return handle_item_reports()

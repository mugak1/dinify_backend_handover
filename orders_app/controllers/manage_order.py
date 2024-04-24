"""
handle the submission of an order
"""
from datetime import datetime
from typing import Union
from users_app.models import User
from orders_app.models import Order
from dinify_backend.configss.messages import (
    OK_ORDER_UPDATED, ERR_ORDER_UPDATED
)


def update_order_status(
    order: Order,
    new_status: str,
    user: Union[User, None]
) -> dict:
    """
    update an order
    """
    try:
        order.order_status = new_status
        if user is None:
            order.last_updated_by = user
        order.time_last_updated = datetime.now()
        order.save()
        return {
            'status': 200,
            'message': OK_ORDER_UPDATED
        }
    except Exception as error:
        print(f"ErrorUpdateOrderStatus: {error}")
        return {
            'status': 400,
            'message': ERR_ORDER_UPDATED
        }

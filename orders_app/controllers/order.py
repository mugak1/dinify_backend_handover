from dataclasses import dataclass
from orders_app.controllers.initiate_order import initiate_order
from orders_app.controllers.submit_order import submit_order


@dataclass
class Order:
    data: dict

    def initiate_order(self):
        """
        Initiates a new order
        """
        return initiate_order(self.data)

    def submit_order(self):
        """
        submits an order that has been initiated
        """
        return submit_order(self.data)

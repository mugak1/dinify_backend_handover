"""
the controller class for misc logic
"""
from misc_app.controllers.check_required_information import check_required_information


class MiscController:
    """
    the controller class for misc logic
    """
    def __init__(self, data):
        self.data = data

    def check_required_information(self):
        """
        check if the required information is present
        """
        return check_required_information(
            self.data['required_information'],
            self.data['provided_information']
        )

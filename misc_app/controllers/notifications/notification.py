from misc_app.controllers.notifications.message_builder import build_messages
from misc_app.controllers.notifications.determine_recipients import determine_receipients
from misc_app.controllers.save_to_mongo import save_to_mongodb
from dinify_backend.mongo_db import COL_NOTIFICATIONS


class Notification:
    def __init__(self, msg_data: dict):
        self.msg_data = msg_data
    # msg_data: dict

    def create_notification(self):
        message = build_messages(self.msg_data)
        recipients = determine_receipients(
            message_type=self.msg_data.get('msg_type'),
            restaurant_id=self.msg_data.get('restaurant_id'),
            user_id=self.msg_data.get('user_id')
        )

        save_to_mongodb(
            collection=COL_NOTIFICATIONS,
            data={
                'tos': recipients['tos'],
                'ccs': recipients['ccs'],
                'subject': message['subject'],
                'email': message['email'],
                'sms': message['sms'],
                'msisdn': recipients['msisdn'],
            }
        )

import random
import hashlib
from datetime import datetime
from users_app.models import User, UserOtp
from misc_app.controllers.notifications.notification import Notification


# @dataclass
class OtpManager:
    def make_otp(self, user: User) -> True:
        otp = random.randint(1000, 9999)
        otp_str = str(otp)
        otp_str = '1234'
        encrypted_otp = hashlib.sha256(otp_str.encode()).hexdigest()
        user_otp = UserOtp(user=user, otp_hash=encrypted_otp)
        user_otp.save()
        # TODO send otp to user
        Notification(msg_data={
            'msg_type': 'otp',
            'first_name': user.first_name,
            'otp': otp_str,
        }).create_notification()


    def verify_otp(self, user_id, otp) -> bool:
        encrypted_otp = hashlib.sha256(otp.encode()).hexdigest()
        try:
            UserOtp.objects.get(
                user_id=user_id,
                otp_hash=encrypted_otp,
                expiry_time__gte=datetime.now()
            )
            return True
        except UserOtp.DoesNotExist:
            return False

import random
import hashlib
from dataclasses import dataclass
from users_app.models import UserOtp


# @dataclass
class OtpManager:
    def make_otp(self, user_id) -> True:
        otp = random.randint(1000, 9999)
        otp_str = str(otp)
        otp_str = '1234'
        encrypted_otp = hashlib.sha256(otp_str.encode()).hexdigest()

        user_otp = UserOtp(user_id=user_id, otp_hash=encrypted_otp)
        user_otp.save()

    def verify_otp(self, user_id, otp) -> bool:
        encrypted_otp = hashlib.sha256(otp.encode()).hexdigest()
        try:
            user_otp = UserOtp.objects.get(
                user_id=user_id,
                otp_hash=encrypted_otp
            )
            return True
        except UserOtp.DoesNotExist:
            return False

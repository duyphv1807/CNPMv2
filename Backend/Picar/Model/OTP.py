from datetime import datetime, timedelta
import random
from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Utils.GenerateID import generate_id

class OTP():
    def __init__(self, email, otpid: str = None):
        self._otpid = otpid if otpid else generate_id("PAY")
        self._email = email
        self._otp_code = str(random.randint(100000, 999999))
        self._expiry_time = datetime.now() + timedelta(minutes=5)
        self._is_used = False

    # --- GETTERS / SETTERS ---
    @property
    def otpid(self):
        return self._otpid

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def otp_code(self):
        return self._otp_code

    @otp_code.setter
    def otp_code(self, value):
        # Lưu dưới dạng chuỗi để tránh mất số 0 ở đầu
        self._otp_code = str(value)

    @property
    def expiry_time(self):
        return self._expiry_time

    @property
    def is_used(self):
        return self._is_used

    @is_used.setter
    def is_used(self, value: bool):
        self._is_used = value

    # --- METHODS ---

    def to_dict(self):
        """Chuyển đổi đối tượng sang dictionary để insert vào Supabase"""
        return {
            "Email": self._email,
            "OTPCode": self._otp_code,
            "ExpiryTime": self._expiry_time.isoformat(),
            "IsUsed": self._is_used
        }

    def save_to_database(self):
        """Lưu bản ghi OTP vào bảng 'OTP' trên Supabase"""
        try:
            # Tên bảng phải khớp chính xác với tên bạn đặt trên Supabase
            response = supabase.table("OTP").insert(self.to_dict()).execute()
            if response.data:
                self._otpid = response.data[0].get("OTPID")
                print(f"--> [DATABASE] Lưu OTP thành công cho: {self._email}")
                return True
            return False
        except Exception as e:
            print(f"--> [ERROR] Lỗi khi lưu OTP: {e}")
            return False

    @staticmethod
    def verify_otp(email, user_code):
        """Phương thức tĩnh để kiểm tra mã OTP người dùng nhập vào"""
        try:
            # Tìm mã mới nhất, chưa dùng của email này
            res = supabase.table("OTP") \
                .select("*") \
                .order("CreatedAt", desc=True) \
                .eq("Email", email) \
                .eq("IsUsed", False) \
                .limit(1) \
                .execute()

            if not res.data:
                return False, "Không tìm thấy mã OTP!"

            record = res.data[0]
            # Kiểm tra thời gian hết hạn
            expiry = datetime.fromisoformat(record['ExpiryTime'].replace('Z', '+00:00'))
            if datetime.now().astimezone() > expiry.astimezone():
                return False, "Mã OTP đã hết hạn!"

            # So sánh mã
            if record['OTPCode'] == str(user_code):
                # Đánh dấu đã sử dụng
                supabase.table("OTP").update({"IsUsed": True}).eq("OTPID", record['OTPID']).execute()
                return True, "Xác thực thành công!"

            return False, "Mã OTP không chính xác!"
        except Exception as e:
            return False, f"Lỗi xác thực: {str(e)}"
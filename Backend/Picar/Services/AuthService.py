import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import bcrypt

from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Model.OTP import OTP

class AuthService:
    @staticmethod
    async def request_otp_reset_password(contact):
        # 1. Nhận diện Email hay SĐT
        is_email = re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', contact)
        is_phone = re.match(r'^0\d{9,10}$', contact)

        if not is_email and not is_phone:
            return False, "Định dạng không hợp lệ!"

        # 2. Kiểm tra tài khoản có tồn tại trong Supabase không
        # Giả sử bạn dùng bảng User_Admin
        from Backend.Picar.ExcuteDatabase import supabase
        user_check = supabase.table("User_Admin") \
            .select("*") \
            .or_(f"Email.eq.{contact},PhoneNumber.eq.{contact}") \
            .execute()

        new_otp = OTP(email=contact)

        # 4. Lưu vào bảng OTP trên Supabase
        if not new_otp.save_to_database():
            return False, "Lỗi hệ thống: Không thể khởi tạo mã xác thực."

        # 5. Lấy mã vừa tạo từ Object để gửi đi
        otp_code = new_otp.otp_code

        if not user_check.data:
            return False, "Tài khoản không tồn tại trên hệ thống!"


        # 5. Gửi OTP thật
        if is_email:
            return await AuthService.send_email_otp(contact, otp_code)
        else:
            return await AuthService.send_sms_otp(contact, otp_code)

    @staticmethod
    async def send_email_otp(email, code, sender = "picarthelocal@gmail.com",sender_password = "sxye qwfm hwyp pigw"):

        try:
            # 1. Thiết lập nội dung Email
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = email
            msg['Subject'] = f"[{code}] Mã xác thực khôi phục mật khẩu PiCar"

            html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 400px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #4DB6AC; text-align: center;">PiCar Verification</h2>
                    <p>Chào bạn,</p>
                    <p>Bạn đang thực hiện yêu cầu khôi phục mật khẩu tài khoản Picar. Mã OTP của bạn là:</p>
                    <div style="background: #f4f4f4; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #333;">
                        {code}
                    </div>
                    <p style="font-size: 12px; color: #888;">Mã này sẽ hết hạn sau 6 phút. Vui lòng không chia sẻ mã này cho bất kỳ ai.</p>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p style="font-size: 10px; text-align: center; color: #aaa;">Đây là tin nhắn tự động, vui lòng không phản hồi.</p>
                </div>
                """
            msg.attach(MIMEText(html_content, 'html'))

            # 2. Kết nối và gửi qua Server Gmail
            # Sử dụng 'with' để đảm bảo đóng kết nối an toàn
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()  # Bảo mật kết nối
                server.login(sender, sender_password)
                server.send_message(msg)

            print(f"--> [SUCCESS] Email OTP sent to {email}")
            return True, "Mã OTP đã được gửi vào Email của bạn."

        except Exception as e:
            print(f"--> [ERROR] Email failed: {str(e)}")
            return False, f"Lỗi gửi Email: {str(e)}"

    @staticmethod
    async def send_sms_otp(phone, code):
        access_token = "fLzZo_NW5AwDOqnAQeCIrpzMOMyuIJQQ"
        content = f"Mã OTP PiCar của bạn là {code}. Có hiệu lực trong 6 phút. Vui lòng không chia sẽ mã này."
        # Endpoint API của SpeedSMS
        url = "https://api.speedsms.vn/index.php/sms/send"
        params = {
            "access-token": access_token,
            "to": phone,
            "content": content,
            "type": 3  # Type 2: Tin nhắn CSKH/OTP (Ưu tiên gửi nhanh)
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()

            if data.get("status") == "success":
                print(f"--> [SPEEDSMS] Đã gửi OTP đến {phone}")
                return True, "Mã OTP đã gửi qua SMS."
            else:
                return False, f"SpeedSMS báo lỗi: {data.get('message')}"
        except Exception as e:
            return False, f"Lỗi kết nối API: {str(e)}"

    # @staticmethod
    # async def send_sms_otp(phone, code):
    #     print(f"[MOCK SMS] OTP gửi tới {phone}: {code}")
    #     return True, "OTP mocked (DEV MODE)"

    @staticmethod
    async def update_password(contact, new_password):
        from Backend.Picar.ExcuteDatabase import supabase

        # 🔐 HASH PASSWORD
        hashed = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        result = supabase.table("User_Admin") \
            .update({"Password": hashed}) \
            .or_(f'Email.eq."{contact}",PhoneNumber.eq."{contact}"') \
            .execute()

        print("UPDATE RESULT:", result.data)
        return bool(result.data)

    @staticmethod
    async def get_user_by_id(user_id):
        try:
            # SỬA: Dùng bảng User_Admin và lấy đúng các cột
            res = supabase.table("User_Admin") \
                .select("UserID, FullName, Email, PhoneNumber, DateOfBirth, Avatar") \
                .eq("UserID", user_id) \
                .execute()

            if not res.data or len(res.data) == 0:
                return None
            return res.data[0]
        except Exception as e:
            print(f"--- [ERROR get_user_by_id]: {str(e)}")
            return None

    #======== PHẦN FIX CẬP NHẬT TÀI KHOẢN ==============
    @staticmethod
    async def update_user(user_id, update_data):
        try:
            # SỬA QUAN TRỌNG: Đổi Users thành User_Admin để khớp với DB
            response = supabase.table("User_Admin") \
                .update(update_data) \
                .eq("UserID", user_id) \
                .execute()

            if response.data:
                print(f"--- [SUPABASE] Cập nhật thành công cho ID: {user_id} ---")
                return True

            print(f"--- [SUPABASE] Không tìm thấy dòng nào để update cho ID: {user_id} ---")
            return False

        except Exception as e:
            # In ra lỗi chi tiết nếu tên cột sai (ví dụ: FullName vs Full_Name)
            print(f"--- [SUPABASE ERROR]: {str(e)} ---")
            return False


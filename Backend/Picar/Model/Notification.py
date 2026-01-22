from datetime import date
from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Model.User import User
from Backend.Picar.Model.Booking import Booking
from Backend.Picar.Model.Payment import Payment
from Backend.Picar.Model.Feedback import Feedback
from Backend.Picar.Utils.GenerateID import generate_id

class Notification:
    TYPES = {
        "BOOKING": "Thông báo liên quan đến đặt xe",
        "PAYMENT": "Thông báo về giao dịch thanh toán",
        "FEEDBACK": "Thông báo về đánh giá dịch vụ",
        "SYSTEM": "Thông báo từ hệ thống"
    }

    def __init__(self, receiver: User, content: str,
                 notification_type: str,
                 booking: Booking = None,
                 payment: Payment = None,
                 feedback: Feedback = None,
                 is_read: bool = False, create_date: date = None, notification_id: str = None):

        self._notification_id = notification_id if notification_id else generate_id("NO")
        self._receiver = receiver
        self._content = content

        # Lưu các thuộc tính dưới dạng Object
        self._booking = booking
        self._payment = payment
        self._feedback = feedback

        self.notification_type = notification_type
        self._is_read = is_read
        self._create_date = create_date if create_date else date.today()

    # --- GETTER / SETTER ĐẦY ĐỦ ---

    @property
    def notification_id(self):
        return self._notification_id

    @notification_id.setter
    def notification_id(self, value: str):
        self._notification_id = value

    @property
    def receiver(self):
        return self._receiver

    @receiver.setter
    def receiver(self, value: User):
        if isinstance(value, User):
            self._receiver = value
        else:
            raise ValueError("Receiver phải là một đối tượng User!")

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value: str):
        if value and len(value.strip()) > 0:
            self._content = value
        else:
            raise ValueError("Nội dung thông báo không được để trống!")

    @property
    def notification_type(self):
        return self._type

    @notification_type.setter
    def notification_type(self, value: str):
        upper_val = value.upper()
        if upper_val not in self.TYPES:
            valid_types = ", ".join(self.TYPES.keys())
            raise ValueError(f"Loại '{value}' không hợp lệ! Phải thuộc: {valid_types}")
        self._type = upper_val

    @property
    def is_read(self):
        return self._is_read

    @is_read.setter
    def is_read(self, value: bool):
        if isinstance(value, bool):
            self._is_read = value
        else:
            raise ValueError("is_read phải là kiểu Boolean (True/False)")

    @property
    def create_date(self):
        return self._create_date

    @property
    def booking_id(self):
        return self._booking.booking_id if self._booking else None

    @property
    def payment_id(self):
        return self._payment.payment_id if self._payment else None

    @property
    def feedback_id(self):
        return self._feedback.feedback_id if self._feedback else None

    # --- DATABASE METHODS ---

    def to_dict(self):
        """Map dữ liệu từ các Object ra ID để lưu vào Database"""
        return {
            "NotificationID": self._notification_id,
            "UserID": self.receiver.user_id,
            "BookingID": self.booking_id,
            "PaymentID": self.payment_id,
            "FeedbackID": self.feedback_id,
            "Content": self._content,
            "Type": self._type,
            "IsRead": self._is_read,
            "CreateDate": str(self._create_date)
        }

    def save_to_db(self):
        max_retries = 3
        attempts = 0
        while attempts < max_retries:
            try:
                return supabase.table("Notification").insert(self.to_dict()).execute()
            except Exception as e:
                if "duplicate key value" in str(e).lower() or "23505" in str(e):
                    print(f"⚠️ Trùng mã {self._notification_id}, đang tạo mã mới...")
                    # Tạo mã mới và thử lại
                    self._notification_id = generate_id("US")
                    attempts += 1
                else:
                    # Nếu là lỗi khác (mất mạng, sai cột...) thì báo lỗi ngay
                    print(f"❌ Lỗi Database: {e}")
                    return None

    def mark_as_read(self):
        """Cập nhật nhanh trạng thái đã đọc"""
        self.is_read = True
        return self.save_to_db()

    def display_short(self):
        status = "READ" if self._is_read else "UNREAD"
        return f"[{status}][{self._type}] {self._content[:30]}..."
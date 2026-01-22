from datetime import date
from Backend.Picar.Model.User import User
from Backend.Picar.Model.Booking import Booking
from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Utils.GenerateID import generate_id

class Feedback:
    def __init__(self, booking: Booking, sender: User,
                 receiver: User, rating: int = 5, comment: str = "", create_date: date = None, feedback_id: str = None):

        self._feedback_id = feedback_id if feedback_id else generate_id("FE")

        # Ở ĐÂY: Gọi nguyên Object booking thay vì chỉ truyền ID
        self._booking = booking

        self._sender = sender
        self._receiver = receiver

        # Dùng setter để kiểm tra dữ liệu
        self._rating = rating
        self.comment = comment
        self._create_date = create_date if create_date else date.today()

    # --- GETTER / SETTER ĐẦY ĐỦ ---

    @property
    def feedback_id(self):
        return self._feedback_id

    @feedback_id.setter
    def feedback_id(self, value: str):
        self._feedback_id = value

    @property
    def booking(self):
        return self._booking

    @booking.setter
    def booking(self, value: Booking):
        if isinstance(value, Booking):
            self._booking = value
        else:
            raise ValueError("Phải truyền vào một đối tượng booking!")

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value: User):
        self._sender = value

    @property
    def receiver(self):
        return self._receiver

    @receiver.setter
    def receiver(self, value: User):
        self._receiver = value

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value: int):
        if 1 <= value <= 5:
            self._rating = value
        else:
            raise ValueError("Rating phải từ 1 đến 5 sao!")

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, value: str):
        self._comment = value.strip() if value and value.strip() else "Người dùng không nhận xét."

    @property
    def create_date(self):
        return self._create_date

    # --- DATABASE METHODS ---

    def to_dict(self):
        """Trích xuất ID từ tất cả các Object liên quan"""
        return {
            "FeedbackID": self._feedback_id,
            "BookingID": self._booking.booking_id,  # Lấy ID từ Obj booking
            "SenderID": self._sender.user_id,
            "ReceiverID": self._receiver.user_id,
            "Rating": self._rating,
            "Comment": self._comment,
            "CreateDate": str(self._create_date)
        }

    def save_to_db(self):
        max_retries = 3
        attempts = 0
        while attempts < max_retries:
            try:
                return supabase.table("Feedback").insert(self.to_dict()).execute()
            except Exception as e:
                if "duplicate key value" in str(e).lower() or "23505" in str(e):
                    print(f"⚠️ Trùng mã {self._feedback_id}, đang tạo mã mới...")
                    # Tạo mã mới và thử lại
                    self._feedback_id = generate_id("US")
                    attempts += 1
                else:
                    # Nếu là lỗi khác (mất mạng, sai cột...) thì báo lỗi ngay
                    print(f"❌ Lỗi Database: {e}")
                    return None

    def display_full_details(self):
        """Lợi ích của việc gọi Object: Lấy được cả thông tin từ booking và Booking"""
        return (f"Feedback cho đơn hàng: {self._booking.booking_id}\n"
                f"Người đánh giá: {self._sender.full_name}\n"
                f"Đánh giá cho: {self._receiver.full_name}\n"
                f"Nội dung: {self._rating}★]: {self._comment}")

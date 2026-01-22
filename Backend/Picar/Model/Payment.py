from datetime import date
from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Model.Booking import Booking
from Backend.Picar.Utils.GenerateID import generate_id
class Payment:
    # Whitelist các phương thức và trạng thái
    METHODS = ["ONLINE", "DIRECT", "WALLET"]
    STATUSES = ["PENDING", "SUCCESS", "FAILED", "REFUNDED"]

    def __init__(self, booking: Booking,
                 payment_method: str = "DIRECT", status: str = "PENDING",
                 payment_date: date = None, payment_id: str = None):

        self._payment_id = payment_id if payment_id else generate_id("PAY")
        self._booking = booking

        # Số tiền tự động lấy từ Booking nếu không truyền thủ công
        self._amount = booking.total_price

        self.payment_method = payment_method
        self.status = status
        self._payment_date = payment_date if payment_date else date.today()

    # --- GETTER / SETTER CHO CÁC THUỘC TÍNH ---
    @property
    def payment_id(self):
        return self._payment_id

    @property
    def booking(self):
        return self._booking

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value: float):
        if value < 0:
            raise ValueError("Số tiền thanh toán không thể âm!")
        self._amount = value

    @property
    def payment_method(self):
        return self._payment_method

    @payment_method.setter
    def payment_method(self, value: str):
        val = value.upper()
        if val in self.METHODS:
            self._payment_method = val
        else:
            raise ValueError(f"Phương thức phải thuộc: {self.METHODS}")

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        val = value.upper()
        if val in self.STATUSES:
            self._status = val
        else:
            raise ValueError(f"Trạng thái phải thuộc: {self.STATUSES}")

    @property
    def payment_date(self):
        return self._payment_date

    # --- HELPER METHODS ---
    def display_amount(self):
        """Hiển thị định dạng tiền tệ đẹp"""
        return f"{self._amount:,.0f} VND"

    def receipt(self):
        """Tạo biên lai tóm tắt"""
        return (f"Mã GD: {self._payment_id} | "
                f"Khách: {self._booking.renter.full_name} | "
                f"Số tiền: {self.display_amount()} | "
                f"Trạng thái: {self._status}")

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Trích xuất ID từ Object Booking để lưu vào Database"""
        return {
            "PaymentID": self._payment_id,
            "BookingID": self._booking.booking_id,  # Lấy ID từ Obj Booking
            "Amount": self._amount,
            "PaymentMethod": self._payment_method,
            "Status": self._status,
            "PaymentDate": str(self._payment_date)
        }

    def save_to_db(self):
        max_retries = 3
        attempts = 0
        while attempts < max_retries:
            try:
                return supabase.table("Payment").insert(self.to_dict()).execute()
            except Exception as e:
                if "duplicate key value" in str(e).lower() or "23505" in str(e):
                    print(f"⚠️ Trùng mã {self._payment_id}, đang tạo mã mới...")
                    # Tạo mã mới và thử lại
                    self._payment_id = generate_id("US")
                    attempts += 1
                else:
                    # Nếu là lỗi khác (mất mạng, sai cột...) thì báo lỗi ngay
                    print(f"❌ Lỗi Database: {e}")
                    return None

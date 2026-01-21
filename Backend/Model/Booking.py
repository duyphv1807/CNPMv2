from datetime import date
from Backend.ExcuteDatabase import supabase
from Backend.Model.User import User
from Backend.Model.Vehicle import Vehicle
from Backend.Helpers import generate_id

class Booking:
    def __init__(self, renter: User, owner: User, vehicle: Vehicle,
                 start_date: date, end_date: date,
                 is_returned: bool = False, status: str = "PENDING", booking_id: str = None):

        # Các thuộc tính Private (_)
        self._booking_id = booking_id if booking_id else generate_id("BO")
        self._renter = renter  # Đối tượng User thuê
        self._owner = owner  # Đối tượng User chủ xe
        self._vehicle = vehicle  # Đối tượng Vehicle
        self._start_date = start_date
        self._end_date = end_date
        self._is_returned = is_returned
        self._status = status.upper()

        # Tự động tính tổng tiền khi khởi tạo
        self._total_price = self.calculate_total_price()

    # --- LOGIC TÍNH TIỀN ---
    def calculate_total_price(self) -> int:
        """Tính tiền dựa trên số ngày và giá thuê của xe"""
        delta = self._end_date - self._start_date
        days = max(delta.days, 1)  # Nếu thuê và trả trong ngày vẫn tính 1 ngày
        return int(days * self._vehicle.rental_price)

    # --- GETTERS / SETTERS ---

    @property
    def booking_id(self):
        return self._booking_id

    @booking_id.setter
    def booking_id(self, value: str):
        self._booking_id = value

    @property
    def renter(self):
        return self._renter

    @property
    def owner(self):
        return self._owner

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value: date):
        self._start_date = value
        self._total_price = self.calculate_total_price()

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value: date):
        if value < self._start_date:
            raise ValueError("Ngày kết thúc không thể trước ngày bắt đầu!")
        self._end_date = value
        self._total_price = self.calculate_total_price()

    @property
    def is_returned(self):
        return self._is_returned

    @is_returned.setter
    def is_returned(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError("is_returned phải là kiểu Boolean")
        self._is_returned = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: str):
        allowed = ["PENDING", "CONFIRMED", "CANCELLED", "COMPLETED"]
        if value.upper() in allowed:
            self._status = value.upper()
        else:
            raise ValueError(f"Status phải thuộc: {allowed}")

    @property
    def total_price(self):
        return self._total_price

    # --- DATABASE METHODS ---
    def to_dict(self):
        """
        Chuyển đổi từ Object sang ID để lưu vào Database.
        Lưu ý: Map đúng tên cột PascalCase trong Database của bạn.
        """
        return {
            "BookingID": self._booking_id,
            "RenterID": self._renter.user_id,     # Trích xuất ID từ Object User
            "OwnerID": self._owner.user_id,       # Trích xuất ID từ Object User
            "VehicleID": self._vehicle.vehicle_id, # Trích xuất ID từ Object Vehicle
            "StartDate": str(self._start_date),
            "EndDate": str(self._end_date),
            "TotalPrice": self._total_price,
            "IsReturned": self._is_returned,
            "Status": self._status
        }

    def save_to_db(self):
        max_retries = 3
        attempts = 0
        while attempts < max_retries:
            try:
                return supabase.table("Booking").insert(self.to_dict()).execute()
            except Exception as e:
                if "duplicate key value" in str(e).lower() or "23505" in str(e):
                    print(f"⚠️ Trùng mã {self._booking_id}, đang tạo mã mới...")
                    # Tạo mã mới và thử lại
                    self._booking_id = generate_id("CO")
                    attempts += 1
                else:
                    # Nếu là lỗi khác (mất mạng, sai cột...) thì báo lỗi ngay
                    print(f"❌ Lỗi Database: {e}")
                    return None
























































































































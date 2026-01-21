from datetime import date
from Backend.ExcuteDatabase import supabase
from Backend.Model.Booking import Booking
from Backend.Helpers import generate_id

class Contract:
    def __init__(self, booking: Booking, content: str = "", create_date: date = None, contract_id: str = None):
        self._contract_id = contract_id if contract_id else generate_id("CO")
        self._booking = booking  # Nhận nguyên Object Booking

        # Nếu content trống, có thể tự động tạo bản nháp sơ bộ từ thông tin Booking
        if not content:
            self._content = self.generate_default_content()
        else:
            self._content = content

        self._create_date = create_date if create_date else date.today()

    def generate_default_content(self) -> str:
        """Tự động tạo nội dung hợp đồng từ dữ liệu Booking"""
        return (f"HỢP ĐỒNG THUÊ XE\n"
                f"Mã đơn hàng: {self._booking.booking_id}\n"
                f"Bên cho thuê: {self._booking.owner.full_name}\n"
                f"Bên thuê: {self._booking.renter.full_name}\n"
                f"Xe: {self._booking.vehicle.name} | Biển số: {self._booking.vehicle.license_plate}\n"
                f"Tổng tiền: {self._booking.total_price:,} VND")
    # --- GETTER / SETTER ĐẦY ĐỦ ---
    @property
    def contract_id(self):
        return self._contract_id

    @contract_id.setter
    def contract_id(self, value: str):
        self._contract_id = value

    @property
    def booking(self):
        return self._booking

    @booking.setter
    def booking(self, value: Booking):
        if not isinstance(value, Booking):
            raise ValueError("Phải truyền vào một đối tượng Booking!")
        self._booking = value

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value: str):
        if value and len(value.strip()) > 10:
            self._content = value
        else:
            raise ValueError("Nội dung hợp đồng quá ngắn hoặc trống!")

    @property
    def create_date(self):
        return self._create_date

    @create_date.setter
    def create_date(self, value: date):
        self._create_date = value

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Map trích xuất ID từ Object Booking để lưu vào DB"""
        return {
            "ContractID": self._contract_id,
            "BookingID": self._booking.booking_id,  # Lấy ID từ Obj
            "Content": self._content,
            "CreateDate": str(self._create_date)
        }

    def save_to_db(self):
        max_retries = 3
        attempts = 0
        while attempts < max_retries:
            try:
                return supabase.table("Contract").insert(self.to_dict()).execute()
            except Exception as e:
                if "duplicate key value" in str(e).lower() or "23505" in str(e):
                    print(f"⚠️ Trùng mã {self._contract_id}, đang tạo mã mới...")
                    # Tạo mã mới và thử lại
                    self._contract_id = generate_id("CO")
                    attempts += 1
                else:
                    # Nếu là lỗi khác (mất mạng, sai cột...) thì báo lỗi ngay
                    print(f"❌ Lỗi Database: {e}")
                    return None

    def display_contract(self):
        """Hiển thị bản tóm tắt hợp đồng"""
        return f"Hợp đồng: {self._contract_id} | Ngày ký: {self._create_date} | Đơn: {self._booking.booking_id}"
from Backend.Model.User import User
from datetime import date
from Backend.Helpers import generate_id
from Backend.ExcuteDatabase import supabase

class Admin(User):
    def __init__(self, full_name: str, nation_id: str, date_of_birth: date,
                 phone_number: str, email: str, driving_license: str, password: str,
                 avatar: str, number_vehicle_own: int = 5, star: int = 5, user_id: str = None, admin_id: int = None):

        # Gọi hàm khởi tạo của class cha (User)
        super().__init__(full_name, nation_id, date_of_birth, phone_number,
                         email, driving_license, password, avatar, number_vehicle_own, star,user_id, )

        self.admin_id = admin_id if admin_id else generate_id("AD")

    @property
    def admin_id(self):
        return self._admin_id

    @admin_id.setter
    def admin_id(self, value: str):
        if len(value) != 10:
            raise ValueError("AdminID phải có đúng 10 ký tự!")
        self._admin_id = value

    # --- OVERRIDE TO_DICT ---
    def to_dict(self):
        data = super().to_dict()  # Lấy bộ khung từ User
        data.update({
            "ClassifyUser": "ADMIN",
            "AdminID": self.admin_id
        })
        return data

    # --- OVERIDING ---
    def save_to_db(self):
        attempts = 0
        max_retries = 3
        while attempts < max_retries:
            try:
                # Lưu vào bảng User_Admin (hoặc bảng User tùy thiết kế của bạn)
                return supabase.table("User_Admin").insert(self.to_dict()).execute()

            except Exception as e:
                error_msg = str(e)
                # Check mã lỗi 23505 (Trùng Primary Key/Unique ID)
                if "23505" in error_msg or "duplicate key value" in error_msg.lower():
                    attempts += 1
                    # Sinh lại mã mới với tiền tố AD
                    new_id = generate_id("AD")
                    print(f"⚠️ Trùng UserID! Đang đổi từ {self._user_id} sang {new_id}")
                    self._user_id = new_id
                else:
                    print(f"❌ Lỗi khác: {error_msg}")
                    return None
        return None

    # Ghi đè phương thức info
    def info(self):
        # Sử dụng self.full_name (snake_case) thay vì FullName
        return f"[ADMIN Level {self.admin_id}] {self.full_name} - Email: {self._email}"
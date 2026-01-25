from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Model.User import User
from Backend.Picar.Model.Transaction import Transaction

class Wallet:
    def __init__(self, owner: User, balance: int = 0, currency: str = "VNĐ"):
        # Lưu cả đối tượng User để dùng dữ liệu khi cần
        self._owner = owner
        # Ép kiểu int để khớp với int8 trong Database
        self._balance = int(balance) if balance >= 0 else 0
        self._currency = currency

    # --- GETTER ---
    @property
    def balance(self):
        return self._balance

    # --- HÀM HIỂN THỊ ---
    def display_balance(self):
        """Ví dụ: 1.000.000 VNĐ"""
        return f"{self._balance:,.0f} {self._currency}"

    # --- NGHIỆP VỤ ---
    def add_funds(self, amount: int):
        if amount > 0:
            self._balance += int(amount)
            return True
        return False

    def deduct_funds(self, amount: int):
        if 0 < amount <= self._balance:
            self._balance -= int(amount)
            return True
        return False

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Phải khớp chính xác với tên cột trên Supabase (UserID, Balance, Currency)"""
        return {
            "UserID": self._owner.user_id, # Cột UserID trên DB
            "Balance": self._balance,      # Cột Balance
            "Currency": self._currency     # Cột Currency
        }

    def create_wallet(self):
        try:
            # Giả sử self.user_id đã có giá trị từ Class User
            return supabase.table("Wallet").insert({
                "UserID": self._owner.user_id,
                "Balance": 0
            }).execute()
        except Exception as e:
            if "23505" in str(e):
                print(f"❌ Lỗi: User {self._owner.user_id} đã sở hữu một ví rồi!")
            return None

    # === Hàm Nạp tiền ===
    def deposit(self, amount: int):
        # Kiểm tra số tiền nạp phải lớn hơn 0
        if amount <= 0:
            return False, "Invalid amount"

        # Cập nhật số dư trong object
        balance_before = self._balance
        balance_after = balance_before + int(amount)

        try:
            # Cập nhật số dư mới lên bảng Wallet
            supabase.table("Wallet").update({
                "Balance": balance_after
            }).eq("UserID", self._owner.user_id).execute()

            # Ghi lịch sử giao dịch (nạp tiền)
            Transaction.create(
                user_id=self._owner.user_id,
                amount=amount,
                tx_type="DEPOSIT",
                balance_before=balance_before,
                balance_after=balance_after,
                note="User deposited money"
            )

            # Trả về thành công và số dư hiện tại
            self._balance = balance_after
            return True, balance_after

        except Exception as e:
            return False, str(e)

    # === Hàm Rút tiền ===
    def withdraw(self, amount: int):
        # Kiểm tra số tiền rút phải lớn hơn 0
        if amount <= 0:
            return False, "Invalid amount"

        # Kiểm tra số dư có đủ để rút không
        if amount > self._balance:
            return False, "Insufficient balance"

        # Trừ tiền trong object
        balance_before = self._balance
        balance_after = balance_before - int(amount)

        try:
            # Cập nhật số dư mới lên bảng Wallet
            supabase.table("Wallet").update({
                "Balance": balance_after
            }).eq("UserID", self._owner.user_id).execute()

            # Ghi lịch sử giao dịch (rút tiền)
            Transaction.create(
                user_id=self._owner.user_id,
                amount=amount,
                tx_type="WITHDRAW",
                balance_before=balance_before,
                balance_after=balance_after,
                note="User withdrew money"
            )

            # Trả về thành công và số dư hiện tại
            self._balance = balance_after
            return True, balance_after

        except Exception as e:
            return False, str(e)

def increase_wallet_balance(user_id: str, amount: int):
            """
            Cộng tiền vào ví theo UserID
            """
            try:
                # Lấy balance hiện tại
                res = (
                    supabase.table("Wallet")
                    .select("Balance")
                    .eq("UserID", user_id)
                    .single()
                    .execute()
                )

                if not res.data:
                    return {"status": "error", "message": "Wallet not found"}

                current_balance = res.data["Balance"]

                new_balance = current_balance + amount

                # Update lại balance
                update = (
                    supabase.table("Wallet")
                    .update({"Balance": new_balance})
                    .eq("UserID", user_id)
                    .execute()
                )

                return {
                    "status": "success",
                    "old_balance": current_balance,
                    "new_balance": new_balance
                }

            except Exception as e:
                return {"status": "error", "message": str(e)}

# supabase_client.py
from supabase import create_client, Client
import numpy as np
# Thay bằng URL và KEY của bạn từ Supabase Project Settings
SUPABASE_URL = "https://tdkmoeyqaejiucanbgdj.supabase.co/"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRka21vZXlxYWVqaXVjYW5iZ2RqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2ODAzMDAwMCwiZXhwIjoyMDgzNjA2MDAwfQ.NQBxr2uL7wKN6xbAwzCuciW27k0bDAWri6rervA5rHw"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===============================================
#                     FUNCTION
# ===============================================

def upload_image_to_storage(image_source, filename, bucket="DrivingLicense"):
    """
    Đẩy ảnh lên Supabase Storage và trả về Public URL.
    """
    file_data = None
    try:
        if image_source is None: return None

        # Chuyển đổi sang bytes
        if isinstance(image_source, np.ndarray):
            import cv2
            _, buffer = cv2.imencode('.jpg', image_source)
            file_data = buffer.tobytes()
        elif isinstance(image_source, str):
            with open(image_source, 'rb') as f:
                file_data = f.read()

        # Trường hợp 3: Byte data trực tiếp
        else:
            file_data = image_source

        storage_path = f"{filename}.jpg"

        # Upload lên bucket được chỉ định
        supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=file_data,
            file_options={"content-type": "image/jpeg", "upsert": "true"}
        )

        return supabase.storage.from_(bucket).get_public_url(storage_path)
    except Exception as e:
        print(f"Lỗi upload: {e}")
        return None

def get_current_user():
    """
    Lấy thông tin user hiện tại.
    Tạm thời lấy USER đầu tiên (đúng chuẩn đồ án, chưa có session/login).
    """
    try:
        response = (
            supabase.table("User_Admin")
            .select("UserID, FullName, DateOfBirth, DrivingLicense, Email, Avatar")
            .eq("ClassifyUser", "USER")
            .limit(1)
            .execute()
        )

        if response.data:
            return response.data[0]
        return None

    except Exception as e:
        print(f"[ERROR] get_current_user: {e}")
        return None

def get_unique_filters():
    """
    Truy vấn danh sách Brand và Color duy nhất từ database.
    """
    try:
        res = (supabase.table("Vehicle_Bike_Motorbike_Car_Truck_Boat")
               .select("Brand", "Color")
               .execute())

        if not res.data:
            return {
                "status": "success",
                "brands": [],
                "colors": []
            }

        # 3. Sử dụng set để lấy các giá trị duy nhất (Unique)
        # Loại bỏ các giá trị None/Null nếu có trong database
        brands = sorted(list(set(item["Brand"] for item in res.data if item.get("Brand"))))
        colors = sorted(list(set(item["Color"] for item in res.data if item.get("Color"))))

        return {
            "status": "success",
            "brands": brands,
            "colors": colors
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    result = increase_wallet_balance("USJAB6YBQP", 5000000)
    print(result)



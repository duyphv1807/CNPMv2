from Backend.ExcuteDatabase import supabase
from Backend.Model.User import User

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

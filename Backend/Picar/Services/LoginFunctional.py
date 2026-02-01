# Backend/Picar/Services/AuthService.py
from ..ExcuteDatabase import supabase
import bcrypt

def login_logic(account_val, password_val):
    try:
        # 1. Truy vấn Database (Lưu ý: lấy dữ liệu từ .data)
        query = supabase.table("User_Admin") \
            .select("*") \
            .or_(f"Email.eq.{account_val},PhoneNumber.eq.{account_val}") \
            .execute()

        # 2. Kiểm tra nếu không tìm thấy tài khoản
        if not query.data:
            return {"status": "error", "message": "Tài khoản không tồn tại trên hệ thống"}

        user_data = query.data[0] # Lấy bản ghi đầu tiên
        # Mật khẩu trong Supabase là dạng HASH nên không được so sánh trực tiếp
        db_password_hash = user_data.get("Password")

        # 3. So sánh trực tiếp (Vì bạn chưa mã hóa mật khẩu trong DB)
        # Kiểm tra mật khẩu người dùng nhập bằng bcrypt.checkpw()
        if not bcrypt.checkpw(password_val.encode("utf-8"), db_password_hash.encode("utf-8")):
            return {"status": "error", "message": "Mật khẩu không chính xác"}

            # Xóa password khỏi user_data trước khi gửi về Client để tăng bảo mật
        user_data.pop("Password", None)
        return {"status": "success", "user_data": user_data}

    except Exception as e:
        print(f"Lỗi tại AuthService: {e}")
        return {"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}
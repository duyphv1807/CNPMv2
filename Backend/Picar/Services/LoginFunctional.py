# Backend/Picar/Services/AuthService.py
from ..ExcuteDatabase import supabase

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
        db_password = user_data.get("Password")

        # 3. So sánh trực tiếp (Vì bạn chưa mã hóa mật khẩu trong DB)
        if db_password == password_val:
            # Xóa password khỏi user_data trước khi gửi về Client để tăng bảo mật
            user_data.pop("Password", None)
            return {"status": "success", "user_data": user_data}
        else:
            return {"status": "error", "message": "Mật khẩu không chính xác"}

    except Exception as e:
        print(f"Lỗi tại AuthService: {e}")
        return {"status": "error", "message": f"Lỗi hệ thống: {str(e)}"}
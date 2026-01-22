from Backend.Picar.ExcuteDatabase import supabase

def verify_logic(email, user_code):
    try:
        # Đảo order lên trên để IDE nhận diện tốt hơn
        query = supabase.table("OTP").select("*").order("CreatedAt", desc=True)

        # Thực hiện các bộ lọc
        res = query.eq("Email", email) \
            .eq("IsUsed", False) \
            .limit(1) \
            .execute()

        if not res.data:
            return False, "Không tìm thấy mã OTP!"

        record = res.data[0]

        # Kiểm tra thời gian hết hạn (Sử dụng datetime chuẩn)
        from datetime import datetime
        expiry = datetime.fromisoformat(record['ExpiryTime'].replace('Z', '+00:00'))

        # So sánh thời gian hiện tại với thời gian hết hạn
        if datetime.now().astimezone() > expiry.astimezone():
            return False, "Mã OTP đã hết hạn!"

        if record['OTPCode'] == str(user_code):
            # Đánh dấu đã dùng
            supabase.table("OTP").update({"IsUsed": True}).eq("OTPID", record['OTPID']).execute()
            return True, "Xác thực thành công!"

        return False, "Mã OTP không chính xác!"
    except Exception as e:
        return False, f"Lỗi hệ thống: {str(e)}"
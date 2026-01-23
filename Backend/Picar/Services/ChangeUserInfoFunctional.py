from Backend.Picar.ExcuteDatabase import supabase

def change_password(user_id, old_password, new_password):
    try:
        # 1. Truy vấn user từ Supabase/Database
        # Giả sử bạn dùng Supabase
        response = supabase.table("User_Admin").select("*").eq("id", user_id).execute()

        if response.data:
            user = response.data[0]
            # 2. Kiểm tra mật khẩu cũ có khớp không
            if user.get("Password") == old_password:
                # 3. Cập nhật mật khẩu mới
                supabase.table("User_Admin").update({"Password": new_password}).eq("id", user_id).execute()
                return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def update_user_profile(user_id, data: dict):
    """
    Cập nhật thông tin người dùng:
    - Tên
    - Ngày sinh
    - GPLX
    - Email
    - Ảnh đại diện

    """
    try:
        payload = {}

        # Chỉ update field nào có truyền lên
        if "FullName" in data:
            payload["FullName"] = data["FullName"]

        if "DateOfBirth" in data:
            payload["DateOfBirth"] = data["DateOfBirth"]

        if "DrivingLicense" in data:
            payload["DrivingLicense"] = data["DrivingLicense"]

        if "Email" in data:
            payload["Email"] = data["Email"]

        if "Avatar" in data:
            payload["Avatar"] = data["Avatar"]

        if not payload:
            return False

        supabase.table("User_Admin") \
            .update(payload) \
            .eq("UserID", user_id) \
            .execute()

        return True

    except Exception as e:
        print(f"[ERROR] update_user_profile: {e}")
        return False
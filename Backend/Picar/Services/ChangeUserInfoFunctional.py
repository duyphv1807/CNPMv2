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
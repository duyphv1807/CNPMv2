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

from datetime import datetime  # Dùng để sửa lỗi "Expected type 'date'"
from Backend.Picar.Model.Vehicle import Vehicle
from Backend.Picar.Model.User import User
from Backend.Picar.Model.Address import Address


class VehicleBike(Vehicle):
    ALLOWED_TYPES = ["MOUNTAIN", "ROAD", "CITY", "ELECTRIC", "FOLDING"]
    ALLOWED_SIZES = ["XS", "S", "M", "L", "XL"]

    def __init__(self, brand: str, color: str, rental_price: float, rental_type: str = "Daily",
                 vehicle_document: str = None, status: str = "Available", owner: any = None,
                 image: str = None, bike_type: str = "CITY", frame_size: str = "M",
                 gear_system: str = "None", vehicle_id: str = None):

        # SỬA LỖI TẠI ĐÂY: Sử dụng tham số có tên để đảm bảo giá trị vào đúng biến
        super().__init__(
            brand=brand,
            color=color,
            rental_price=rental_price,
            vehicle_document=vehicle_document,
            status=status,
            owner=owner,
            image=image,
            vehicle_id=vehicle_id
        )

        # TỰ GÁN rental_type VÌ LỚP CHA KHÔNG NHẬN THAM SỐ NÀY
        self.rental_type = rental_type

        self._required_license = "NONE"
        self._classify_vehicle = "BIKE"
        self.bike_type = bike_type
        self.frame_size = frame_size
        self.gear_system = gear_system

    # --- Property & Setters (Giữ nguyên logic của bạn) ---
    @property
    def bike_type(self):
        return self._bike_type

    @bike_type.setter
    def bike_type(self, value):
        val = str(value).upper().strip()
        if val in self.ALLOWED_TYPES:
            self._bike_type = val
        else:
            raise ValueError(f"Loại xe {value} không hợp lệ!")

    @property
    def frame_size(self):
        return self._frame_size

    @frame_size.setter
    def frame_size(self, value):
        val = str(value).upper().strip()
        if val in self.ALLOWED_SIZES:
            self._frame_size = val
        else:
            raise ValueError(f"Kích cỡ {value} không hợp lệ!")

    @property
    def gear_system(self):
        return self._gear_system

    @gear_system.setter
    def gear_system(self, value):
        if value:
            self._gear_system = value
        else:
            raise ValueError("Hệ thống truyền động không được để trống!")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "ClassifyVehicle": "BIKE",
            "BikeType": self._bike_type,
            "FrameSize": self._frame_size,
            "GearSystem": self._gear_system,
            "VehicleID": self._vehicle_id  # Đảm bảo ID có trong dict
        })
        return data


# --- PHẦN TEST (Sửa lỗi Type Hinting từ ảnh của bạn) ---
if __name__ == "__main__":
    # 3. FIX LỖI "Expected type 'date', got 'str'":
# Chuyển chuỗi thành đối tượng date thực thụ
    dob_obj = datetime.strptime("18/07/2000", "%d/%m/%Y").date()

    user1 = User("user_picar", "083222222222", dob_obj, "0377111111",
                 "awr@gmai.com", "091122222222", "Abc123",
                 "https://example.com/avatar.jpg", 0, 5, "USE7BK3OU6")

    # 4. FIX LỖI "Unused import Address":
    # Khởi tạo và sử dụng Address
    ad3 = Address(
        detail="89 Nguyễn Văn Thoại",
        commune="Phường Mỹ An, Quận Ngũ Hành Sơn",
        city="Đà Nẵng",
        latitude=16.0544,
        longitude=108.2022
    )

    # 5. FIX LỖI "Expected type 'User', got 'str'":
    # Truyền biến user1 (đối tượng), không phải chuỗi "user1"
    bike1 = VehicleBike(
        brand="Asama Road Pro",
        color="White",
        rental_price=100000,
        rental_type="Daily",
        vehicle_document="BIKE_DOC_001",  # Giá trị này sẽ không bị nhầm vào status nữa
        status="Available",  # Đảm bảo giá trị này hợp lệ với logic trong Vehicle.py
        owner=user1,
        image=r"D:\anh xe\OIP (3).webp",
        bike_type="CITY",
        frame_size="L",
        gear_system="Shimano",
    )

    # Lưu vào DB để kiểm tra logic
    try:
        bike1.save_to_db(ad3)
        print("Đã khởi tạo và lưu xe đạp thành công!")
    except Exception as e:
        print(f"Lỗi khi thực thi: {e}")
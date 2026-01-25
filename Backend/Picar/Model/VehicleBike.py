from Backend.Picar.Model.Vehicle import Vehicle

class VehicleBike(Vehicle):
    # Danh sách các tùy chọn chuẩn cho xe đạp
    ALLOWED_TYPES = ["MOUNTAIN", "ROAD", "CITY", "ELECTRIC", "FOLDING"]
    ALLOWED_SIZES = ["XS", "S", "M", "L", "XL"]

    class Bike(Vehicle):
        def __init__(self, brand: str, color: str, rental_price: float, rental_type: str = "Daily",
                     vehicle_document: str = None, status: str = "Available", owner: any = None,
                     image: str = None, bike_type: str = "City", frame_size: str = "M",
                     gear_system: str = "None", vehicle_id: str = None):
            # Gọi hàm khởi tạo cha
            super().__init__(
                brand=brand,
                color=color,
                rental_price=rental_price,
                rental_type=rental_type,
                vehicle_document=vehicle_document,
                status=status,
                owner=owner,
                image=image,
                vehicle_id=vehicle_id
            )

            # Xe đạp mặc định không bằng lái và phân loại là Bike
            self._required_license = "NONE"
            self._classify_vehicle = "Bike"  # Rất quan trọng cho hàm search_logic

            # Gán thuộc tính đặc thù
            self.bike_type = bike_type
            self.frame_size = frame_size
            self.gear_system = gear_system

    # --- SETTER CHO BIKE TYPE ---
    @property
    def bike_type(self):
        return self._bike_type

    @bike_type.setter
    def bike_type(self, value: str):
        val_upper = value.upper().strip()
        if val_upper in self.ALLOWED_TYPES:
            self._bike_type = val_upper
        else:
            raise ValueError(f"Loại xe {value} không hợp lệ! Chọn: {self.ALLOWED_TYPES}")

    # --- SETTER CHO FRAME SIZE ---
    @property
    def frame_size(self):
        return self._frame_size

    @frame_size.setter
    def frame_size(self, value: str):
        val_upper = value.upper().strip()
        if val_upper in self.ALLOWED_SIZES:
            self._frame_size = val_upper
        else:
            raise ValueError(f"Kích cỡ {value} không hợp lệ! Chọn: {self.ALLOWED_SIZES}")

    # --- GETTER/SETTER CHO GEAR SYSTEM ---
    @property
    def gear_system(self):
        return self._gear_system

    @gear_system.setter
    def gear_system(self, value: str):
        if value and value.strip():
            self._gear_system = value
        else:
            raise ValueError("Hệ thống truyền động không được để trống!")

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Ghi đè to_dict để thêm các trường đặc thù của xe đạp"""
        data = super().to_dict() # Lấy thông tin chung từ Vehicle
        data.update({
            "ClassifyVehicle": "BIKE", # Dùng để phân biệt trong database
            "BikeType": self._bike_type,
            "FrameSize": self._frame_size,
            "GearSystem": self._gear_system
        })
        return data

    # --- GHI ĐÈ PHƯƠNG THỨC INFO ---
    def get_info(self):
        info = super().get_info()
        info.update({
            "Bike Type": self._bike_type,
            "Frame Size": self._frame_size,
            "Gear System": self._gear_system
        })
        return info


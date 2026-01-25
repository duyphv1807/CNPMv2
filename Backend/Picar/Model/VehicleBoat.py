from Backend.Picar.Model.Vehicle import Vehicle

class VehicleBoat(Vehicle):
    # Danh sách các tùy chọn chuẩn cho tàu thuyền
    ALLOWED_ENGINES = ["OUTBOARD", "INBOARD", "JET", "SAIL"]

    def __init__(self, brand: str, color: str, rental_price: float, rental_type: str = "Daily",
                 vehicle_document: str = None, status: str = "Available", owner: any = None,
                 image: str = None, length: float = 0.0, engine_type: str = "Outboard",
                 passenger_capacity: int = 0, license_plate: str = "", vehicle_id: str = None):

        # 1. Gọi hàm khởi tạo của class cha (Phải có owner)
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

        # 2. Thuộc tính riêng (Sử dụng protected _ để đồng bộ)
        self._length = length
        self._passenger_capacity = passenger_capacity
        self._license_plate = license_plate

        # Gán qua setter để kiểm tra logic engine_type
        self.engine_type = engine_type

        # 3. Tự động xác định hạng bằng thuyền trưởng
        self._update_required_license()

    def _update_required_license(self):
        """Logic phân hạng bằng lái đường thủy dựa trên sức chở"""
        if self._passenger_capacity <= 12:
            self._required_license = "T3"
        elif 12 < self._passenger_capacity <= 50:
            self._required_license = "T2"
        else:
            self._required_license = "T1"

    # --- GETTER/SETTER CHO ENGINE TYPE ---
    @property
    def engine_type(self):
        return self._engine_type

    @engine_type.setter
    def engine_type(self, value: str):
        val_upper = value.upper().strip()
        if val_upper in self.ALLOWED_ENGINES:
            self._engine_type = val_upper
        else:
            raise ValueError(f"Loại động cơ không hợp lệ! Chọn: {self.ALLOWED_ENGINES}")

    # --- CÁC GETTER/SETTER KHÁC ---
    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, value: float):
        if value > 0:
            self._length = value
        else:
            raise ValueError("Chiều dài tàu phải lớn hơn 0")

    @property
    def passenger_capacity(self):
        return self._passenger_capacity

    @passenger_capacity.setter
    def passenger_capacity(self, value: int):
        if value > 0:
            self._passenger_capacity = value
            self._update_required_license()  # Cập nhật lại bằng lái nếu sức chở thay đổi
        else:
            raise ValueError("Sức chở phải lớn hơn 0")

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Ghi đè to_dict để thêm các trường đặc thù của tàu thuyền"""
        data = super().to_dict()
        data.update({
            "ClassifyVehicle": "BOAT",
            "Length": self._length,
            "EngineType": self._engine_type,
            "PassengerCapacity": self._passenger_capacity,
            "LicensePlate": self._license_plate
        })
        return data

    # --- GHI ĐÈ PHƯƠNG THỨC INFO ---
    def get_info(self):
        info = super().get_info()
        info.update({
            "Length": f"{self._length} m",
            "Capacity": f"{self._passenger_capacity} người",
            "Engine": self._engine_type,
            "Registration": self._license_plate
        })
        return info

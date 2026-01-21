from Backend.Model.Vehicle import Vehicle
from Backend.Model.User import User


class VehicleMotorbike(Vehicle):
    # Danh sách các tùy chọn chuẩn cho xe máy
    ALLOWED_TRANSMISSIONS = ["MANUAL", "AUTOMATIC", "SEMI-AUTOMATIC"]

    def __init__(self, brand: str, color: str, rental_price: float,
                 vehicle_document: str, status: str, owner: User, image: str, engine_capacity: int,
                 transmission_type: str, license_plate: str, vehicle_id: str = None):

        # 1. Gọi hàm khởi tạo của class cha (Bắt buộc có owner)
        super().__init__(brand, color, rental_price, vehicle_document, status, owner, image, vehicle_id)

        # 2. Các thuộc tính (Sử dụng protected _)
        self._engine_capacity = engine_capacity
        self._license_plate = license_plate.upper().strip()

        # Sử dụng setter để gán và kiểm tra logic
        self.transmission_type = transmission_type

        # 3. Tự động xác định bằng lái yêu cầu (Luật VN)
        self._update_required_license()

    # --- LOGIC TỰ ĐỘNG XÁC ĐỊNH BẰNG LÁI ---
    def _update_required_license(self):
        if self._engine_capacity < 50:
            self._required_license = "NONE"
        elif 50 <= self._engine_capacity < 175:
            self._required_license = "A1"
        else:
            self._required_license = "A2"

    # --- GETTER/SETTER ---
    @property
    def engine_capacity(self):
        return self._engine_capacity

    @engine_capacity.setter
    def engine_capacity(self, value: int):
        if value > 0:
            self._engine_capacity = value
            self._update_required_license()
        else:
            raise ValueError("Phân khối xe phải lớn hơn 0")

    @property
    def transmission_type(self):
        return self._transmission_type

    @transmission_type.setter
    def transmission_type(self, value: str):
        val_upper = value.upper().strip()
        if val_upper in self.ALLOWED_TRANSMISSIONS:
            self._transmission_type = val_upper
        else:
            raise ValueError(f"Loại truyền động không hợp lệ! Chọn: {self.ALLOWED_TRANSMISSIONS}")

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Map dữ liệu để lưu lên Supabase"""
        data = super().to_dict()
        data.update({
            "ClassifyVehicle": "MOTORBIKE",
            "EngineCapacity": self._engine_capacity,
            "TransmissionType": self._transmission_type,
            "LicensePlate": self._license_plate
        })
        return data

    # --- GHI ĐÈ PHƯƠNG THỨC INFO ---
    def get_info(self):
        info = super().get_info()
        info.update({
            "Engine Capacity": f"{self._engine_capacity} cc",
            "Transmission": self._transmission_type,
            "License Plate": self._license_plate
        })
        return info

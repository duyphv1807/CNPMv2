from Backend.Picar.Model.Vehicle import Vehicle
from Backend.Picar.Model.User import User

class VehicleCar(Vehicle):
    # Danh sách các tùy chọn chuẩn cho ô tô
    ALLOWED_FUELS = ["GASOLINE", "DIESEL", "ELECTRIC", "HYBRID"]
    ALLOWED_TRANSMISSIONS = ["MANUAL", "AUTOMATIC"]

    def __init__(self, brand: str, color: str, rental_price: float,
                 model: str, seating_capacity: int, fuel_type: str,
                 transmission: str, engine_power: str, license_plate: str,
                 vehicle_document: str = None, status: str = "Available",
                 owner: User = None, image: str = None,
                 rental_type: str = "Daily", vehicle_id: str = None):

        # 1. Gọi hàm khởi tạo của class cha (Bắt buộc có owner)
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
        self._model = model
        self._seating_capacity = seating_capacity
        self._engine_power = engine_power
        self._license_plate = license_plate.upper().strip()

        # Gán giá trị thông qua setter để kiểm tra logic và tự động định danh bằng lái
        self.fuel_type = fuel_type
        self.transmission = transmission

    # --- LOGIC TỰ ĐỘNG XÁC ĐỊNH BẰNG LÁI ---
    def _update_required_license(self):
        """Luật VN: B1 cho số tự động, B2 cho số sàn"""
        if self._transmission == "AUTOMATIC":
            self._required_license = "B1"
        else:
            self._required_license = "B2"

    # --- SETTER/GETTER ---
    @property
    def fuel_type(self):
        return self._fuel_type

    @fuel_type.setter
    def fuel_type(self, value: str):
        val_upper = value.upper().strip()
        if val_upper in self.ALLOWED_FUELS:
            self._fuel_type = val_upper
        else:
            raise ValueError(f"Loại nhiên liệu không hợp lệ! Chọn: {self.ALLOWED_FUELS}")

    @property
    def transmission(self):
        return self._transmission

    @transmission.setter
    def transmission(self, value: str):
        val_upper = value.upper().strip()
        if val_upper in self.ALLOWED_TRANSMISSIONS:
            self._transmission = val_upper
            # Cập nhật lại hạng bằng lái tương ứng
            self._update_required_license()
        else:
            raise ValueError(f"Loại hộp số không hợp lệ! Chọn: {self.ALLOWED_TRANSMISSIONS}")

    @property
    def seating_capacity(self):
        return self._seating_capacity

    @seating_capacity.setter
    def seating_capacity(self, value: int):
        if 2 <= value <= 50:
            self._seating_capacity = value
        else:
            raise ValueError("Số chỗ ngồi không hợp lệ (2-50 chỗ)")

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Map dữ liệu để lưu lên Supabase"""
        data = super().to_dict()
        data.update({
            "ClassifyVehicle": "CAR",
            "Model": self._model,
            "SeatingCapacity": self._seating_capacity,
            "FuelType": self._fuel_type,
            "Transmission": self._transmission,
            "EnginePower": self._engine_power,
            "LicensePlate": self._license_plate
        })
        return data

    # --- GHI ĐÈ PHƯƠNG THỨC INFO ---
    def get_info(self):
        info = super().get_info()
        info.update({
            "Model": self._model,
            "Seats": f"{self._seating_capacity} chỗ",
            "Fuel": self._fuel_type,
            "TransmissionType": self._transmission,
            "Power": self._engine_power,
            "License Plate": self._license_plate
        })
        return info

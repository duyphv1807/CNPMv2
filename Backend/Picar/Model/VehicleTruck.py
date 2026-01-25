from Backend.Picar.Model.Vehicle import Vehicle
from Backend.Picar.Model.User import User

class VehicleTruck(Vehicle):
    # Danh sách các tùy chọn chuẩn cho xe tải
    ALLOWED_ENGINES = ["DIESEL", "GASOLINE", "ELECTRIC"]

    def __init__(self, brand: str, color: str, rental_price: float,
                 load_capacity: float, engine_type: str, dimensions: str, license_plate: str,
                 vehicle_document: str = None, status: str = "Available",
                 owner: User = None, image: str = None,
                 rental_type: str = "Daily", vehicle_id: str = None):

        # 1. Gọi hàm khởi tạo của class cha (Phải truyền owner lên)
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

        # 2. Các thuộc tính (Sử dụng protected _ để nhất quán)
        self._load_capacity = load_capacity
        self._dimensions = dimensions
        self._license_plate = license_plate.upper().strip()

        # Gán qua setter để kiểm tra logic
        self.engine_type = engine_type

        # 3. Tự động xác định bằng lái yêu cầu
        self._update_required_license()

    # --- LOGIC TỰ ĐỘNG XÁC ĐỊNH BẰNG LÁI ---
    def _update_required_license(self):
        """Luật Việt Nam: < 3.5 tấn dùng B2, >= 3.5 tấn dùng C"""
        if self._load_capacity < 3.5:
            self._required_license = "B2"
        else:
            self._required_license = "C"

    # --- SETTER/GETTER ---
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

    @property
    def load_capacity(self):
        return self._load_capacity

    @load_capacity.setter
    def load_capacity(self, value: float):
        if value > 0:
            self._load_capacity = value
            self._update_required_license()  # Cập nhật lại bằng lái khi đổi tải trọng
        else:
            raise ValueError("Tải trọng phải lớn hơn 0!")

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Map dữ liệu để lưu lên Supabase"""
        data = super().to_dict()
        data.update({
            "ClassifyVehicle": "TRUCK",
            "LoadCapacity": self._load_capacity,
            "EngineType": self._engine_type,
            "Dimensions": self._dimensions,
            "LicensePlate": self._license_plate
        })
        return data

    # --- GHI ĐÈ PHƯƠNG THỨC INFO ---
    def get_info(self):
        info = super().get_info()
        info.update({
            "Load Capacity": f"{self._load_capacity} Tấn",
            "Dimensions": self._dimensions,
            "Engine": self._engine_type,
            "License Plate": self._license_plate
        })
        return
if __name__ == "__main__":
    user1 = User("user","083222222222","18/07/2000","0377111111",
                 "awr@gmai.com","091122222222","Abc123","https://supabase.com/dashboard/project/tdkmoeyqaejiucanbgdj/storage/files/buckets/Avatar/avatar.jpg",
                 0,5,"USE7BK3OU6")

    boat1 = VehicleTruck(
        brand="Suzuki",
        color="White",
        rental_price=500000,
        vehicle_document="TRUCK_DOC_001",
        status="AVAILABLE",
        owner=user1,
        image=r"C:\Users\ASUS\OneDrive\Máy tính\bài tập\test\carry.jfif",
        load_capacity=0.5,  # 500kg -> Bằng B2
        engine_type="GASOLINE",
        dimensions="2.5m x 1.3m x 1.3m",
        license_plate="51C-123.45"
    )
    boat1.save_to_db()
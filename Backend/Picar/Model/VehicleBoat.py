from datetime import datetime
from Backend.Picar.Model.Vehicle import Vehicle
from Backend.Picar.Model.User import User
from Backend.Picar.Model.Address import Address


class VehicleBoat(Vehicle):
        # Danh sách các tùy chọn chuẩn cho tàu thuyền
        ALLOWED_ENGINES = ["OUTBOARD", "INBOARD", "JET", "SAIL"]

<<<<<<< HEAD
        # Trong file VehicleBoat.py, sửa lại hàm __init__ như sau:

        def __init__(self, brand: str, color: str, rental_price: float, rental_type: str = "Daily",
                     vehicle_document: str = None, status: str = "Available", owner: User = None,
                     image: str = None, length: float = 0.0, engine_type: str = "OUTBOARD",
                     passenger_capacity: int = 0, license_plate: str = "", vehicle_id: str = None):

            # SỬA LẠI: Đổi rental_type thành type (hoặc bỏ đi nếu lớp cha không có)
            super().__init__(
                brand=brand,
                color=color,
                rental_price=rental_price,
                # rental_type=rental_type, # <--- Bị lỗi ở đây
                # Thử đổi thành:
                # type=rental_type,
                vehicle_document=vehicle_document,
                status=status,
                owner=owner,
                image=image,
                vehicle_id=vehicle_id
            )

            # Nếu lớp cha không nhận rental_type, hãy gán nó tại đây để sử dụng
            self.rental_type = rental_type
=======
    # Trong file VehicleBoat.py, sửa lại hàm __init__ như sau:

    def __init__(self, brand: str, color: str, rental_price: float, rental_type: str = "Daily",
                 vehicle_document: str = None, status: str = "Available", owner: User = None,
                 image: str = None, length: float = 0.0, engine_type: str = "OUTBOARD",
                 passenger_capacity: int = 0, license_plate: str = "", vehicle_id: str = None):

        # SỬA LẠI: Đổi rental_type thành type (hoặc bỏ đi nếu lớp cha không có)
        super().__init__(
            brand=brand,
            color=color,
            rental_price=rental_price,
            # rental_type=rental_type, # <--- Bị lỗi ở đây
            # Thử đổi thành:
            # type=rental_type,
            vehicle_document=vehicle_document,
            status=status,
            owner=owner,
            image=image,
            vehicle_id=vehicle_id
        )

        # Nếu lớp cha không nhận rental_type, hãy gán nó tại đây để sử dụng
        self.rental_type = rental_type

        # ... các thuộc tính khác giữ nguyên ...
        # 2. Thuộc tính riêng
        self._length = length
        self._passenger_capacity = passenger_capacity
        self._license_plate = license_plate
        self._classify_vehicle = "BOAT"

        # Gán qua setter để kiểm tra logic
        self.engine_type = engine_type
>>>>>>> 2443bfd022fff62c4f665e4d1b7696db2ca0d02c

            # ... các thuộc tính khác giữ nguyên ...
            # 2. Thuộc tính riêng
            self._length = length
            self._passenger_capacity = passenger_capacity
            self._license_plate = license_plate
            self._classify_vehicle = "BOAT"

            # Gán qua setter để kiểm tra logic
            self.engine_type = engine_type

<<<<<<< HEAD
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

        @property
        def engine_type(self):
            return self._engine_type
=======
    @property
    def engine_type(self):
        return self._engine_type

    @engine_type.setter
    def engine_type(self, value: str):
        val_upper = str(value).upper().strip()
        if val_upper in self.ALLOWED_ENGINES:
            self._engine_type = val_upper
        else:
            raise ValueError(f"Loại động cơ {value} không hợp lệ! Chọn: {self.ALLOWED_ENGINES}")

    @property
    def length(self):
        return self._length
>>>>>>> 2443bfd022fff62c4f665e4d1b7696db2ca0d02c

        @engine_type.setter
        def engine_type(self, value: str):
            val_upper = str(value).upper().strip()
            if val_upper in self.ALLOWED_ENGINES:
                self._engine_type = val_upper
            else:
                raise ValueError(f"Loại động cơ {value} không hợp lệ! Chọn: {self.ALLOWED_ENGINES}")

        @property
        def length(self):
            return self._length

<<<<<<< HEAD
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
                self._update_required_license()
            else:
                raise ValueError("Sức chở phải lớn hơn 0")

        def to_dict(self):
            data = super().to_dict()
            data.update({
                "ClassifyVehicle": "BOAT",
                "Length": self._length,
                "EngineType": self._engine_type,
                "PassengerCapacity": self._passenger_capacity,
                "LicensePlate": self._license_plate,
            })
            return data

        def get_info(self):
            info = super().get_info()
            info.update({
                "Length": f"{self._length} m",
                "Capacity": f"{self._passenger_capacity} người",
                "Engine": self._engine_type,
                "Registration": self._license_plate,
                "License Required": self._required_license
            })
            return info

        # --- PHẦN TEST VỚI MẪU NGẪU NHIÊN ---


if __name__ == "__main__":
        # Khởi tạo User và Address chuẩn
        dob = datetime.strptime("18/07/2000", "%d/%m/%Y").date()
        user1 = User("picar_boat_owner", "083222222222", dob, "0377111111",
                     "boat@picar.vn", "091122222222", "Abc123",
                     "avatar.jpg", 0, 5, "US1ETD2WWE")

        ad1 = Address(detail="250 Điện Biên Phủ", commune="Phường 17, Quận Bình Thạnh", city="TP Hồ Chí Minh",
                      latitude=16.0544, longitude=108.2022)

        ad1.update_gps_from_address()
        boat1 = VehicleBoat(
            brand="Bayliner Element",
            color="Gray",
            rental_price=800000,
            rental_type="Hourly",
            vehicle_document="BOAT_DOC_001",
            status="AVAILABLE",
            owner=user1,
            image=r"D:\anh xe\IMG_3416.jpg",
            length=5.5,
            engine_type="OUTBOARD",
            passenger_capacity=10,
        )

        boat1.save_to_db(ad1)

=======
    @passenger_capacity.setter
    def passenger_capacity(self, value: int):
        if value > 0:
            self._passenger_capacity = value
            self._update_required_license()
        else:
            raise ValueError("Sức chở phải lớn hơn 0")

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "ClassifyVehicle": "BOAT",
            "Length": self._length,
            "EngineType": self._engine_type,
            "PassengerCapacity": self._passenger_capacity,
            "LicensePlate": self._license_plate,
            "RequiredLicense": self._required_license
        })
        return data

    def get_info(self):
        info = super().get_info()
        info.update({
            "Length": f"{self._length} m",
            "Capacity": f"{self._passenger_capacity} người",
            "Engine": self._engine_type,
            "Registration": self._license_plate,
            "License Required": self._required_license
        })
        return info


# --- PHẦN TEST VỚI MẪU NGẪU NHIÊN ---
if __name__ == "__main__":
    # Khởi tạo User và Address chuẩn
    dob = datetime.strptime("18/07/2000", "%d/%m/%Y").date()
    user1 = User("picar_boat_owner", "083222222222", dob, "0377111111",
                 "boat@picar.vn", "091122222222", "Abc123", "avatar.jpg", 0, 5, "USCSCIY1CV")

    ad1 = Address(detail="89 Nguyễn Văn Thoại", commune="Phường Mỹ An", city="Đà Nẵng",
                  latitude=16.0544, longitude=108.2022)

    # Danh sách mẫu thuyền thực tế
    boat_samples = [
        {"brand": "Yamaha FX Cruiser", "price": 500000, "len": 3.5, "eng": "JET", "cap": 3, "plate": "DN-001"},
        {"brand": "Sea Ray SPX 210", "price": 1200000, "len": 6.5, "eng": "INBOARD", "cap": 12, "plate": "DN-002"},
        {"brand": "Sunseeker Predator", "price": 5000000, "len": 22.0, "eng": "INBOARD", "cap": 25, "plate": "DN-003"},
        {"brand": "Kawasaki Ultra 310X", "price": 450000, "len": 3.3, "eng": "JET", "cap": 3, "plate": "DN-004"},
        {"brand": "Whaly 500 Professional", "price": 800000, "len": 4.9, "eng": "OUTBOARD", "cap": 10,
         "plate": "DN-005"}
    ]

    list_boats = []
    for i, s in enumerate(boat_samples):
        try:
            boat = VehicleBoat(
                brand=s["brand"],
                color="White/Blue",
                rental_price=s["price"],
                rental_type="Hourly" if s["eng"] == "JET" else "Daily",
                vehicle_document=f"BOAT_DOC_{i}",
                status="AVAILABLE",
                owner=user1,
                image=f"boat_{i}.jpg",
                length=s["len"],
                engine_type=s["eng"],
                passenger_capacity=s["cap"],
                license_plate=s["plate"],
                vehicle_id=f"BT_{2026}_{i}"
            )
            list_boats.append(boat)
            # Thử lưu vào DB
            # boat.save_to_db(ad1)
        except Exception as e:
            print(f"Lỗi tạo mẫu {s['brand']}: {e}")

    print(f"--- Đã tạo {len(list_boats)} mẫu thuyền/mô tô nước thành công ---")
    if list_boats:
        print(f"Ví dụ mẫu 1: {list_boats[0].brand} - Bằng lái yêu cầu: {list_boats[0]._required_license}")
>>>>>>> 2443bfd022fff62c4f665e4d1b7696db2ca0d02c

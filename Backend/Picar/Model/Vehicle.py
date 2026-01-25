from Backend.Picar.Model.User import User
from Backend.Picar.ExcuteDatabase import upload_image_to_storage
from Backend.Picar.Utils.GenerateID import generate_id

class Vehicle:
    # Danh sách các hạng bằng lái chuẩn tại Việt Nam
    LICENSE_TYPES = {
        "NONE": "Không yêu cầu bằng lái",
        "A1": "Xe máy dưới 175cc",
        "A2": "Xe máy từ 175cc trở lên",
        "B1": "Ô tô số tự động dưới 9 chỗ",
        "B2": "Ô tô số sàn & tự động dưới 9 chỗ",
        "C": "Xe tải trên 3.5 tấn",
        "T3": "Bằng thuyền trưởng hạng 3 (Tàu nhỏ)",
        "T2": "Bằng thuyền trưởng hạng 2 (Tàu vừa)",
        "T1": "Bằng thuyền trưởng hạng 1 (Tàu lớn)"
    }

    def __init__(self, brand: str, color: str, rental_price: float,
                 vehicle_document: str, status: str, owner: User, image: str, vehicle_id: str = None):

        self._vehicle_id = vehicle_id if vehicle_id else generate_id("VE")
        self._owner = owner  # Lưu toàn bộ đối tượng User là chủ xe

        # Gán thông qua setter để kiểm tra logic
        self.brand = brand
        self.rental_price = rental_price
        self.status = status
        self.color = color
        self.vehicle_document = vehicle_document
        self.image = image

        # Thuộc tính sẽ được class con cụ thể hóa (Car gán B2, Motor gán A1...)
        self._required_license = "NONE"

    # --- GETTER/SETTER ---
    @property
    def vehicle_id(self):
        return self._vehicle_id

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        # Có thể bổ sung kiểm tra định dạng file tại đây nếu cần
        self._image = value
    @property
    def owner(self):
        return self._owner

    @property
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, value: str):
        if not value or not value.strip():
            raise ValueError("Thương hiệu không được để trống!")
        self._brand = value

    @property
    def rental_price(self):
        return self._rental_price

    @rental_price.setter
    def rental_price(self, value: float):
        if value < 0:
            raise ValueError("Giá thuê không được nhỏ hơn 0!")
        self._rental_price = value

    @property
    def status(self):
        return self._status.upper()

    @status.setter
    def status(self, value: str):
        allowed_status = ["AVAILABLE", "RENTED", "MAINTENANCE", "LOCKED"]
        if value.upper() in allowed_status:
            self._status = value.upper()
        else:
            raise ValueError(f"Trạng thái {value} không hợp lệ!")

    @property
    def vehicle_document(self):
        return self._vehicle_document

    @vehicle_document.setter
    def vehicle_document(self, value: str):
        self._vehicle_document = value

    # --- DATABASE METHODS ---
    def to_dict(self):
        """Map từ Python sang PascalCase của Supabase"""
        return {
            "VehicleID": self._vehicle_id,
            "OwnerID": self._owner.user_id,  # Lấy ID từ đối tượng User
            "Brand": self._brand,
            "Color": self.color,
            "RentalPrice": self._rental_price,
            "Status": self.status,
            "VehicleDocument": self._vehicle_document,
            "RequiredLicenseType": self._required_license,
            "Image": self.image
        }

    def save_to_db(self):
        from Backend.Picar.ExcuteDatabase import supabase
        if self._image:
            # Đặt tên file theo VehicleID để tránh trùng lặp
            public_url = upload_image_to_storage(
                image_source=self._image,
                filename=self._vehicle_id,
                bucket="VehicleImages"  # Bạn nên tạo bucket tên 'Vehicles'
            )
            if public_url:
                self._image_url = public_url
            else:
                print("⚠️ Cảnh báo: Không thể upload ảnh, xe sẽ không có hình hiển thị.")
        max_retries = 3
        attempts = 0
        while attempts < max_retries:
            try:
                return supabase.table("Vehicle_Bike_Motorbike_Car_Truck_Boat").insert(self.to_dict()).execute()
            except Exception as e:
                if "duplicate key value" in str(e).lower() or "23505" in str(e):
                    print(f"⚠️ Trùng mã {self._vehicle_id}, đang tạo mã mới...")
                    # Tạo mã mới và thử lại
                    self._vehicle_id = generate_id("VE")
                    attempts += 1
                else:
                    # Nếu là lỗi khác (mất mạng, sai cột...) thì báo lỗi ngay
                    print(f"❌ Lỗi Database: {e}")
                    return None

    def get_info(self):
        license_desc = self.LICENSE_TYPES.get(self._required_license, "Chưa xác định")
        return {
            "ID": self._vehicle_id,
            "Owner": self._owner.full_name,  # Lấy tên chủ xe dễ dàng
            "Brand": self._brand,
            "Color": self.color,
            "Price": f"{self._rental_price:,.0f} VND",
            "RequiredLicenseType": self._required_license,
            "Description": license_desc,
            "Status": self.status
        }


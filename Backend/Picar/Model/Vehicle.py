from Backend.Picar.Model.User import User
from Backend.Picar.ExcuteDatabase import supabase
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

    def __init__(self, brand: str, color: str, rental_price: float, rental_type: str = "Daily",
                 vehicle_document: str = None, status: str = "Available", owner: any = None,
                 image: str = None, vehicle_id: str = None):

        self._vehicle_id = vehicle_id if vehicle_id else generate_id("VE")
        self._owner = owner  # Lưu đối tượng User (OwnerID)

        # Gán thông qua setter để kiểm tra logic
        self.brand = brand
        self.rental_price = rental_price
        self.rental_type = rental_type  # Bổ sung gán RentalType (Daily/Hourly)
        self.status = status
        self.color = color
        self.vehicle_document = vehicle_document
        self.image = image

        # Thuộc tính sẽ được class con cụ thể hóa
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

    def save_to_db(self, address_obj=None):
        """
        Lưu thông tin xe và địa chỉ vào Database.
        address_obj: Đối tượng thuộc class VehicleAddress
        """
        from Backend.Picar.ExcuteDatabase import upload_image_to_storage

        # 1. Xử lý Upload ảnh (giữ nguyên logic của bạn)
        if self.image:
            public_url = upload_image_to_storage(
                image_source=self.image,
                filename=self._vehicle_id,
                bucket="VehicleImages"
            )
            if public_url:
                self.image = public_url  # Cập nhật lại đường dẫn URL sau khi upload thành công

        # 2. Lưu thông tin Vehicle vào bảng chính
        max_retries = 3
        attempts = 0
        vehicle_saved = False
        result = None

        while attempts < max_retries:
            try:
                # Thực hiện insert vào bảng Vehicle
                result = supabase.table("Vehicle_Bike_Motorbike_Car_Truck_Boat").insert(self.to_dict()).execute()

                if result.data:
                    vehicle_saved = True
                    print(f"✅ Đã lưu thông tin xe: {self._vehicle_id}")
                    break
            except Exception as e:
                if "duplicate key value" in str(e).lower() or "23505" in str(e):
                    self._vehicle_id = generate_id("VE")
                    attempts += 1
                else:
                    print(f"❌ Lỗi Database khi lưu Vehicle: {e}")
                    return None

        # 3. GỌI LƯU ĐỊA CHỈ (Nếu xe đã lưu thành công và có đối tượng địa chỉ truyền vào)
        if vehicle_saved and address_obj:
            # Gọi hàm save_to_database của class Address và truyền VehicleID hiện tại
            address_result = address_obj.save_to_database(vehicle_id=self._vehicle_id)

            if address_result["status"] == "success":
                print(f"✅ Đã lưu địa chỉ cho xe: {self._vehicle_id}")
            else:
                print(f"⚠️ Cảnh báo: Xe đã lưu nhưng lỗi lưu địa chỉ: {address_result['message']}")

        return result

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


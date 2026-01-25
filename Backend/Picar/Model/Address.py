import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from Backend.Picar.ExcuteDatabase import supabase
class Address:
    def __init__(self, detail, commune, city, latitude = None, longitude = None):
        # 1. Số nhà, đường, xóm...
        self.detail = detail

        # 2. Cấp cơ sở (Phường/Xã/Đặc khu)
        self.commune = commune

        # 3. Cấp tỉnh (34 tỉnh thành mới)
        self.city = city

        # Tọa độ GPS để tính xe gần nhất
        self.lat = latitude
        self.lng = longitude

    @property
    def detail(self): return self.__detail

    @property
    def commune(self): return self.__commune

    @property
    def city(self): return self.__city

    @property
    def lat(self): return self.__lat

    @property
    def lng(self): return self.__lng

    @detail.setter
    def detail(self, value): self.__detail = value

    @commune.setter
    def commune(self, value): self.__commune = value

    @city.setter
    def city(self, value): self.__city = value

    @lat.setter
    def lat(self, value):
        if value is None:
            self.__lat = None
        else:
            self.__lat = float(value)

    @lng.setter
    def lng(self, value):
        if value is None:
            self.__lng = None
        else:
            self.__lng = float(value)

    def get_full_address(self):
        """Định dạng địa chỉ chuẩn 2025: [Chi tiết], [Cấp Xã], [Cấp Tỉnh]"""
        return f"{self.detail}, {self.commune}, {self.city}"

    def to_dict(self):
        """Chuyển đổi thành dictionary để gửi qua API JSON"""
        return {
            "detail": self.__detail,
            "commune": self.__commune,
            "city": self.__city,
            "full_address": self.get_full_address(),
            "lat": self.__lat,
            "lng": self.__lng
        }

    def update_gps_from_address(self):
        """
        Tự động lấy tọa độ Lat/Lng dựa trên địa chỉ (Detail, Ward, City)
        """
        # Tạo chuỗi địa chỉ đầy đủ để tìm kiếm chính xác nhất
        full_address = f"{self.detail}, {self.commune}, {self.city}, Vietnam"

        geolocator = Nominatim(user_agent="picar_vehicle_app")

        try:
            # Gọi dịch vụ lấy tọa độ
            location = geolocator.geocode(full_address)

            if location:
                self.lat = location.latitude
                self.lng = location.longitude
                print(f"Success: {full_address} -> ({self.lat}, {self.lng})")
                return True
            else:
                print(f"Error: Không tìm thấy tọa độ cho địa chỉ: {full_address}")
                return False

        except GeocoderTimedOut:
            print("Error: Dịch vụ định vị bị quá tải (Timeout).")
            return False

    def get_coordinates(self):
        """Trả về tuple tọa độ"""
        return (self.lat, self.lng)

    def save_to_database(self, vehicle_id):
        """
        Lưu địa chỉ vào bảng VehicleAddress trên Supabase.
        vehicle_id: ID của xe mà địa chỉ này thuộc về.
        """
        # 1. Tự động cập nhật tọa độ nếu lat/lng đang trống
        if self.lat is None or self.lng is None:
            print("Đang lấy tọa độ GPS từ địa chỉ...")
            self.update_gps_from_address()

        # 2. Chuẩn bị dữ liệu theo cấu trúc bảng trong Database
        address_data = {
            "VehicleID": vehicle_id,
            "Detail": self.detail,
            "Ward": self.commune,
            "City": self.city,
            "Latitude": self.lat,
            "Longitude": self.lng
        }

        try:
            # 3. Gọi Supabase để insert dữ liệu
            # Giả sử ApiService.client là đối tượng supabase đã được init
            result = supabase.table("VehicleAddress").insert(address_data).execute()

            if result.data:
                print(f"Lưu địa chỉ thành công cho xe ID: {vehicle_id}")
                return {"status": "success", "data": result.data}
            else:
                return {"status": "error", "message": "Không có dữ liệu trả về"}

        except Exception as e:
            print(f"Lỗi khi lưu vào Database: {str(e)}")
            return {"status": "error", "message": str(e)}

def calculate_address_distance(addr1: Address, addr2: Address):
    """
    Tính khoảng cách giữa 2 đối tượng Address dùng công thức Haversine (đơn vị: km).
    """
    # Lấy tọa độ từ các getter của class Address
    lat1, lon1 = addr1.lat, addr1.lng
    lat2, lon2 = addr2.lat, addr2.lng

    # Bán kính Trái Đất trung bình là 6371 km
    R = 6371.0

    # Chuyển đổi sang radian
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    # Công thức Haversine
    a = (math.sin(d_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return round(distance, 2)  # Trả về kết quả làm tròn 2 chữ số thập phân
class VehicleAddress:
    def __init__(self, detail, ward_commune, province_city, latitude, longitude):
        # 1. Số nhà, đường, xóm...
        self.detail = detail

        # 2. Cấp cơ sở (Phường/Xã/Đặc khu)
        self.ward_commune = ward_commune

        # 3. Cấp tỉnh (34 tỉnh thành mới)
        self.province_city = province_city

        # Tọa độ GPS để tính xe gần nhất
        self.latitude = float(latitude)
        self.longitude = float(longitude)

    @property
    def detail(self): return self.__detail

    @property
    def ward_commune(self): return self.__ward_commune

    @property
    def province_city(self): return self.__province_city

    @property
    def lat(self): return self.__lat

    @property
    def lng(self): return self.__lng

    @detail.setter
    def detail(self, value): self.__detail = value

    @ward_commune.setter
    def ward_commune(self, value): self.__ward_commune = value

    @province_city.setter
    def province_city(self, value): self.__province_city = value

    @lat.setter
    def lat(self, value): self.__lat = float(value)

    @lng.setter
    def lng(self, value): self.__lng = float(value)

    def get_full_address(self):
        """Định dạng địa chỉ chuẩn 2025: [Chi tiết], [Cấp Xã], [Cấp Tỉnh]"""
        return f"{self.detail}, {self.ward_commune}, {self.province_city}"

    def to_dict(self):
        """Chuyển đổi thành dictionary để gửi qua API JSON"""
        return {
            "detail": self.__detail,
            "ward_commune": self.__ward_commune,
            "province_city": self.__province_city,
            "full_address": self.get_full_address(),
            "lat": self.__lat,
            "lng": self.__lng
        }
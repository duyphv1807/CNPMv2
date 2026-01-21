from datetime import date
from Backend.ExcuteDatabase import supabase
import re
from Backend.Helpers import generate_id, save_driving_license_data, upload_image_to_storage
from datetime import datetime

class User:
    def __init__(self, full_name: str, nation_id: str, date_of_birth: date,
                 phone_number: str, email: str, driving_license: str, password: str,
                 avatar: str, number_vehicle_own: int = 0, star: int = 5,user_id: str = None):

        # Gán qua setter để validation hoạt động
        self.user_id = user_id if user_id else generate_id("US")
        self.full_name = full_name
        self.date_of_birth = date_of_birth
        self.phone_number = phone_number
        self.avatar = avatar
        self.number_vehicle_own = number_vehicle_own

        # Các thuộc tính private/protected (snake_case)
        self._nation_id = nation_id
        self._driving_license = driving_license
        self._email = email
        self._password = password
        self._star = star

        @property
        def user_id(self):
            return self.__user_id

        @user_id.setter
        def user_id(self, value):
            if len(value) != 10:
                raise ValueError("UserID phải có đúng 10 ký tự!")
            self.__user_id = value

        # --- 2. PASSWORD PROPERTY ---
        @property
        def password(self):
            return "********"

        @password.setter
        def password(self, value):
            if not (6 <= len(value) <= 20):
                raise ValueError("Mật khẩu phải từ 6-20 ký tự!")
            if not re.search(r'[A-Z]', value):
                raise ValueError("Mật khẩu phải có ít nhất 1 chữ cái viết hoa!")
            if not re.search(r'[0-9]', value):
                raise ValueError("Mật khẩu phải có ít nhất 1 chữ số!")
            self._password = value
        # --- GETTER/SETTER CHO NATION ID (CCCD) ---
        @property
        def nation_id(self):
            # Chỉ hiển thị 3 số cuối để bảo mật (Masking)
            return f"*******{self.__nation_id[-3:]}"

        @nation_id.setter
        def nation_id(self, value):
            if len(value) != 12:  # Kiểm tra độ dài cơ bản
                raise ValueError("Số CCCD không hợp lệ!")
            self.__nation_id = value

        # --- GETTER/SETTER CHO DRIVING LICENSE ---
        @property
        def driving_license(self):
            # Trả về dạng viết hoa toàn bộ để đồng bộ
            return self.__driving_license.upper()

        @driving_license.setter
        def driving_license(self, value):
            if not value:
                raise ValueError("Giấy phép lái xe không được để trống!")
            self.__driving_license = value

        # --- CÁC THUỘC TÍNH KHÁC GIỮ NGUYÊN ---
        @property
        def email(self):
            return self._email

        @email.setter
        def email(self, value):
            if "@" not in value: raise ValueError("Email sai định dạng!")
            self._email = value

    # --- Methos ---
    # --- HÀM CHUYỂN ĐỔI SANG DICT ---
    def to_dict(self):
        return {
            "UserID": self.user_id,
            "FullName": self.full_name,
            "NationID": self._nation_id,
            "DateOfBirth": str(self.date_of_birth),
            "PhoneNumber": self.phone_number,
            "Email": self._email,
            "DrivingLicense": self._driving_license,
            "Password": self._password,
            "Avatar": self.avatar,
            "NumberVehicleOwn": self.number_vehicle_own,
            "Star": self._star,
            "ClassifyUser": "USER"  # Gán thẳng giá trị tại đây
        }

    # --- HÀM LƯU VÀO DATABASE ---
    def save_to_db(self):
        max_retries = 3
        attempts = 0
        while attempts < max_retries:
            try:
                return supabase.table("User_Admin").insert(self.to_dict()).execute()
            except Exception as e:
                error_str = str(e).lower()

                # Kiểm tra lỗi vi phạm tính duy nhất (Unique Violation)
                if "23505" in error_str or "duplicate key value" in error_str:

                    # TRƯỜNG HỢP 1: Trùng Primary Key (UserID) -> Có thể tự generate lại
                    if "user_admin_pkey" in error_str or "userid" in error_str:
                        attempts += 1
                        new_id = generate_id("US")
                        print(f"⚠️ Trùng UserID {self._user_id}, thử lại với mã mới: {new_id}")
                        self._user_id = new_id
                        continue  # Thử lại vòng lặp

                    # TRƯỜNG HỢP 2: Trùng NationID -> Báo lỗi cho người dùng, không thử lại
                    elif "nationid" in error_str:
                        print(f"❌ Lỗi: Số CCCD/NationID '{self._nation_id}' đã tồn tại trên hệ thống!")
                        return None

                    # TRƯỜNG HỢP 3: Trùng DrivingLicense -> Báo lỗi cho người dùng, không thử lại
                    elif "driving_license" in error_str:
                        print(f"❌ Lỗi: Giấy phép lái xe '{self._driving_license}' đã được đăng ký!")
                        return None

                    else:
                        print(f"❌ Lỗi trùng lặp dữ liệu: {e}")
                        return None

                else:
                    # Các lỗi khác (Kết nối, sai kiểu dữ liệu...)
                    print(f"❌ Lỗi Database: {e}")
                    return None
        return None

    @classmethod
    def register_user(cls, data):
        try:
            # 1. Khởi tạo User trước (để lấy user_id định danh duy nhất)
            dob_source = data.get('dob')
            dob_obj = datetime.strptime(dob_source, '%d/%m/%Y').date() if isinstance(dob_source, str) else dob_source

            new_user = cls(
                full_name=data.get('fullname'),
                nation_id=data.get('nation_id'),
                date_of_birth=dob_obj,
                phone_number=data.get('phone'),
                email=data.get('email'),
                driving_license=data.get('license_no'),
                password=data.get('password'),
                avatar="default_avatar.png",  # Tạm thời để mặc định
                user_id=None  # Hệ thống tự tạo USxxxxxx
            )

            # 2. Xử lý Avatar ĐỊNH DANH THEO USER_ID
            avatar_source = data.get('avatar')
            # LƯU Ý: Kiểm tra tên Bucket chính xác trên Supabase (Ví dụ: "Avatar")
            target_bucket = "Avatar"

            if avatar_source and avatar_source != "default_avatar.png":
                uploaded_url = upload_image_to_storage(
                    avatar_source,
                    f"{new_user.user_id}_avatar.jpg",
                    bucket=target_bucket
                )
                if uploaded_url:
                    new_user.avatar = uploaded_url
                else:
                    # Nếu upload lỗi, gán ảnh mặc định để không bị lỗi DB
                    new_user.avatar = "https://tdkmoeyqaejiucanbgdj.supabase.co/storage/v1/object/public/Avatar/avatar.jpg"
            else:
                new_user.avatar = "https://tdkmoeyqaejiucanbgdj.supabase.co/storage/v1/object/public/Avatar/avatar.jpg"

            # 3. Lưu bảng User_Admin
            user_response = new_user.save_to_db()

            if user_response:
                # Khởi tạo ví với số dư 0 VNĐ cho owner là new_user vừa tạo
                from Backend.Model.Wallet import Wallet
                #Impport tại đây để tránh lỗi vòng lặp
                new_wallet = Wallet(owner=new_user, balance=0)
                wallet_response = new_wallet.create_wallet()

                if wallet_response:
                    print(f"--> [SYSTEM] Tạo ví thành công cho User: {new_user.user_id}")
                else:
                    print(f"--> [WARNING] User đã tạo nhưng ví bị lỗi.")

                # 4. Lưu bảng DrivingLicense (Giữ nguyên)
                save_driving_license_data(
                    data.get('license_no'),
                    data.get('front_img'),
                    data.get('back_img'),
                    data.get('license_class')
                )
                return True, "Đăng ký thành công và đã tạo ví điện tử!"

            return False, "Lỗi khi lưu dữ liệu người dùng."

        except Exception as e:
            return False, f"Lỗi hệ thống: {str(e)}"

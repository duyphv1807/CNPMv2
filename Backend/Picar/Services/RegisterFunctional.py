from datetime import datetime
from Backend.Picar.Utils.DrivingLicenseDetect import save_driving_license_data
from Backend.Picar.ExcuteDatabase import upload_image_to_storage
from Backend.Picar.Model.User import User
from Backend.Picar.Model.Wallet import Wallet

def register_logic(data):
    try:
        # 1. Xử lý ngày sinh
        dob_source = data.get('dob')
        try:
            dob_obj = datetime.strptime(dob_source, '%d/%m/%Y').date() if isinstance(dob_source, str) else dob_source
        except Exception:
            dob_obj = datetime.now().date()  # Giá trị dự phòng

        # 2. Tạo ID trước để định danh file ảnh (Ví dụ gọi hàm tạo ID của bạn)
        # Giả sử: temp_user_id = User.generate_new_id()

        # 3. Xử lý Upload Avatar trước khi lưu DB
        avatar_source = data.get('avatar')
        default_url = "https://tdkmoeyqaejiucanbgdj.supabase.co/storage/v1/object/public/Avatar/avatar.jpg"
        final_avatar_url = default_url

        if avatar_source and avatar_source != "default_avatar.png":
            # Upload ảnh và lấy URL trực tiếp
            uploaded_url = upload_image_to_storage(
                avatar_source,
                f"avatar_{data.get('phone')}.jpg",  # Dùng phone làm định danh tạm nếu chưa có ID
                bucket="Avatar"
            )
            if uploaded_url:
                final_avatar_url = uploaded_url

        # 4. Khởi tạo Object User với đầy đủ thông tin (bao gồm URL ảnh)
        new_user = User(
            full_name=data.get('fullname'),
            nation_id=data.get('nation_id'),
            date_of_birth=dob_obj,
            phone_number=data.get('phone'),
            email=data.get('email'),
            driving_license=data.get('license_no'),
            password=data.get('password'),
            avatar=final_avatar_url,
            user_id=None  # Đảm bảo hàm save_to_db của bạn tự tạo USxxxxxx
        )

        # 5. Lưu vào bảng User_Admin
        user_response = new_user.save_to_db()
        if not user_response:
            return False, "Lỗi: Không thể lưu thông tin tài khoản vào hệ thống."

        # 6. Tạo ví điện tử (Chỉ khi User đã lưu thành công)
        try:
            new_wallet = Wallet(owner=new_user, balance=0)
            new_wallet.create_wallet()
            print(f"--> [SYSTEM] Tạo ví thành công cho: {data.get('email')}")
        except Exception as wallet_err:
            print(f"--> [WARNING] Lỗi tạo ví: {wallet_err}")

        # 7. Lưu thông tin bằng lái (Bước OCR từ Step 2)
        save_driving_license_data(
            data.get('license_no'),
            data.get('front_img'),
            data.get('back_img'),
            data.get('license_class')
        )

        return True, "Đăng ký thành công!"

    except Exception as e:
        print(f"--> [CRITICAL ERROR] Register Logic: {str(e)}")
        return False, f"Lỗi hệ thống: {str(e)}"
if __name__ == "__main__":
    data = {
        'fullname': 'duy',
        'nation_id': '082134658429',
        'dob': '07/07/1985',
        'phone': '0679753473',
        'email': 'coigaimupp@gamil.com',
        'license_no': '044463044045',
        'license_class': 'D',
        # Lưu ý: Đường dẫn ảnh phải là đường dẫn thực tế trên máy bạn để test ko bị lỗi
        'front_img': 'C:/Users/ASUS/OneDrive/Máy tính/bài tập/test/a1.jpg',
        'back_img': 'C:/Users/ASUS/OneDrive/Máy tính/bài tập/test/back.jpg',
        "password": "Abc123"
    }
    register_logic(data)

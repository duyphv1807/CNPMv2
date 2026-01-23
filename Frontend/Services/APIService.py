import requests

# Địa chỉ IP của máy tính chạy Flask (Thay đổi theo IP máy bạn)
SERVER_IP = "http://192.168.100.70:5000/api" #đoạn này có thể thay đổi
BASE_URL = SERVER_IP
class ApiService:
    @staticmethod
    def login_api(account, password):
        """
        Gửi yêu cầu đăng nhập tới Flask Server.
        """
        try:
            url = f"{BASE_URL}/login"
            # Đóng gói dữ liệu vào JSON
            payload = {
                "account": account,
                "password": password
            }

            # Thực hiện gửi lệnh POST
            response = requests.post(url, json=payload, timeout=5)

            # Trả về kết quả dưới dạng Dictionary
            return response.json()

        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Không thể kết nối tới Server. Vui lòng kiểm tra Wifi hoặc IP."}
        except Exception as e:
            return {"status": "error", "message": f"Lỗi không xác định: {str(e)}"}

    @staticmethod
    def register_api(data):
        try:
            url = f"{BASE_URL}/register"
            # Gửi dữ liệu dưới dạng JSON
            response = requests.post(url, json=data, timeout=15)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": f"Kết nối thất bại: {str(e)}"}

    @staticmethod
    def send_otp_api(email):
        try:
            # Route này khớp với endpoint bạn đã tạo trong Backend/Picar/Routes.py
            url = f"{BASE_URL}/send-otp"
            response = requests.post(url, json={"email": email}, timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def verify_otp_api(email, otp_code):
        """
        Gửi mã OTP và email lên server để xác thực.
        :param email: Email của người dùng cần reset mật khẩu.
        :param otp_code: Chuỗi 6 số OTP người dùng vừa nhập.
        :return: Dictionary chứa status và message từ server.
        """
        try:
            url = f"{BASE_URL}/verify-otp"

            # Dữ liệu gửi đi phải khớp với key mà Backend đang đợi (request.json.get('...'))
            payload = {
                "email": email,
                "otp_code": otp_code
            }

            response = requests.post(
                url,
                json=payload,
                timeout=10  # Thời gian chờ tối đa 10 giây
            )

            # Chuyển đổi phản hồi từ Server thành Dictionary
            return response.json()

        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Không thể kết nối tới Server. Vui lòng kiểm tra mạng!"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Lỗi không xác định: {str(e)}"
            }
    @staticmethod
    def locate_api(access_status, lat, lng):
        """
        Gửi yêu cầu vị trí lên Backend thông qua phương thức POST.
        """
        try:
            response = requests.post(
                f"{BASE_URL}/handle-locate",
                json={
                    "access": access_status,
                    "lat": lat,
                    "lng": lng
                }
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
import requests

# Địa chỉ IP của máy tính chạy Flask (Thay đổi theo IP máy bạn)

SERVER_IP = "http://192.168.1.31:5000/api" #đoạn này có thể thay đổi


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

    @staticmethod
    def get_fillter_api():
        """
        Gọi API Backend để lấy danh sách Brand và Color duy nhất từ Database.
        """
        try:
            # Gửi yêu cầu POST đến endpoint /get_fillter
            response = requests.post(f"{BASE_URL}/get-fillter", timeout=10)

            # Kiểm tra trạng thái phản hồi từ Server
            if response.status_code == 200:
                # Trả về dữ liệu JSON chứa {status, brands, colors}
                return response.json()
            else:
                # Trả về lỗi nếu server phản hồi mã không phải 200
                return {
                    "status": "error",
                    "message": f"Server error: {response.status_code}"
                }

        except requests.exceptions.RequestException as e:
            # Xử lý các lỗi kết nối (Timeout, Connection refused, v.v.)
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}"
            }

    @staticmethod
    def search_api(filters, user_lat, user_lng):
        """
        Gửi yêu cầu tìm kiếm kèm tọa độ người dùng để tính khoảng cách.
        """
        try:
            # 1. Tạo bản sao của filters để tránh ghi đè dữ liệu gốc ở UI
            payload = filters.copy() if filters else {}

            # 2. Gộp tọa độ vào payload gửi đi
            payload["user_lat"] = user_lat
            payload["user_lng"] = user_lng

            # 3. Gửi yêu cầu POST đến Backend
            response = requests.post(
                f"{BASE_URL}/search",
                json=payload,
                timeout=10  # Tránh treo App nếu server phản hồi chậm
            )

            # 4. Kiểm tra phản hồi
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"Server returned error {response.status_code}",
                    "details": response.text
                }

        except requests.exceptions.Timeout:
            return {"status": "error", "message": "Yêu cầu quá thời hạn (Timeout)"}
        except requests.exceptions.ConnectionError:
            return {"status": "error", "message": "Không thể kết nối đến máy chủ"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def update_account_api(payload):
        try:
            url = f"{BASE_URL}/update_account"
            # Đảm bảo payload gửi đi chứa đúng các key mà Backend mong đợi
            # Frontend truyền: client -> Backend nhận: phone_number
            formatted_payload = {
                "user_id": payload.get("user_id"),
                "full_name": payload.get("full_name"),
                "email": payload.get("email"),
                "phone_number": payload.get("phone"),  # Khớp với cột PhoneNumber
                "DateOfBirth": payload.get("dob"),
                "password": payload.get("password")
            }
            response = requests.post(url, json=formatted_payload, timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @staticmethod
    def get_account_api(user_id):
        try:
            url = f"{BASE_URL}/account"
            # Gửi request lấy thông tin
            response = requests.post(url, json={"user_id": user_id}, timeout=15)
            result = response.json()

            # DEBUG: In ra để kiểm tra Backend trả về đủ cột chưa
            print(f"--- API DEBUG (Get Account): {result} ---")
            return result
        except Exception as e:
            return {"status": "error", "message": f"Kết nối thất bại: {str(e)}"}
    @staticmethod
    def locate_api(use_coords, lat=None, lng=None):
        try:
            url = f"{BASE_URL}/get_location"
            params = {"lat": lat, "lng": lng} if use_coords else {}
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
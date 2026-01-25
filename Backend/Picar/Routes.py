from flask import request, jsonify
from Backend.Picar import app
from .Services.LoginFunctional import login_logic
from .Services.RegisterFunctional import register_logic
from .Model.OTP import OTP
from .Services.AuthService import AuthService
from .Services.Location import locate_logic
from .ExcuteDatabase import get_unique_filters
from .Services.SearchFunctional import search_logic
@app.route("/api/login", methods=["POST"])
def handle_login():
    try:
        # 1. Nhận gói dữ liệu JSON gửi từ Flet
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Không nhận được dữ liệu"}), 400

        # Trích xuất tài khoản và mật khẩu
        account = data.get("account")
        password = data.get("password")

        # 2. Kiểm tra dữ liệu đầu vào cơ bản
        if not account or not password:
            return jsonify({"status": "error", "message": "Thiếu tài khoản hoặc mật khẩu"}), 400

        # 3. Gọi phòng chuyên môn (AuthService) để thực hiện tác vụ kiểm tra
        result = login_logic(account, password)

        # 4. Trả kết quả về cho Frontend
        if result["status"] == "success":
            # Trả về mã 200 (Thành công)
            return jsonify(result), 200
        else:
            # Trả về mã 401 (Lỗi xác thực)
            return jsonify(result), 401

    except Exception as e:
        print(f"Lỗi tại Routes: {e}")
        return jsonify({"status": "error", "message": "Lỗi máy chủ nội bộ"}), 500

@app.route("/api/register", methods=["POST"])
def handle_register():
    print("\n" + "=" * 50, flush=True)
    print("--> [GATEWAY] ĐÃ NHẬN REQUEST ĐĂNG KÝ", flush=True)
    print("=" * 50 + "\n", flush=True)
    try:
        # 1. Nhận dữ liệu JSON từ App Flet gửi lên
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "Không nhận được dữ liệu đăng ký"}), 400

        # 2. Gọi hàm logic xử lý đăng ký (Lưu User, GPLX, Tạo Ví)
        # register_logic trả về một tuple (True/False, "Thông báo")
        success, message = register_logic(data)

        # 3. Phản hồi kết quả cho Frontend
        if success:
            return jsonify({
                "status": "success",
                "message": message
            }), 201  # 201 Created: Tạo tài khoản mới thành công
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 400

    except Exception as e:
        print(f"Lỗi tại Route Đăng ký: {e}")
        return jsonify({
            "status": "error",
            "message": "Lỗi hệ thống khi xử lý đăng ký"}), 500

@app.route('/api/send-otp', methods=['POST'])
async def handle_send_otp():
    # 1. Lấy email từ body mà Frontend gửi lên (json={"email": "..."})
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"status": "error", "message": "Thiếu thông tin Email!"}), 400

    # 2. Gọi Service để tạo OTP, lưu DB và gửi mail
    success, message = await AuthService.request_otp_reset_password(email)

    # 3. Trả kết quả về cho Frontend
    if success:
        return jsonify({"status": "success", "message": message}), 200
    else:
        return jsonify({"status": "error", "message": message}), 400

@app.route('/api/verify-otp', methods=['POST'])
def handle_verify_otp():
    try:
        # 1. Nhận dữ liệu từ Frontend
        data = request.json
        email = data.get('email')
        user_code = data.get('otp_code')

        if not email or not user_code:
            return jsonify({
                "status": "error",
                "message": "Thiếu Email hoặc mã OTP"
            }), 400

        # 2. Gọi hàm verify_otp (Phương thức static bạn đã viết trong Class OTP)
        # Hàm này trả về (True/False, "Thông báo")
        success, message = OTP.verify_otp(email, user_code)

        # 3. Phản hồi kết quả
        if success:
            return jsonify({
                "status": "success",
                "message": message
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), 400

    except Exception as e:
        print(f"Lỗi tại Route Verify OTP: {e}")
        return jsonify({
            "status": "error",
            "message": "Lỗi hệ thống khi xác thực mã"
        }), 500


@app.route('/api/handle-locate', methods=['POST'])
def handle_locate():
    try:
        # Lấy dữ liệu JSON từ request
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        # Frontend gửi lên trạng thái cấp quyền và tọa độ
        access = data.get('access')
        lat = data.get('lat')
        lng = data.get('lng')

        # Kiểm tra logic: Nếu có quyền truy cập nhưng thiếu tọa độ
        if access and (lat is None or lng is None):
            return jsonify({"status": "error", "message": "Missing coordinates"}), 400

        # Gọi hàm xử lý trong Service Backend
        result = locate_logic(access, lat, lng)

        # Trả về kết quả thành công
        return jsonify(result), 200

    except Exception as e:
        # Ghi log lỗi tại đây nếu cần (ví dụ: logging.error(str(e)))
        return jsonify({
            "status": "error",
            "message": "Internal Server Error",
            "details": str(e)  # Bạn có thể ẩn details này khi deploy thật để bảo mật
        }), 500

@app.route('/api/get-fillter', methods=['POST'])
def get_fillter():
    try:
        # Gọi hàm xử lý logic để truy vấn Brand và Color duy nhất từ Supabase
        result = get_unique_filters()

        # Kiểm tra nếu hàm logic trả về trạng thái lỗi
        if result.get("status") == "error":
            return jsonify(result), 400

        # Trả về dữ liệu filters (brands, colors) cho Frontend
        return jsonify(result), 200

    except Exception as e:
        # Xử lý các lỗi phát sinh ngoài dự kiến của hệ thống
        return jsonify({
            "status": "error",
            "message": "Internal Server Error",
            "details": str(e)
        }), 500


def handle_search():
    try:
        # 1. Lấy toàn bộ dữ liệu JSON từ Frontend gửi lên
        data = request.json

        # Kiểm tra tính hợp lệ của dữ liệu đầu vào
        if not data:
            return jsonify({
                "status": "error",
                "message": "Không tìm thấy dữ liệu yêu cầu (Missing JSON body)"
            }), 400

        # 2. Bóc tách tọa độ người dùng và bộ lọc
        # Lưu ý: Các key này phải khớp với key mà APIService.py gửi lên
        u_lat = data.get("user_lat")
        u_lng = data.get("user_lng")

        # filters chứa các thông tin còn lại như brands, categories, details...
        filters = data

        # 3. Gọi hàm logic xử lý tìm kiếm chuyên sâu
        # Truyền cả filters và cặp tọa độ để tính khoảng cách & match_score
        result = search_logic(filters, u_lat, u_lng)

        # 4. Phản hồi kết quả cho Frontend
        if result.get("status") == "success":
            # Trả về mã 200 kèm danh sách xe đã được sắp xếp
            return jsonify(result), 200
        else:
            # Trả về mã 500 nếu có lỗi trong quá trình truy vấn Supabase
            return jsonify(result), 500

    except Exception as e:
        # Bắt các lỗi hệ thống không lường trước
        print(f"Lỗi Route handle_search: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Lỗi máy chủ nội bộ",
            "details": str(e)
        }), 500

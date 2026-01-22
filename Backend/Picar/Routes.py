from flask import request, jsonify
from . import app
from .Services.LoginFunctional import login_logic
from .Services.RegisterFunctional import register_logic
from .Model.OTP import OTP
from .Services.AuthService import AuthService



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
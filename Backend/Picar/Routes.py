from flask import request, jsonify
from Backend.Picar import app
from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Services.LoginFunctional import login_logic
from Backend.Picar.Services.RegisterFunctional import register_logic
from Backend.Picar.Model.OTP import OTP
from Backend.Picar.Services.AuthService import AuthService

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

#====== ACCOUNT SECTION ==========

# Tại Backend (Server)
@app.route('/api/account', methods=['POST'])
def get_account():
    data = request.json
    user_id = data.get("user_id")

    # Dùng .select("*") để lấy hết tất cả các cột trong bảng User_Admin
    result = supabase.table("User_Admin").select("*").eq("UserID", user_id).single().execute()

    if result.data:
        # Đảm bảo trả về đúng tên các trường mà Frontend đang mong đợi
        return {
            "status": "success",
            "data": {
                "UserID": result.data.get("UserID"),
                "FullName": result.data.get("FullName"),
                "Email": result.data.get("Email"),
                "PhoneNumber": result.data.get("PhoneNumber"),  # THÊM DÒNG NÀY
                "DateOfBirth": result.data.get("DateOfBirth"),  # DÙNG ĐÚNG TÊN NÀY
                "Avatar": result.data.get("Avatar")
            }
        }
    return {"status": "error", "message": "User not found"}


@app.route('/api/update_account', methods=['POST'])
def update_account():
    try:
        data = request.json
        user_id = data.get("user_id")

        # 1. Chuẩn bị dữ liệu để update
        update_vals = {
            "FullName": data.get("full_name"),
            "Email": data.get("email"),
            "PhoneNumber": data.get("phone_number"),
        }

        # 2. Xử lý riêng cho DateOfBirth để tránh lỗi định dạng
        dob_value = data.get("dob")
        if dob_value and dob_value.strip() != "":
            # Đảm bảo cột trong Supabase của bạn tên là 'DateOfBirth'
            # (Kiểm tra lại trên Supabase Dashboard xem là DOB hay DateOfBirth)
            update_vals["DateOfBirth"] = dob_value
        else:
            update_vals["DateOfBirth"] = None  # Gán NULL nếu trống

        # 3. Thực hiện Update
        result = supabase.table("User_Admin").update(update_vals).eq("UserID", user_id).execute()

        if result.data:
            return jsonify({"status": "success", "message": "Cập nhật thành công"}), 200
        else:
            return jsonify({"status": "error", "message": "Không tìm thấy User để cập nhật"}), 404

    except Exception as e:
        print(f"Lỗi Update Account: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

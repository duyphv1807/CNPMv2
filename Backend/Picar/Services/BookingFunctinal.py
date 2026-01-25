from datetime import datetime
from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Model.User import User
from Backend.Picar.Model.Vehicle import Vehicle
from Backend.Picar.Model.Booking import Booking  # Đảm bảo bạn đã import class Booking


def booking_logic(renter_data: dict, vehicle_data: dict, start_date_str: str, end_date_str: str):
    """
    Logic chính để thực hiện đặt xe:
    1. Kiểm tra ví tiền của người thuê.
    2. Kiểm tra xe có đang rảnh không.
    3. Tạo đơn hàng và trừ tiền ví.
    """
    try:
        # 1. Chuyển đổi dữ liệu input sang Object
        # Giả sử renter_data và vehicle_data chứa đầy đủ thông tin để init Object
        renter = User(user_id=renter_data.get("UserID"),
                      full_name=renter_data.get("FullName"),
                      wallet_balance=renter_data.get("WalletBalance", 0))

        # Lấy thông tin chủ xe từ vehicle_data (giả định có OwnerID hoặc Owner object)
        owner_info = vehicle_data.get("User_Admin", {})
        owner = User(user_id=owner_info.get("UserID"), full_name=owner_info.get("FullName"))

        vehicle = Vehicle(brand=vehicle_data.get("Brand"),
                          rental_price=float(vehicle_data.get("RentalPrice")),
                          vehicle_id=vehicle_data.get("VehicleID"))

        start_date = datetime.fromisoformat(start_date_str).date()
        end_date = datetime.fromisoformat(end_date_str).date()

        # 2. Khởi tạo đối tượng Booking để tính tiền tự động
        new_booking = Booking(
            renter=renter,
            owner=owner,
            vehicle=vehicle,
            start_date=start_date,
            end_date=end_date
        )

        total_price = new_booking.total_price

        # 3. KIỂM TRA ĐIỀU KIỆN THUÊ
        # A. Kiểm tra số dư ví
        if renter.wallet_balance < total_price:
            return {"status": "error",
                    "message": f"Số dư ví không đủ. Cần thêm {total_price - renter.wallet_balance:,.0f} đ"}

        # B. Kiểm tra trạng thái xe (Double check với DB)
        current_vehicle = supabase.table("Vehicle_Bike_Motorbike_Car_Truck_Boat") \
            .select("Status").eq("VehicleID", vehicle.vehicle_id).single().execute()

        if current_vehicle.data.get("Status") != "AVAILABLE":
            return {"status": "error", "message": "Rất tiếc, xe vừa mới được người khác đặt hoặc đang bảo trì."}

        # 4. THỰC HIỆN TRANSACTION (Giao dịch)
        # Bước 1: Trừ tiền người thuê
        new_balance = renter.wallet_balance - total_price
        update_wallet = supabase.table("User").update({"WalletBalance": new_balance}) \
            .eq("UserID", renter.user_id).execute()

        if not update_wallet.data:
            raise Exception("Không thể cập nhật ví tiền.")

        # Bước 2: Lưu đơn hàng Booking
        booking_res = new_booking.save_to_db()
        if not booking_res:
            # Rollback ví tiền nếu lưu đơn hàng lỗi (Giao dịch an toàn)
            supabase.table("User").update({"WalletBalance": renter.wallet_balance}) \
                .eq("UserID", renter.user_id).execute()
            raise Exception("Lỗi hệ thống khi tạo đơn hàng.")

        # Bước 3: Cập nhật trạng thái xe sang RENTED
        supabase.table("Vehicle_Bike_Motorbike_Car_Truck_Boat") \
            .update({"Status": "RENTED"}).eq("VehicleID", vehicle.vehicle_id).execute()

        return {
            "status": "success",
            "message": "Đặt xe thành công!",
            "booking_id": new_booking.booking_id,
            "total_price": total_price
        }

    except Exception as e:
        print(f"❌ Booking Logic Error: {e}")
        return {"status": "error", "message": str(e)}

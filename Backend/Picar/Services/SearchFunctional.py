from Backend.Picar.ExcuteDatabase import supabase
from Backend.Picar.Model.Address import Address, calculate_address_distance
def search_logic(filters, u_lat, u_lng):
    """
    Hàm tìm kiếm xe tổng hợp:
    1. Lọc cứng từ Database (Category, Brand, Color, City).
    2. Join bảng địa chỉ và bảng chủ xe (Rating).
    3. Tính khoảng cách thực tế giữa người thuê và xe.
    4. Sắp xếp theo điểm số ưu tiên (Best Match).
    """
    try:
        # --- BƯỚC 1: TRUY VẤN DỮ LIỆU CƠ BẢN (JOIN 3 BẢNG) ---
        query = supabase.table("Vehicle_Bike_Motorbike_Car_Truck_Boat").select(
            "*, "
            "VehicleAddress!inner(*), "  # Lấy tọa độ và địa chỉ chi tiết
            "User_Admin:OwnerID(Rating)"  # Lấy Rating của chủ xe
        )

        # --- BƯỚC 2: ÁP DỤNG BỘ LỌC CỨNG ---
        # Lọc theo Thành phố (Nếu có)
        city_input = filters.get("location")
        if city_input and city_input != "None":
            query = query.ilike("VehicleAddress.City", f"%{city_input}%")

        # Lọc theo loại xe, nhãn hiệu, màu sắc
        if filters.get("categories"):
            query = query.in_("ClassifyVehicle", filters["categories"])
        if filters.get("brands"):
            query = query.in_("Brand", filters["brands"])
        if filters.get("colors"):
            query = query.in_("Color", filters["colors"])

        # Thực thi lấy dữ liệu từ Supabase
        res = query.execute()
        vehicles = res.data if res.data else []

        # --- BƯỚC 3: TÍNH TOÁN KHOẢNG CÁCH & ĐIỂM SỐ (MATCH SCORE) ---
        # Tạo đối tượng Address cho người thuê
        user_addr = Address(
            detail="", ward_commune="", province_city="",
            latitude=u_lat if u_lat is not None else 10.7769,
            longitude=u_lng if u_lng is not None else 106.7009
        )

        details_filter = filters.get("details", {})

        for vehicle in vehicles:
            score = 0

            # 1. Xử lý khoảng cách
            addr_data = vehicle.get("VehicleAddress", {})
            vehicle_addr = Address(
                detail=addr_data.get("Detail", ""),
                ward_commune=addr_data.get("Ward", ""),
                province_city=addr_data.get("City", ""),
                latitude=addr_data.get("Latitude", 0),
                longitude=addr_data.get("Longitude", 0)
            )

            dist = calculate_address_distance(user_addr, vehicle_addr)
            vehicle["distance_km"] = dist

            # Cộng điểm ưu tiên cho xe gần (trong bán kính 15km)
            if dist < 15:
                score += (15 - dist) * 10

                # 2. Cộng điểm theo Rating của chủ xe
            rating = float(vehicle.get("User_Admin", {}).get("Rating", 0) or 0)
            score += rating * 20

            # 3. Cộng điểm nếu khớp thông số kỹ thuật (Details)
            for key, val in details_filter.items():
                if key in vehicle and vehicle[key] is not None:
                    if str(val).lower() in str(vehicle[key]).lower():
                        score += 50  # Khớp thông số Detail được ưu tiên cao nhất

            vehicle["match_score"] = score

        # --- BƯỚC 4: SẮP XẾP KẾT QUẢ ---
        # Ưu tiên xe có match_score cao nhất lên đầu
        vehicles.sort(key=lambda x: x.get("match_score", 0), reverse=True)

        return {
            "status": "success",
            "data": vehicles,
            "count": len(vehicles)
        }

    except Exception as e:
        print(f"Lỗi search_logic: {str(e)}")
        return {"status": "error", "message": str(e)}
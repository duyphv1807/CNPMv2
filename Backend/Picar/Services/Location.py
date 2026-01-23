from geopy.geocoders import Nominatim

def locate_logic(access_granted, lat, lng):
    """
    Nguyên tắc: Chỉ khi access_granted là True mới xử lý lấy địa chỉ.
    """
    if not access_granted:
        return {"status": "denied", "message": "Quyền truy cập bị từ chối"}

    try:
        # Giả lập gọi API bản đồ (ví dụ Nominatim) để lấy địa chỉ từ lat, lng
        geolocator = Nominatim(user_agent="picar_app")
        location = geolocator.reverse(f"{lat}, {lng}", exactly_one=True)

        return {
            "status": "success",
            "display_name": location.address if location else "Không xác định được địa chỉ",
            "coords": {"lat": lat, "lng": lng}
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
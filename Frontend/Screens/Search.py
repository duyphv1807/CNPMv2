import flet as ft
from Frontend.Style import COLORS
from datetime import datetime
from Frontend.Services.APIService import ApiService

class SearchScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Search",
            padding=0,
            bgcolor="#F5F7FA",
        )

        # --- KHỞI TẠO STATE ---
        self.brand_list = []
        self.colors_list = []

        # Định nghĩa bộ tùy chọn Detail theo từng loại xe
        self.detail_options = {
            "Bike": [("Type", "mountain/road/city"), ("Frame size", "cm"), ("Gear", "levels")],
            "Motorbike": [("Engine", "cc"), ("Type", "manual/auto"), ("License plate", "number")],
            "Car": [("Seating", "seats"), ("Fuel", "type"), ("Transmission", "manual/auto")],
            "Truck": [("Load", "tons"), ("Engine", "type"), ("Dimensions", "m")],
            "Boat": [("Length", "m"), ("Engine", "hp"), ("Capacity", "passengers")]
        }

        # Nạp dữ liệu từ Backend ngay khi khởi tạo
        self.load_filters()

        # --- LẤY DỮ LIỆU TỪ SESSION ---
        saved_location = page.session.store.get("location_name") or "TP. Hồ Chí Minh"
        s_date_raw = page.session.store.get("start_date")
        e_date_raw = page.session.store.get("end_date")

        if s_date_raw and e_date_raw:
            start_dt = datetime.fromisoformat(s_date_raw)
            end_dt = datetime.fromisoformat(e_date_raw)
            time_display = f"{start_dt.strftime('%H:%M')} T{start_dt.weekday() + 2}, {start_dt.strftime('%d/%m')} • {end_dt.strftime('%H:%M')} T{end_dt.weekday() + 2}, {end_dt.strftime('%d/%m')}"
        else:
            time_display = "None"

        # --- 1. SEARCH BAR TOP ---
        self.search_bar = ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW,
                              icon_size=18,
                              icon_color=COLORS["text"],
                              on_click=lambda _: self.page.go("/Dashboard")),
                ft.Column([
                    ft.Text(saved_location, size=14, weight=ft.FontWeight.BOLD, color=COLORS["primary"], no_wrap=True),
                    ft.Text(time_display, size=11, color=COLORS["primary"]),
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.IconButton(ft.Icons.TUNE_ROUNDED, icon_size=20),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            margin=ft.Margin(20, 10, 20, 0),
            padding=ft.Padding(10, 5, 10, 5),
            bgcolor="white",
            border_radius=30,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black"))
        )

        # --- 2. FILTER SECTION ---
        filters = ft.Row([
            self.filter_chip("Category", ft.Icons.DIRECTIONS_CAR_OUTLINED,
                             ["Bike", "Car", "Motorbike", "Truck", "Boat"], page),
            self.filter_chip("Brand", ft.Icons.LANGUAGE, self.brand_list, page),
            self.filter_chip("Color", ft.Icons.COLOR_LENS_OUTLINED, self.colors_list, page),
            self.filter_chip("Rental price", ft.Icons.ATTACH_MONEY, ["Per hour", "Per day"], page),
            self.filter_chip("Detail", ft.Icons.INFO_OUTLINE, None, is_detail=True,page_ref = page),
        ], scroll=ft.ScrollMode.ADAPTIVE, spacing=5)

        self.filter_section = ft.Container(content=filters, padding=ft.Padding(20, 15, 20, 10))

        # --- 3. VEHICLE LIST (GIẢ LẬP) ---
        self.vehicle_list = ft.ListView(
            controls=[
                self.vehicle_card("MITSUBISHI XPANDER 2021", "957", "https://picsum.photos/id/1071/400/220",
                                  ["Số tự động", "7 chỗ", "Xăng"], "4.6"),
                self.vehicle_card("VINFAST VF8 2023", "1.200", "https://picsum.photos/id/183/400/220",
                                  ["Số điện", "5 chỗ", "Điện"], "5.0"),
            ],
            expand=True,
            padding=ft.Padding(20, 0, 20, 100),
            spacing=15
        )

        # --- MAIN LAYOUT (MOBILE WIDTH 380) ---
        self.controls = [
            ft.Container(
                width=380,
                height=800,
                bgcolor="#F5F7FA",
                alignment=ft.Alignment.TOP_CENTER,
                content=ft.Column([
                    self.search_bar,
                    self.filter_section,
                    self.vehicle_list,
                ], spacing=0, expand=True),
                margin=ft.Margin.symmetric(horizontal=(page.width - 380) / 2 if page.width > 380 else 0)
            )
        ]

    def open_filter_sheet(self, title, options, is_detail_mode=False):
        checkboxes = []
        detail_inputs = {}
        display_controls = []  # Danh sách chứa tất cả UI (Text, TextField, Checkbox)

        def close_bs(e):
            selected_items = [cb.label for cb in checkboxes if cb.value]

            if title == "Category":
                self.page.session.store.set("selected_categories", selected_items)
            elif title == "Brand":
                self.page.session.store.set("selected_brands", selected_items)
            elif title == "Color":
                self.page.session.store.set("selected_colors", selected_items)
            elif title == "Rental price":
                # Ánh xạ UI -> Database Value
                mapped_prices = []
                for item in selected_items:
                    if item == "Per hour": mapped_prices.append("Hourly")
                    if item == "Per day": mapped_prices.append("Daily")
                self.page.session.store.set("selected_prices", mapped_prices)

            self.bs.open = False
            self.update_filter_ui()

            self.fetch_filtered_vehicles()

        for opt in options:
            if isinstance(opt, str) and opt.startswith("---"):
                # Tiêu đề nhóm cho Detail
                display_controls.append(
                    ft.Container(
                        content=ft.Text(opt, weight=ft.FontWeight.BOLD, color=COLORS["primary"], size=14),
                        margin=ft.Margin.only(top=10, bottom=5)
                    )
                )
            elif is_detail_mode and isinstance(opt, tuple):
                # Hàng Detail có Đơn vị
                name, unit = opt
                input_field = ft.TextField(
                    hint_text="...", height=35, width=100, text_size=12, color = COLORS["primary"],
                    content_padding=ft.Padding.all(5), border_radius=8
                )
                detail_inputs[name] = input_field
                display_controls.append(
                    ft.Row([
                        ft.Text(f"{name}:", size=14, expand=True, color="black"),
                        input_field,
                        ft.Container(content=ft.Text(unit, size=12, color="grey"), width=60)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
            else:
                # Checkbox mặc định
                cb = ft.Checkbox(
                    label=opt,
                    label_style=ft.TextStyle(color="black", size=14),
                    active_color=COLORS["primary"]
                )
                checkboxes.append(cb)
                display_controls.append(cb)

        self.bs = ft.BottomSheet(
            content=ft.Container(
                width=380,  # Tăng nhẹ width để ko bị sát lề
                padding=20,
                bgcolor="white",
                content=ft.Column([
                    ft.Row([
                        ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=COLORS["primary"]),
                        ft.IconButton(ft.Icons.CLOSE, on_click=close_bs, icon_color=COLORS["primary"])
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(height=1, color="#EEEEEE"),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            controls=display_controls,  # <<< SỬA TẠI ĐÂY: Dùng display_controls
                            spacing=5,  # Để 5 cho dễ nhìn hơn 1
                            scroll=ft.ScrollMode.ADAPTIVE,
                        ),
                        height=400,  # Tăng height để chứa được nhiều detail của nhiều xe
                    ),
                    ft.Container(
                        margin=ft.Margin.only(top=15),
                        alignment=ft.Alignment.CENTER,
                        content=ft.FilledButton(
                            content=ft.Text("Apply", weight=ft.FontWeight.BOLD, color="white"),
                            width=340, height=45,
                            bgcolor=COLORS["primary"],
                            on_click=close_bs,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
                        )
                    )
                ], tight=True)
            ),
            bgcolor="white",
            shape=ft.RoundedRectangleBorder(radius=ft.BorderRadius.only(top_left=20, top_right=20))
        )

        self.page.overlay.append(self.bs)
        self.bs.open = True
        self.page.update()

    def filter_chip(self, label, icon, options, page_ref: ft.Page, is_detail=False):
        # --- LOGIC KIỂM TRA TRẠNG THÁI ACTIVE ---
        is_active = False
        if page_ref and page_ref.session:
            session_data = page_ref.session.store
            if label == "Category":
                is_active = len(session_data.get("selected_categories") or []) > 0
            elif label == "Brand":
                is_active = len(session_data.get("selected_brands") or []) > 0
            elif label == "Color":
                is_active = len(session_data.get("selected_colors") or []) > 0
            elif label == "Rental price":
                is_active = len(session_data.get("selected_prices") or []) > 0
            elif is_detail:
                is_active = len(session_data.get("selected_categories") or []) > 0

        # Thiết lập màu sắc theo trạng thái
        bg_color = COLORS["primary"] if is_active else "white"
        content_color = "white" if is_active else COLORS["text"]
        border_color = COLORS["primary"] if is_active else "#E0E0E0"

        def handle_click(e):
            if is_detail:
                selected_categories = self.page.session.store.get("selected_categories") or []
                if not selected_categories:
                    self.page.snack_bar = ft.SnackBar(ft.Text("Vui lòng chọn ít nhất một Category!"), bgcolor="orange")
                    self.page.snack_bar.open = True
                    self.page.update()
                    return

                combined_details = []
                for cat in selected_categories:
                    if cat in self.detail_options:
                        combined_details.append(f"--- {cat} Details ---")
                        combined_details.extend(self.detail_options[cat])
                self.open_filter_sheet(label, combined_details, is_detail_mode=True)
            else:
                self.open_filter_sheet(label, options)

        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=content_color, size=16),
                ft.Text(label, size=12, color=content_color, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL)
            ], spacing=3),
            padding=ft.Padding(12, 8, 12, 8),
            border=ft.Border.all(1, border_color),
            border_radius=40,
            bgcolor=bg_color,
            on_click=handle_click,
            ink=True
        )

    def vehicle_card(self, name, price, image_url, specs, rating, address="None",
                     distance=None, rental_type="Daily", vehicle_data=None):
        # Xác định đơn vị tiền tệ dựa trên RentalType
        unit = "/giờ" if rental_type == "Hourly" else "/ngày"

        display_address = address if address else "None"
        if distance is not None:
            display_address = f"{display_address} ({distance} km)"

        def on_card_click(e):
            if vehicle_data:
                # LƯU TOÀN BỘ DỮ LIỆU XE VÀO SESSION ĐỂ BOOKING DÙNG
                self.page.session.store.set("selected_vehicle_data", vehicle_data)
                # Chuyển hướng sang màn hình Booking
                self.page.go("/Booking")

        return ft.Container(
            content=ft.Column([
                ft.Stack([
                    ft.Image(src=image_url, border_radius=ft.BorderRadius(15, 15, 0, 0), width=380, height=200,
                             fit="cover"),
                    ft.Container(content=ft.Icon(ft.Icons.FAVORITE_BORDER, color="white", size=20), top=10, right=10),
                ]),
                ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text(name, size=16, weight=ft.FontWeight.BOLD, color="#1A1A1A"),
                        ft.Row([
                            ft.Row([ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=14, color=COLORS["muted"]),
                                    ft.Text(specs[0], size=12, color=COLORS["muted"])], spacing=5),
                            ft.Row([ft.Icon(ft.Icons.PERSON_OUTLINE, size=14, color=COLORS["muted"]),
                                    ft.Text(specs[1], size=12, color=COLORS["muted"])], spacing=5),
                            ft.Row([ft.Icon(ft.Icons.LOCAL_GAS_STATION_OUTLINED, size=14, color=COLORS["muted"]),
                                    ft.Text(specs[2], size=12, color=COLORS["muted"])], spacing=5),
                        ], spacing=15),
                        ft.Row([
                            ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color=COLORS["primary"]),
                            ft.Text(display_address, size=12, color="#444444", italic=True),
                        ], spacing=5),
                        ft.Divider(height=10, color="#F0F0F0"),
                        ft.Row([
                            ft.Row([
                                ft.Icon(ft.Icons.STAR, size=16, color="#FFC107"),
                                ft.Text(rating, size=14, weight=ft.FontWeight.BOLD, color="#1A1A1A"),
                                ft.Text(" • 100+ chuyến", size=11, color="grey")
                            ], spacing=4),
                            ft.Column([
                                # HIỂN THỊ GIÁ KÈM ĐƠN VỊ MỚI
                                ft.Text(f"{price}K{unit}", size=18, weight=ft.FontWeight.BOLD, color="#2ECC71"),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=8)
                )
            ]),
            bgcolor="white",
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black")),
            margin=ft.Margin(0, 5, 0, 5),
            on_click = on_card_click,  # Thêm sự kiện click ở đây
            ink = True
        )

    def load_filters(self):
        result = ApiService.get_fillter_api()
        if result["status"] == "success":
            self.brand_list.clear()
            self.brand_list.extend(result["brands"])
            self.colors_list.clear()
            self.colors_list.extend(result["colors"])
            print(f"Loaded database filters: {len(self.brand_list)} brands")

    def update_filter_ui(self):
        # Dựng lại hàng chip mới với trạng thái màu sắc mới
        # Lúc này dùng self.page vì View đã được gắn vào trang thành công
        updated_row = ft.Row([
            self.filter_chip("Category", ft.Icons.DIRECTIONS_CAR_OUTLINED,
                             ["Bike", "Car", "Motorbike", "Truck", "Boat"], self.page),
            self.filter_chip("Brand", ft.Icons.LANGUAGE, self.brand_list, self.page),
            self.filter_chip("Color", ft.Icons.COLOR_LENS_OUTLINED, self.colors_list, self.page),
            self.filter_chip("Rental price", ft.Icons.ATTACH_MONEY, ["Per hour", "Per day"], self.page),
            self.filter_chip("Detail", ft.Icons.INFO_OUTLINE, None, self.page, is_detail=True),  # Đã thêm self.page
        ], scroll=ft.ScrollMode.ADAPTIVE, spacing=5)

        # Thay thế nội dung cũ trong filter_section
        self.filter_section.content = updated_row
        self.page.update()

    def fetch_filtered_vehicles(self):
        # 1. Thu thập dữ liệu từ session
        store = self.page.session.store

        user_lat = store.get("user_lat") or 10.7769
        user_lng = store.get("user_lng") or 106.7009

        filters = {
            "categories": store.get("selected_categories") or [],
            "brands": store.get("selected_brands") or [],
            "colors": store.get("selected_colors") or [],
            "prices": store.get("selected_prices") or [],
            "details": store.get("detail_values") or {}
        }

        # 2. Hiển thị trạng thái Loading
        self.vehicle_list.controls = [
            ft.Container(content=ft.ProgressRing(), alignment=ft.Alignment.CENTER, padding=50)
        ]
        self.page.update()

        # 3. Gọi API thật
        result = ApiService.search_api(filters, user_lat, user_lng)

        if result.get("status") == "success":
            # 4. Cập nhật giao diện với danh sách xe thật nhận được (Đã được Backend sắp xếp theo khoảng cách)
            self.render_vehicle_results(result["data"])
        else:
            # Xử lý khi có lỗi (Hiện SnackBar)
            error_msg = result.get("message", "Không thể kết nối máy chủ")
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Lỗi: {error_msg}"),
                bgcolor="red"
            )
            self.page.snack_bar.open = True

            # Xóa vòng xoay loading nếu lỗi
            self.vehicle_list.controls.clear()
            self.page.update()

    def render_vehicle_results(self, vehicles_data):
        self.vehicle_list.controls.clear()

        for vehicle in vehicles_data:
            addr_obj = vehicle.get("VehicleAddress", {})
            full_addr = f"{addr_obj.get('Ward', '')}, {addr_obj.get('City', '')}"
            user_obj = vehicle.get("User_Admin", {})
            rating_val = str(user_obj.get("Rating", "0.0"))

            # Tự động điều chỉnh specs dựa trên loại xe thực tế
            specs = [
                vehicle.get("TransmissionType") or vehicle.get("Transmission") or "N/A",
                f"{vehicle.get('SeatingCapacity') or vehicle.get('PassengerCapacity') or 0} chỗ",
                vehicle.get("FuelType") or vehicle.get("EngineType") or "N/A"
            ]

            card = self.vehicle_card(
                name=f"{vehicle.get('Brand')} {vehicle.get('Model', '')}".upper(),
                price=str(vehicle.get("RentalPrice", 0)),
                image_url=vehicle.get("Image"),
                specs=specs,
                rating=rating_val,
                address=full_addr,
                distance=vehicle.get("distance_km"),
                rental_type=vehicle.get("RentalType", "Daily"), # Lấy RentalType từ DB
                vehicle_data = vehicle
            )
            self.vehicle_list.controls.append(card)

        self.page.update()

async def main(page: ft.Page):
    page.views.append(SearchScreen(page))
    page.update()


if __name__ == "__main__":
    ft.run(main)
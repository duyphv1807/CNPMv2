import flet as ft
from Frontend.Style import COLORS
from datetime import datetime, timedelta
from Frontend.Services.APIService import ApiService
import flet_geolocator as fg


class DashboardScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Dashboard",
            bgcolor=COLORS["bg"],
            padding=0,
        )
        user_info = page.session.store.get("user_data")
        display_name = user_info["FullName"] if user_info else "Guest"

        # --- KHÔI PHỤC DỮ LIỆU TỪ SESSION ---
        saved_loc = page.session.store.get("location_name") or "TP. Hồ Chí Minh, Việt Nam"
        s_date_raw = page.session.store.get("start_date")
        e_date_raw = page.session.store.get("end_date")

        self.start_date = datetime.fromisoformat(s_date_raw) if s_date_raw else datetime.now()
        self.end_date = datetime.fromisoformat(e_date_raw) if e_date_raw else datetime.now() + timedelta(days=1)

        # --- STATE ---
        self.rental_mode = "self-driving"
        self.selected_category = "Car"
        self.category_buttons = {}

        # --- OVERLAYS ---
        self.geolocator = fg.Geolocator()
        self.start_date_picker = ft.DatePicker(on_change=self.on_start_date_change, first_date=datetime.now())
        self.end_date_picker = ft.DatePicker(on_change=self.on_end_date_change, first_date=datetime.now())
        self.start_time_picker = ft.TimePicker(on_change=self.on_start_time_change)
        self.end_time_picker = ft.TimePicker(on_change=self.on_end_time_change)

        page.overlay.extend([self.geolocator, self.start_date_picker, self.end_date_picker, self.start_time_picker,
                             self.end_time_picker])

        self.location_text = ft.Text(saved_loc, size=14, weight=ft.FontWeight.BOLD, color="#333333")
        self.product_display = ft.Column(spacing=15)

        # Text objects để cập nhật giao diện khi chọn ngày
        self.txt_start_val = ft.Text(self.start_date.strftime("%d/%m/%Y"), size=14, weight=ft.FontWeight.BOLD,
                                     color="#333333")
        self.txt_end_val = ft.Text(self.end_date.strftime("%d/%m/%Y"), size=14, weight=ft.FontWeight.BOLD,
                                   color="#333333")

        # KHỞI TẠO KHUNG HIỂN THỊ SẢN PHẨM (Nằm trong vùng cuộn riêng)

        # --- NAVIGATION BAR ---
        self.navigation_bar_custom = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.CHAT_BUBBLE_OUTLINE, label="Chat"),
                ft.NavigationBarDestination(icon=ft.Icons.DIRECTIONS_CAR, label="Trip"),
                ft.NavigationBarDestination(icon=ft.Icons.NOTIFICATIONS_OUTLINED,label="Notification"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, label="Account"),
            ],
            selected_index=0,
            height=65,
            on_change=self.on_nav_change
        )


        # 1. Header
        self.header = ft.Container(
            padding=ft.Padding(20, 40, 20, 10),
            content=ft.Row([
                ft.Icon(icon=ft.Icons.ACCOUNT_CIRCLE, size=45, color=COLORS["primary"]),
                ft.Column([
                    ft.Text("Welcome to PiCar!", size=14, color=COLORS["muted"]),
                    ft.Text(display_name, size=20, weight=ft.FontWeight.BOLD, color=COLORS["primary"]),
                ], spacing=0)
            ])
        )

        # 2. Booking Card
        self.booking_card = ft.Container(
            margin=ft.Margin.only(top=5, left=20, right=20, bottom=10),
            bgcolor="#FFFFFF",
            border_radius=20,
            shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.with_opacity(0.1, "black")),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        spacing=0,
                        controls=[
                            self.create_mode_tab("Xe tự lái", "self-driving", ft.Icons.PERSON_OUTLINED, active=True),
                            self.create_mode_tab("Xe có tài xế", "with-driver", ft.Icons.DIRECTIONS_CAR_OUTLINED,
                                                 active=False),
                        ]
                    ),
                    ft.Container(
                        padding=20,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Container(
                                    content=self.create_info_row(ft.Icons.LOCATION_ON_OUTLINED, "Địa điểm",
                                                                 self.location_text),
                                    on_click=self.handle_location_click,
                                    ink = True,
                                ),
                                # --- SỬA LỖI TẠI ĐÂY ---
                                ft.Row([
                                    ft.Container(
                                        expand=True,
                                        content=self.create_clickable_time_column(ft.Icons.LOGIN_ROUNDED, "Ngày nhận",
                                                                                  self.txt_start_val),
                                        on_click=self.open_start_picker  # Đổi sang hàm helper
                                    ),
                                    ft.Container(
                                        expand=True,
                                        content=self.create_clickable_time_column(ft.Icons.LOGOUT_ROUNDED, "Ngày trả",
                                                                                  self.txt_end_val),
on_click=self.open_end_picker  # Đổi sang hàm helper
                                    ),
                                ], spacing=10),  # Đã đóng ngoặc vuông cho ft.Row

                                ft.Container(height=5),
                                ft.FilledButton(
                                    content=ft.Text("Search", size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    width=float("inf"), height=45,
                                    style=ft.ButtonStyle(bgcolor=COLORS["primary"],
                                                         shape=ft.RoundedRectangleBorder(radius=12)),
                                    on_click=lambda _: self.page.go("/Search")
                                )
                            ]
                        )
                    )
                ]
            )
        )

        # 3. Category Section (Đã fix theo kiểu Tab viền đen)
        # Lưu ý: Truyền tên Category trực tiếp vào hàm mới
        self.category_section = ft.Container(
            padding=ft.Padding(20, 0, 20, 5),
            content=ft.Row(
                scroll=ft.ScrollMode.ADAPTIVE,
                spacing=10,
                controls=[
                    self.create_vehicle_button("Car"),
                    self.create_vehicle_button("Motorbike"),
                    self.create_vehicle_button("Bike"),
                    self.create_vehicle_button("Boat"),
                    self.create_vehicle_button("Truck"),
                ]
            )
        )

        # --- LAYOUT WRAPPER (Fix vùng cuộn sản phẩm) ---
        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=380,
                        bgcolor=COLORS["bg"],
                        content=ft.Column(
                            spacing=0,
                            controls=[
                                # PHẦN CỐ ĐỊNH (Sticky Top)
                                self.header,
                                self.booking_card,
                                ft.Container(
                                    padding=ft.Padding.only(left=25, bottom=10),
                                    content=ft.Text("Danh mục xe", weight=ft.FontWeight.BOLD, size=16,color = COLORS["primary"]),
                                ),
                                self.category_section,

                                # PHẦN CUỘN SẢN PHẨM (Scrollable Area)
                                ft.Container(
                                    padding=ft.Padding.only(left=20, right=20, top=1, bottom=20),
                                    expand=True,  # Lấy phần diện tích còn lại
                                    content=ft.Column(
                                    controls=[self.product_display],
                                        scroll=ft.ScrollMode.AUTO,  # Chỉ cuộn trong vùng này
                                    )
                                ),

                                # PHẦN CỐ ĐỊNH (Bottom Nav)
                                self.navigation_bar_custom
                            ]
                        )
                    )
                ]
            )
        ]

        # Load dữ liệu mặc định
        self.update_product_list("Car")

    # --- HELPER METHODS ---

    def create_clickable_time_column(self, icon, label, text_obj):
        return ft.Column([
            ft.Row([ft.Icon(icon, size=16, color=COLORS["muted"]), ft.Text(label, color=COLORS["muted"], size=11)],
                    spacing=5),
            text_obj,
            ft.Divider(height=1, color="#EEEEEE")
        ], spacing=2)

    def on_start_date_change(self, e):
        if self.start_date_picker.value:
            d = self.start_date_picker.value
            self.start_date = self.start_date.replace(year=d.year, month=d.month, day=d.day)
            self.start_time_picker.open = True  # Tự động chọn giờ sau khi chọn ngày
            self.page.update()

    def on_start_time_change(self, e):
        if self.start_time_picker.value:
            t = self.start_time_picker.value
            self.start_date = self.start_date.replace(hour=t.hour, minute=t.minute)

            # Kiểm tra nếu ngày trả bị nhỏ hơn ngày nhận mới
            if self.end_date <= self.start_date:
                self.end_date = self.start_date + timedelta(hours=2)  # Mặc định thuê ít nhất 2h
                self.page.session.store.set("end_date", self.end_date.isoformat())
                self.txt_end_val.value = self.end_date.strftime("%H:%M - %d/%m/%Y")

            self.page.session.store.set("start_date", self.start_date.isoformat())
            self.txt_start_val.value = self.start_date.strftime("%H:%M - %d/%m/%Y")
            self.page.update()

    def on_end_date_change(self, e):
        if self.end_date_picker.value:
            d = self.end_date_picker.value
            self.end_date = self.end_date.replace(year=d.year, month=d.month, day=d.day)
            self.end_time_picker.open = True
            self.page.update()

    def on_end_time_change(self, e):
        if self.end_time_picker.value:
            t = self.end_time_picker.value
            temp_end = self.end_date.replace(hour=t.hour, minute=t.minute)

            if temp_end <= self.start_date:
                self.page.snack_bar = ft.SnackBar(ft.Text("Thời gian trả phải sau thời gian nhận!"))
                self.page.snack_bar.open = True
            else:
                self.end_date = temp_end
                self.page.session.store.set("end_date", self.end_date.isoformat())
                self.txt_end_val.value = self.end_date.strftime("%H:%M - %d/%m/%Y")

                self.page.update()


            self.page.update()



    def create_mode_tab(self, text, mode, icon, active):
        is_left = (mode == "self-driving")
        icon_ctrl = ft.Icon(icon, size=18, color="#FFFFFF" if active else COLORS["primary"])
        text_ctrl = ft.Text(text, size=13, weight=ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL,
                            color="#FFFFFF" if active else COLORS["primary"])

        tab = ft.Container(
            content=ft.Row([icon_ctrl, text_ctrl], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=COLORS["primary"] if active else "#F5F5F5",
            expand=True, height=40,
            border_radius=ft.BorderRadius.only(top_left=20 if is_left else 0, top_right=0 if is_left else 20),
            on_click=lambda _: self.toggle_mode(mode)
        )
        if is_left:
            self.tab_self_container, self.tab_self_items = tab, [icon_ctrl, text_ctrl]
        else:
            self.tab_driver_container, self.tab_driver_items = tab, [icon_ctrl, text_ctrl]
        return tab

    def toggle_mode(self, mode):
        self.rental_mode = mode
        # Logic update màu sắc Tab (giữ nguyên của bạn)
        for t, items, active in [(self.tab_self_container, self.tab_self_items, mode == "self-driving"),
                                 (self.tab_driver_container, self.tab_driver_items, mode == "with-driver")]:
            t.bgcolor = COLORS["primary"] if active else "#F5F5F5"
            items[0].color = items[1].color = "#FFFFFF" if active else COLORS["primary"]
        self.page.update()

    def create_info_row(self, icon, label, content_control):
        # Nếu content_control là chuỗi, ta mới tạo ft.Text mới
        # Nếu nó đã là một ft.Text (như self.location_text), ta dùng luôn nó
        display_item = content_control if isinstance(content_control, ft.Control) else ft.Text(
            content_control, size=14, weight=ft.FontWeight.BOLD, color="#333333"
        )

        return ft.Column([
            ft.Row([
                ft.Icon(icon, size=18, color=COLORS["muted"]),
                ft.Text(label, color=COLORS["muted"], size=12)
            ], spacing=5),
            display_item,  # Đưa đối tượng thật vào đây
            ft.Divider(height=1, color="#EEEEEE")
        ], spacing=3)

    def create_vehicle_button(self, name):
        is_selected = (name == self.selected_category)
        name_txt = ft.Text(
            name,
            size=14,
            weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.W_400,
            color="black",
            no_wrap=True, # Đảm bảo chữ không bị xuống dòng làm hỏng layout
        )

        btn = ft.Container(
            content=name_txt,
            padding=ft.Padding.symmetric(vertical=8, horizontal=12),
            border=ft.Border.all(1, "black" if is_selected else "#E0E0E0"),
            border_radius=12, # Bo góc mềm mại hơn một chút
bgcolor="white",
            animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            on_click=lambda _: self.select_category(name)
        )
        self.category_buttons[name] = (btn, name_txt)
        return btn

    def select_category(self, name):
        self.selected_category = name  # Cập nhật trạng thái hiện tại
        for cat_name, (container, text_obj) in self.category_buttons.items():
            active = (cat_name == name)
            # Cập nhật style cho Container
            container.border = ft.Border.all(2, "black" if active else "#E0E0E0")
            # Cập nhật style cho Text
            text_obj.weight = ft.FontWeight.W_600 if active else ft.FontWeight.W_400

        self.update_product_list(name)
        self.page.update()

    def update_product_list(self, category_name):
        products = {
            "Car": [
                ("VinFast VF8", "1.2tr/ngày"),
                ("Toyota Vios", "800k/ngày"),
                ("Hyundai Accent", "750k/ngày"),
                ("Mazda 3", "900k/ngày"),
                ("Honda Civic", "1tr/ngày"),
                ("Kia Cerato", "850k/ngày"),
            ],
            "Motorbike": [("Honda SH", "350k/ngày"), ("Air Blade", "150k/ngày")],
            "Bike": [("Xe đạp địa hình", "50k/ngày")],
        }

        self.product_display.controls.clear()
        # Tăng spacing giữa các Card sản phẩm
        self.product_display.spacing = 8

        items = products.get(category_name, [("Sắp có xe mới...", "")])

        for title, price in items:
            self.product_display.controls.append(
                ft.Container(
                    padding=15,
                    bgcolor="#FFFFFF",
                    border_radius=16,
                    # Thêm margin nhẹ để bóng đổ (shadow) không bị cắt mất bởi Container cha
                    margin=ft.Margin.only(bottom=2),
                    shadow=ft.BoxShadow(
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.05, "black"),
                        offset=ft.Offset(0, 4)  # Đổ bóng xuống dưới tạo độ sâu
                    ),
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.DIRECTIONS_CAR_ROUNDED, color=COLORS["primary"], size=28),
                            bgcolor="#F8F9FA",
                            padding=6,
                            border_radius=8
                        ),
                        ft.Column([
                            ft.Text(title, weight=ft.FontWeight.BOLD, size=15, color="#1A1A1A"),
                            ft.Text(price, color=COLORS["muted"], size=13),
                        ], expand=True, spacing=4),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD_IOS,
icon_size=14,
                            icon_color="#CCCCCC"
                        )
                    ])
                )
            )

    def open_start_picker(self, e):
        print("Đang mở lịch...")
        self.start_date_picker.open = True
        self.page.update()

    def open_end_picker(self, e):
        print("Đang mở lịch...")
        self.end_date_picker.open = True
        self.page.update()

    async def handle_location_click(self, e):  # Thêm async ở đây
        print(">>> Đang kích hoạt lấy vị trí...")
        self.location_text.value = "Đang xin quyền GPS..."
        self.page.update()

        try:
            # BẮT BUỘC: Phải có await để đợi phần cứng trả về tọa độ thực
            pos = await self.geolocator.get_current_position()

            if pos:
                self.page.session.store.set("loc_lat", pos.latitude)
                self.page.session.store.set("loc_lng", pos.longitude)

                print(f">>> Đã lưu tọa độ vào Session: {pos.latitude}, {pos.longitude}")

                result = ApiService.locate_api(True, pos.latitude, pos.longitude)

                if result and result.get("status") == "success":
                    addr = result.get("display_name")
                    self.location_text.value = addr
                    self.page.session.store.set("location_name",addr)
                    self.location_text.color = "#333333"
                else:
                    self.location_text.value = "Server từ chối xử lý"
            else:
                self.location_text.value = "Không thể lấy tọa độ"

        except Exception as ex:
            print(f">>> Lỗi thực thi: {ex}")
            self.location_text.value = "Lỗi truy cập vị trí"

        self.page.update()
    def on_nav_change(self, e):
        index = e.control.selected_index

        if index == 0:
            self.page.go("/Dashboard")
        elif index == 1:
            self.page.go("/Chat")
        elif index == 2:
            self.page.go("/Trip")
        elif index == 3:
            self.page.go("/Notification")
        elif index == 4:
            self.page.go("/Account")



# --- Chạy main ---
async def main(page: ft.Page):

    page.views.append(DashboardScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)
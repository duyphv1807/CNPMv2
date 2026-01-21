import flet as ft
# Giả sử COLORS đã có sẵn, nếu lỗi hãy thay COLORS["bg"] bằng "#F5F5F5"
try:
    from Frontend.Style import COLORS
except:
    COLORS = {"bg": "#F5F5F5", "border": "#B3E5E5", "text": "#000000"}

class DashboardScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Dashboard",
            bgcolor=COLORS["bg"],
            padding=0, # View chính để padding 0 để Nav Bar sát cạnh
        )
        user_info = page.session.store.get("user_data")

        # Kiểm tra nếu có dữ liệu thì lấy FullName, không thì để Guest
        display_name = user_info["FullName"] if user_info else "Guest"
        self.user_id = user_info["UserID"] if user_info else None

        self.rental_mode = "self-driving"
        self.selected_category = "Car"
        self.category_buttons = {}

        # --- NAVIGATION BAR ---
        self.navigation_bar_custom = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.CHAT_BUBBLE_OUTLINE, label="Chat"),
                ft.NavigationBarDestination(icon=ft.Icons.DIRECTIONS_CAR, label="Trip"),
                ft.NavigationBarDestination(icon=ft.Icons.SUPPORT_AGENT, label="Support"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, label="Account"),
            ],
            selected_index=0,
            on_change=self.on_nav_change,
            height=65
        )

        # --- UI COMPONENTS ---
        self.header = ft.Container(
            padding=ft.Padding(20, 40, 20, 10),
            content=ft.Row([
                ft.Icon(icon=ft.Icons.ACCOUNT_CIRCLE, size=45),
                ft.Text(f"Welcome to PiCar! {display_name}", size=22, weight=ft.FontWeight.BOLD, color=COLORS["primary"]),
            ])
        )

        self.mode_toggle = ft.Container(
            padding=ft.Padding(20, 0, 20, 0),
            content=ft.Row([
                self.create_mode_btn("🚗 self-driving", "self-driving", active=True),
                self.create_mode_btn("🚖 with driver", "with-driver", active=False),
            ], spacing=10)
        )

        # Main Column chứa mọi thứ
        self.main_content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.header,
                self.mode_toggle,
                # Info Boxes
                ft.Container(
                    padding=ft.Padding(20, 15, 20, 0),
                    content=ft.Column([
                        self.create_info_box(ft.Icons.LOCATION_ON, "location", "TP.Ho Chi Minh, Viet Nam"),
                        self.create_info_box(ft.Icons.CALENDAR_MONTH, "rental period", "12:00, 01/01 - 20:00, 02/01"),
                    ], spacing=10,horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
                ),
                # Categories (5 nút chung 1 hàng bọc trong wrap)
                ft.Container(
                    padding=ft.Padding(10, 20, 10, 20),
                    content=ft.Row(
                        wrap=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        run_spacing=15,
                        controls=[
                            self.create_vehicle_button("🚲", "Bike"),
                            self.create_vehicle_button("🏍️", "Motorbike"),
                            self.create_vehicle_button("⛵", "Boat"),
                            self.create_vehicle_button("🚗", "Car"),
                            self.create_vehicle_button("🚚", "Truck"),
                        ]
                    )
                ),
                ft.Container(height=100)
            ]
        )

        # --- LAYOUT WRAPPER (Sửa lỗi out screen) ---
        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,  # Căn giữa khối 380px vào màn hình PC
                controls=[
                    ft.Container(
                        width=380,  # Khóa chiều ngang
                        bgcolor=COLORS["bg"],
                        content=ft.Column(
                            spacing=0,
                            controls=[
                                ft.Container(content=self.main_content, expand=True),  # Phần nội dung cuộn
                                self.navigation_bar_custom  # Thanh điều hướng nằm dưới cùng khối 380px
                            ]
                        )
                    )
                ]
            )
        ]

    # --- HELPER METHODS ---
    def create_mode_btn(self, text, mode, active):
        btn = ft.Container(
            content=ft.Text(text, size=12, weight=ft.FontWeight.BOLD),
            bgcolor="#B3E5E5" if active else "#E0F7F7",
            expand=1,
            height=45,
            border_radius=8,
            alignment=ft.Alignment.CENTER,
            on_click=lambda _: self.toggle_mode(mode)
        )
        if mode == "self-driving": self.btn_self = btn
        else: self.btn_driver = btn
        return btn

    def toggle_mode(self, mode):
        self.rental_mode = mode
        self.btn_self.bgcolor = "#B3E5E5" if mode == "self-driving" else "#E0F7F7"
        self.btn_driver.bgcolor = "#B3E5E5" if mode == "with-driver" else "#E0F7F7"
        self.page.update()

    def create_info_box(self, icon_data, title, subtitle):
        return ft.Container(
            padding=15,
            bgcolor="#E0F7F7",
            border=ft.Border.all(1, "#B3E5E5"),
            border_radius=10,
            content=ft.Row([
                ft.Icon(icon=icon_data, color="black", size=30),
                ft.Column([
                    ft.Text(title, size=12, color="#666666"),
                    ft.Text(subtitle, size=14, weight=ft.FontWeight.BOLD, color="black"),
                ], spacing=2)
            ])
        )

    def create_vehicle_button(self, emoji, name):
        is_selected = (name == self.selected_category)
        btn = ft.Container(
            content=ft.Column([
                ft.Text(emoji, size=25),
                ft.Text(name, size=10.5, weight=ft.FontWeight.BOLD),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER,),
            width=60,
            height=70,
            bgcolor="#4DB6AC" if is_selected else "#B3E5E5",
            border_radius=12,
            animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            on_click=lambda _: self.select_category(name)
        )
        self.category_buttons[name] = btn
        return btn

    def select_category(self, name):
        for k, v in self.category_buttons.items():
            v.bgcolor = "#B3E5E5"
        self.selected_category = name
        self.category_buttons[name].bgcolor = "#4DB6AC"
        self.page.update()

    def on_nav_change(self, e):
        # Bạn sẽ viết logic chuyển route ở đây
        pass

# --- MAIN RUNNER (Fix lỗi không hiển thị) ---
def main(page: ft.Page):
    page.views.append(DashboardScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)
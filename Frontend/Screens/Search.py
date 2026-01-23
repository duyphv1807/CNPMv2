import flet as ft
from Frontend.Style import COLORS
class SearchScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Search",
            padding=0,
            bgcolor="#F5F7FA",
        )

        # --- 1. SEARCH BAR TOP ---
        self.search_bar = ft.Container(
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_size=16),
                ft.Column([
                    ft.Text("TP. Hồ Chí Minh", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("21:00 T6, 23/01 • 20:00 T7, 24/01", size=11, color=COLORS["primary"]),
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
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
            self.filter_chip("Loại xe", ft.Icons.DIRECTIONS_CAR_OUTLINED),
            self.filter_chip("Hãng xe", ft.Icons.LANGUAGE),
            self.filter_chip("Thuê giờ", ft.Icons.ACCESS_TIME),
            self.filter_chip("Giá", ft.Icons.ATTACH_MONEY),
        ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10)

        self.filter_section = ft.Container(content=filters, padding=ft.Padding(20, 15, 20, 10))

        # --- 3. VEHICLE LIST ---
        self.vehicle_list = ft.ListView(
            controls=[
                self.vehicle_card("MITSUBISHI XPANDER 2021", "957", "https://picsum.photos/id/1071/400/220",
                                 ["Số tự động", "7 chỗ", "Xăng"], "4.6"),
                self.vehicle_card("VINFAST VF8 2023", "1.200", "https://picsum.photos/id/183/400/220",
                                 ["Số điện", "5 chỗ", "Điện"], "5.0"),
            ],
            expand=True,
            padding=ft.Padding(20, 0, 20, 100), # Padding bottom lớn để không bị map_btn che
            spacing=15
        )

        # --- FLOATING MAP BUTTON ---
        self.floating_action_button = ft.FloatingActionButton(
            content=ft.Row([ft.Icon(ft.Icons.LANGUAGE, size=18), ft.Text("Bản đồ", size=13, weight=ft.FontWeight.BOLD)], 
                           alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            bgcolor="white", width=120, height=45,
            shape=ft.RoundedRectangleBorder(radius=30),
        )
        self.floating_action_button_location = ft.FloatingActionButtonLocation.CENTER_FLOAT

        # --- MAIN LAYOUT (MOBILE BORDER 380) ---
        # Bọc tất cả vào Container width 380 để giả lập màn hình Mobile
        self.controls = [
            ft.Container(
                width=380,
                height=800, # Chiều cao giả lập mobile
                bgcolor="#F5F7FA",
                alignment=ft.Alignment.TOP_CENTER,
                content=ft.Column([
                    self.search_bar,
                    self.filter_section,
                    self.vehicle_list,
                ], spacing=0, expand=True),
                # Căn giữa container 380 này trên màn hình PC
                margin=ft.margin.symmetric(horizontal=(page.width - 380) / 2 if page.width > 380 else 0)
            )
        ]

    def filter_chip(self, label, icon):
        return ft.Container(
            content=ft.Row([ft.Icon(icon, size=16), ft.Text(label, size=12)], spacing=5),
            padding=ft.Padding(12, 8, 12, 8),
            border=ft.Border.all(1, "#E0E0E0"),
            border_radius=20,
            bgcolor="white",
        )

    def vehicle_card(self, name, price, image_url, specs, rating):
        return ft.Container(
            content=ft.Column([
                ft.Stack([
                    ft.Image(src=image_url, border_radius=ft.BorderRadius(15, 15, 0, 0),
                             width=380, height=200, fit="cover"),
                    ft.Container(content=ft.Icon(ft.Icons.FAVORITE_BORDER, color="white", size=20), top=10, right=10),
                    ft.Container(
                        content=ft.Text("Giảm 13%", color="white", size=10, weight=ft.FontWeight.BOLD),
                        bgcolor="#FF5A5F", padding=ft.Padding(8, 4, 8, 4), border_radius=5,
                        bottom=10, right=10
                    )
                ]),
                ft.Container(
                    padding=15,
                    content=ft.Column([
                        ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            ft.Icon(ft.Icons.SETTINGS, size=12, color="grey"), ft.Text(specs[0], size=10, color="grey"),
                            ft.Icon(ft.Icons.PERSON, size=12, color="grey"), ft.Text(specs[1], size=10, color="grey"),
                        ], spacing=10),
                        ft.Divider(height=15, color="#EEEEEE"),
                        ft.Row([
                            ft.Row([ft.Icon(ft.Icons.STAR, size=14, color="orange"), ft.Text(rating, size=12, weight=ft.FontWeight.BOLD)], spacing=4),
                            ft.Column([
                                ft.Text(f"{price}K", size=16, weight=ft.FontWeight.BOLD, color="#2ECC71"),
                                ft.Text("/ngày", size=9, color="grey"),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ], spacing=5)
                )
            ]),
            bgcolor="white",
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.with_opacity(0.05, "black"))
        )

async def main(page: ft.Page):

    page.views.append(SearchScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)
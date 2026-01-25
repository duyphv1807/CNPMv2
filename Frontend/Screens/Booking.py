import flet as ft
from datetime import datetime
from Frontend.Style import COLORS

class BookingScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Booking",
            padding=0,
            bgcolor="#FFFFFF",
        )

        # --- LẤY DỮ LIỆU TỪ SESSION (Dashboard đã lưu) ---
        s_date_raw = page.session.store.get("start_date")
        e_date_raw = page.session.store.get("end_date")
        vehicle_data = page.session.store.get("selected_vehicle_data")

        if vehicle_data is None:
            vehicle_data = {
                "Brand": "VinFast", "Model": "VF8", "Category": "Car",
                "FuelType": "Điện", "Transmission": "Số tự động",
                "SeatingCapacity": 5, "RentalPrice": 1251000,
                "Image": "https://picsum.photos/id/183/400/250"
            }

        image_url = vehicle_data.get("Image", "link_anh_mac_dinh.jpg")
        vehicle_name = f"{vehicle_data.get('Brand')} {vehicle_data.get('Model')}"
        location_vehicle = page.session.store.get("location_name") or "TP. Hồ Chí Minh"

        # Logic xử lý hiển thị ngày giờ
        if s_date_raw and e_date_raw:
            dt_start = datetime.fromisoformat(s_date_raw)
            dt_end = datetime.fromisoformat(e_date_raw)
            start_display = dt_start.strftime("%H:%M - %d/%m/%Y")
            end_display = dt_end.strftime("%H:%M - %d/%m/%Y")
        else:
            start_display = "Chưa chọn"
            end_display = "Chưa chọn"

        category = vehicle_data.get("Category", "Car")
        fuel = vehicle_data.get("FuelType") or vehicle_data.get("EngineType") or "N/A"
        transmission = vehicle_data.get("TransmissionType") or vehicle_data.get("Transmission") or "N/A"
        seats = vehicle_data.get("SeatingCapacity") or vehicle_data.get("PassengerCapacity") or 0
        price_val = vehicle_data.get("RentalPrice", 0)

        specs_row = []
        if category == "Bike":
            specs_row = [
                self.spec_item(ft.Icons.PEDAL_BIKE, "Xe đạp"),
                self.spec_item(ft.Icons.LEADERBOARD, vehicle_data.get("Type", "Địa hình")),
                self.spec_item(ft.Icons.SQUARE_FOOT, f"{vehicle_data.get('FrameSize', 'M')} size")
            ]
        elif category == "Truck":
            load = vehicle_data.get("LoadCapacity", 0)
            specs_row = [
                self.spec_item(ft.Icons.LOCAL_SHIPPING, f"{load} tấn"),
                self.spec_item(ft.Icons.SETTINGS, transmission),
                self.spec_item(ft.Icons.LOCAL_GAS_STATION, fuel)
            ]
        else:  # Car, Motorbike, Boat
            main_icon = ft.Icons.ELECTRIC_CAR if "Điện" in fuel else ft.Icons.LOCAL_GAS_STATION
            specs_row = [
                self.spec_item(main_icon, fuel),
                self.spec_item(ft.Icons.SETTINGS if "Tự động" in transmission else ft.Icons.HANDYMAN, transmission),
                self.spec_item(ft.Icons.CHAIR, f"{seats} ghế")
            ]

        self.temp = ft.Text("Quy định khác:\n"
                            "- Sử dụng xe đúng mục đích.\n"
                            "- Không sử dụng xe vào mục đích phi pháp, trái pháp luật.\n"
                            "- Không sử dụng xe thuê để cầm đồ, thế chấp.\n"
                            "- Không hút thuốc, nhả kẹo cao su, xả rác trong xe.\n"
                            "- Không chở hàng quốc cấm, dễ cháy nổ.\n"
                            "- Không chở hoa quả, thực phẩm nặng mùi trong xe.\n"
                            "- Khi trả xe, nếu xe bẩn hoạc có mùi trong xe, khách hàng vui lòng vễ sinh xe hoặc gửi phụ thu phí vệ sinh xe.\n"
                            "Trân trọng cảm ơn, chúc quý khách hàng có những chuyến đi tuyệt vời!"
                            ,color="black", italic=True, size= 14)

        # --- FIXED TOP NAVIGATION ---
        self.nav_top = ft.Container(
            padding=ft.Padding(10, 40, 10, 10),
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, on_click=lambda _: page.go("/Search"), icon_size=18, icon_color = COLORS["primary"]),
                ft.Text("CHI TIẾT THUÊ XE", color = COLORS["primary"], size=18, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.IconButton(ft.Icons.SHARE_OUTLINED, icon_size=20, icon_color = COLORS["primary"],),
            ])
        )

        # --- SCROLLABLE CONTENT ---
        self.content_column = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            controls=[
                # 1. Ảnh phương tiện (Slider giả lập)
                ft.Stack([
                    ft.Image(src=image_url, width=380, height=250, fit="cover"),
                    ft.Container(
                        content=ft.Row([
                            ft.IconButton(ft.Icons.CHEVRON_LEFT, icon_color="white"),
                            ft.IconButton(ft.Icons.CHEVRON_RIGHT, icon_color="white"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        width=380, top=100
                    ),
                    ft.Container(
                        content=ft.Text("1/5", color="white", size=12),
                        bgcolor="black54", padding=5, border_radius=10, bottom=10, right=10
                    )
                ]),

                # 2. Tên xe & Số sao (Nằm cùng hàng)
                ft.Container(
                    padding=20,
                    content=ft.Row([
                        ft.Text(vehicle_name, size=20, weight=ft.FontWeight.BOLD, color = COLORS["primary"], expand=True),
                        ft.Row([
                            ft.Icon(ft.Icons.STAR, color="orange", size=18),
                            ft.Text("5.0", weight=ft.FontWeight.BOLD, size=16, color = COLORS["primary"])
                        ], spacing=5)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),

                # 3. Frame Thời gian thuê (Dữ liệu từ Session)
                self.section_header("Thời gian thuê xe"),
                ft.Container(
                    padding=ft.Padding(20, 0, 20, 5),
                    content=ft.Container(
                        padding=15, border=ft.Border.all(1, color = "black"), border_radius=12,
                        content=ft.Row([
                            ft.Column([ft.Text("Nhận xe", size=11, color=COLORS["primary"]),
                                       ft.Text(start_display, size=13, weight=ft.FontWeight.BOLD, color=COLORS["primary"])], expand=True),
                            ft.VerticalDivider(width=1),
                            ft.Column([ft.Text("Trả xe", size=11, color=COLORS["primary"]),
                                       ft.Text(end_display, size=13, weight=ft.FontWeight.BOLD, color=COLORS["primary"])], expand=True),
                        ])
                    )
                ),

                # 4. Địa điểm giao nhận
                self.section_header("Địa điểm giao nhận xe"),
                ft.Container(
                    padding=ft.Padding(20, 0, 20, 5),
                    content=ft.Column([
                        # Tùy chọn 1: Tự lấy xe (Đang chọn)
                        ft.Container(
                            padding=15, border=ft.Border.all(1, "black"), border_radius=12, bgcolor="#F0FFF0",
                            content=ft.Row([
                                ft.Icon(ft.Icons.RADIO_BUTTON_CHECKED, color="black"),
                                ft.Column([ft.Text("Tôi tự đến lấy xe", weight=ft.FontWeight.BOLD, color=COLORS["primary"]),
                                           ft.Text(location_vehicle, size=12, color="black")])
                            ])
                        ),
                        # Tùy chọn 2: Giao tận nơi (Chưa hỗ trợ - Disable)
                        ft.Container(
                            padding=15, border=ft.Border.all(1, "#EEEEEE"), border_radius=12,
                            content=ft.Row([
                                ft.Icon(ft.Icons.RADIO_BUTTON_OFF, color="grey"),
                                ft.Column([
                                    ft.Text("Giao xe tận nơi", color="grey", weight=ft.FontWeight.BOLD),
                                    ft.Text("Hệ thống chưa hỗ trợ tính năng này", size=11, color="red")
                                ])
                            ]),
                            on_click=lambda _: None  # Không cho click
                        ),
                        # Google Map ảnh
                        self.section_header("Map"),
                        ft.Image(
                            src="https://media.wired.com/photos/59269c967034dc5f91beba7f/master/w_2560%2Cc_limit/GoogleMap-660x440.jpg",
                            height=150, border_radius=12, fit="cover")
                    ], spacing=10)
                ),

                # 5. Đặc điểm (Theo loại xe)
                self.section_header("Đặc điểm"),
                ft.Container(
                    padding=ft.Padding(20, 0, 20, 15),
                    content=ft.Row(specs_row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),

                # 6. Mô tả (Chủ xe viết)
                self.section_header("Mô tả"),
                ft.Container(padding=ft.Padding(20, 0, 20, 10),
                             content=ft.Text("Xe mới, sạc đầy pin. Chủ xe nhiệt tình hỗ trợ 24/7.", size=13,color = "black")),

                # 8. Giấy tờ thuê
                self.section_header("Giấy tờ thuê xe"),
                ft.Container(
                    padding=ft.Padding(20, 0, 20, 10),
                    content=ft.Column([
                        self.doc_item(ft.Icons.BADGE, "GPLX (đối chiếu) & CCCD (đối chiếu Vneid)"),
                        self.doc_item(ft.Icons.CONTACT_EMERGENCY, "GPLX (đối chiếu) & Passport (giữ lại)"),
                    ], spacing=10)
                ),

                # 9. Các mục trống (Điều khoản, Phụ phí, Hợp đồng, Chính sách hủy)
                self.section_header("Điều khoản"),
                ft.Container(padding=ft.Padding(20, 0, 20, 10),
                             content=self.temp),

                self.section_header("Phụ phí phát sinh"),
                ft.Container(
                    padding=ft.Padding(20, 0, 20, 15),
                    content=ft.Column([
                        self.fee_item(
                            "Phí vượt giới hạn",
                            "3.000đ /km",
                            "Phụ phí phát sinh nếu di chuyển vượt quá 300 km khi thuê xe 1 ngày"
                        ),
                        self.fee_item(
                            "Phí quá giờ",
                            "100.000đ /giờ",
                            "Phụ phí phát sinh nếu hoàn trả xe trễ giờ. Trường hợp trễ quá 5 giờ phụ phí thêm 1 ngày thuê"
                        ),
                        self.fee_item(
                            "Phụ vệ sinh",
                            "100.000đ",
                            "Phụ phí phát sinh khi xe hoàn trả không đảm bảo vệ sinh(nhiều vết bẩn, bùn cát, sình lầy...)"
                        ),
                        self.fee_item(
                            "Phí Khử mùi",
                            "300.000đ,",
                            "Phụ phí phát sinh khi xe hoàn trả bị ám mùi khó chịu(mùi thuốc lá, thực phẩm nặng mùi)"
                        ),
                    ], spacing=15)
                ),

                self.section_header("Hợp đồng"),
                ft.Container(padding=ft.Padding(20, 0, 20, 10),
                             content=ft.Text("(Sẽ được tạo tự động khi đặt xe)", color="grey", italic=True)),

                self.section_header("Chính sách hủy chuyến"),
                ft.Container(padding=ft.Padding(20, 0, 20, 10),
                             content=ft.TextButton(ft.Text("Xem thêm >", color="black"), on_click=lambda _: page.go("/CancellationPolicy"))),

                ft.Container(height=120)
            ]
        )

        # --- FIXED BOTTOM PAYMENT BAR ---
        self.bottom_bar = ft.Container(
            padding=ft.Padding(20, 10, 20, 25), bgcolor="white",
            border=ft.Border.only(top=ft.border.BorderSide(1, "#EEEEEE")),
            content=ft.Row([
                ft.Column([
                    ft.Text("Giá thuê dự kiến", size=12, color="grey"),
                    ft.Text("1.251.000 đ", size=20, weight=ft.FontWeight.BOLD, color="green"),
                ], expand=True, spacing=0),
                ft.FilledButton(
                    content=ft.Text("THUÊ NGAY", color="white", weight=ft.FontWeight.BOLD),
                    style=ft.ButtonStyle(bgcolor="green", shape=ft.RoundedRectangleBorder(radius=10)),
                    height=50, width=160
                )
            ])
        )

        # Main Layout
        self.controls = [
            ft.Container(
                expand=True,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.VerticalAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=380,
                            height=800,
                            bgcolor="white",
                            border_radius=20,
                            shadow=ft.BoxShadow(blur_radius=20, color="black12"),
                            content=ft.Stack([
                                # Content chính
                                ft.Column([
                                    self.nav_top,
                                    self.content_column
                                ], spacing=0, expand=True),
                                # Thanh Bar dính đáy
                                ft.Container(
                                    content=self.bottom_bar,
                                    bottom=0,
                                    width=380
                                )
                            ])
                        )
                    ]
                )
            )
        ]

    # --- HELPERS ---
    def section_header(self, title):
        return ft.Container(padding=ft.Padding(20, 20, 20, 10), content=ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color = "black"))

    def spec_item(self, icon, val):
        return ft.Column([ft.Icon(icon, color="green", size=24),
                          ft.Text(val, size=12, weight=ft.FontWeight.BOLD, color = "black")],
                         horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def amenity_tag(self, icon, label):
        return ft.Row([ft.Icon(icon, size=18, color="black45"), ft.Text(label, size=12)], spacing=10, expand=True)

    def doc_item(self, icon, text):
        return ft.Row([ft.Icon(icon, size=18, color="green"), ft.Text(text, size=13, color = "black")], spacing=10)

    def fee_item(self, title, price, desc):
        return ft.Column([
            ft.Row([
                ft.Text(title, size=14, weight=ft.FontWeight.W_500, color="black"),
                ft.Text(price, size=14, weight=ft.FontWeight.BOLD, color="green")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(desc, size=12, color="black",italic = True),
        ], spacing=2)

async def main(page: ft.Page):
    page.views.append(BookingScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)

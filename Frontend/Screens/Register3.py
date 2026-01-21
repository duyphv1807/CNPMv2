import flet as ft
import re
from Frontend.Style import COLORS
from Frontend import Screens
from Backend.Model.User import User

class RegisterScreen3(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Register3",
            bgcolor=COLORS["bg"],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE
        )

        # Các trường nhập liệu
        self.pw_field = ft.TextField(
            label="New password",
            password=True,
            text_style=ft.TextStyle(weight=ft.FontWeight.W_300, size=16, color=COLORS["text"]),
            # Tăng độ đậm của nhãn (Label)
            label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=COLORS["muted"]),
            can_reveal_password=True,
            border_radius=10,
            border_color=COLORS["border"],
            width=340,
            height=55,
            text_size=14,
            cursor_color=COLORS["primary"],
            content_padding=15,
        )

        self.re_pw_field = ft.TextField(
            label="Re-enter the new password",
            text_style=ft.TextStyle(weight=ft.FontWeight.W_300, size=16, color=COLORS["text"]),
            # Tăng độ đậm của nhãn (Label)
            label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=COLORS["muted"]),
            password=True,
            border_radius=10,
            can_reveal_password=True,
            border_color=COLORS["border"],
            width=340,
            height=55,
            text_size=14,
            cursor_color=COLORS["primary"],
            content_padding=15,
        )

        # Thông tin hướng dẫn mật khẩu
        self.tip_text = ft.Text(
            "• Dài từ 6-20 ký tự\n• Có ít nhất 1 chữ số\n• Có ít nhất 1 chữ cái viết hoa",
            size=12,
            color="#666666",
        )

        # Giao diện chính
        # Giao diện chính
        self.controls = [
            ft.Container(
                width=350,
                # Dùng margin tự động để Container 350px này luôn nằm giữa màn hình
                margin=ft.Margin(left=0, top=0, right=0, bottom=0),
                content=ft.Column(
                    # Quan trọng: Ép tất cả con của Column này ra giữa theo chiều ngang
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        # Nút Back - Đặt trong Row để không ảnh hưởng đến căn giữa của Column chính
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK_IOS_NEW,
                                    icon_size=18,
                                    icon_color=COLORS["text"],
                                    on_click=lambda _: self.page.go("/Register2")  # Chỉnh lại route về trang 2
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),

                        ft.Container(height=40),

                        # Nhóm Logo & Icon - Đảm bảo nhóm này cũng căn giữa
                        ft.Column(
                            controls=[
                                ft.Text(
                                    value="PiCar",
                                    size=32,  # Hoặc FONTS["title"]
                                    weight=ft.FontWeight.BOLD,
                                    color=COLORS["text"]
                                ),
                                # Dùng icon đúng như ảnh mẫu (person_pin)
                                ft.Icon(ft.Icons.PERSON_PIN_ROUNDED, size=70, color=COLORS["text"]),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                        ),

                        ft.Container(height=30),

                        # Các ô nhập mật khẩu
                        self.pw_field,
                        ft.Container(height=10),
                        self.re_pw_field,

                        # Tip mật khẩu
                        ft.Container(
                            content=self.tip_text,
                            width=340,
                            padding=ft.Padding(left=5, top=5, right=0, bottom=0)
                        ),

                        ft.Container(height=40),

                        # Nút Complete - Dùng ElevatedButton để giống style trong ảnh hơn
                        ft.FilledButton(
                            content="Complete",
                            width=340,
                            height=50,
                            bgcolor="black",
                            color="white",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=self.handle_complete
                        ),
                    ]
                )
            )
        ]

    def validate_password(self, password):
        if not (6 <= len(password) <= 20):
            return False, "Mật khẩu phải từ 6 đến 20 ký tự!"
        if not re.search(r"\d", password):
            return False, "Mật khẩu phải có ít nhất 1 chữ số!"
        if not re.search(r"[A-Z]", password):
            return False, "Mật khẩu phải có ít nhất 1 chữ cái viết hoa!"
        return True, ""

    async def handle_complete(self, e):
        pw = self.pw_field.value
        re_pw = self.re_pw_field.value

        # 1. Kiểm tra logic mật khẩu
        if pw != re_pw:
            self.show_snack("Mật khẩu xác nhận không khớp!")
            return

        is_valid, msg = self.validate_password(pw)
        if not is_valid:
            self.show_snack(msg)
            return

        # 2. Lấy dữ liệu tổng hợp từ Screens (Thông tin b1 + OCR b2)
        current_data = self.page.session.store.get("temp_data2")

        if not current_data:
            self.show_snack("Lỗi: Không tìm thấy dữ liệu đăng ký!")
            return

        current_data["password"] = pw

        # 3. Hiển thị Loading Overlay
        loading_dlg = ft.AlertDialog(
            content=ft.Row([ft.ProgressRing(), ft.Text(" Đang tải dữ liệu lên hệ thống...")]),
            modal=True
        )
        self.page.overlay.append(loading_dlg)
        loading_dlg.open = True
        self.page.update()

        # 4. Gọi hàm Register từ Backend
        try:
            # Lưu ý: registration_payload hiện đã có số GPLX 044463044045 từ Screens
            success, result_msg = User.register_user(current_data)

            loading_dlg.open = False
            self.page.update()

            if success:
                self.show_snack("Tài khoản đã khởi tạo thành công! Đang quay lại Đăng nhập...")
                self.page.go("/Login")
            else:
                friendly_msg = "SĐT hoặc GPLX này đã tồn tại!" if "exists" in result_msg else result_msg
                self.show_snack(friendly_msg)

        except Exception as ex:
            loading_dlg.open = False
            self.page.update()
            self.show_snack(f"Lỗi kết nối: {str(ex)}")

    def show_snack(self, message):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()


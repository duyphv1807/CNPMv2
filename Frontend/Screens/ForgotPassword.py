import flet as ft
from Frontend.Style import COLORS, FONTS, PRIMARY_BUTTON_STYLE
import time
import random

class ForgotPasswordScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/ForgotPassword",
            bgcolor=COLORS["bg"],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE
        )

        # --- INPUT FIELD ---
        self.contact_input = ft.TextField(
            label="Email or Phone number",
            label_style=ft.TextStyle(color=COLORS["muted"], weight=ft.FontWeight.BOLD),
            border_color=COLORS["border"],
            focused_border_color=COLORS["primary"],
            cursor_color=COLORS["primary"],
            text_style=ft.TextStyle(color=COLORS["text"]),
            height=40,
        )
        self.button_send_otp = ft.FilledButton(
            content=ft.Text("Gửi mã OTP", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            style=PRIMARY_BUTTON_STYLE,
            width=float("inf"),
            height=40,
            on_click=self.send_otp
        )
        # --- GIAO DIỆN ---
        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=380,
                        bgcolor=COLORS["bg"],
                        padding=20,
                        content=ft.Column(
                            controls=[
                                ft.SafeArea(
                                    content=ft.Column(
                                        controls=[
                                            ft.Container(
                                                content=ft.IconButton(
                                                    icon=ft.Icons.ARROW_BACK_IOS_NEW,
                                                    icon_size=18,
                                                    icon_color=COLORS["text"],
                                                    on_click=lambda _: self.page.go("/Login")
                                                ),
                                                alignment=ft.Alignment(-1, -1),  # Ép về góc trái trên cùng
                                                margin=ft.Margin.only(left=-10)  # Chỉnh nhẹ để sát mép hơn nếu muốn
                                            ),

                                            # 2. Dịch xuống dưới một chút (Spacer này đẩy nội dung xuống)
                                            ft.Container(height=60),

                                            # 3. Header Section (Căn giữa chữ)
                                            ft.Text(
                                                value="Quên mật khẩu",
                                                size=FONTS["title"],
                                                weight=ft.FontWeight.BOLD,
                                                color=COLORS["text"],
                                                text_align=ft.TextAlign.CENTER,
                                                width=340  # Giúp text_align có tác dụng
                                            ),
                                            ft.Text(
                                                value="Vui lòng nhập Email hoặc SĐT để nhận mã OTP khôi phục mật khẩu.",
                                                size=14,
                                                color=COLORS["muted"],
                                                text_align=ft.TextAlign.CENTER,
                                                width=340
                                            ),

                                            ft.Container(height=40),  # Khoảng cách đến ô nhập

                                            # 4. Input Section (Đảm bảo width Inf để giãn đều theo khung 380px)
                                            ft.Container(
                                                content=self.contact_input,
                                                width=float("inf"),
                                            ),

                                            ft.Container(height=10),  # Khoảng cách nhỏ giữa 2 ô

                                            # 5. Submit Button (Đảm bảo width Inf để bằng với ô Input)
                                            self.button_send_otp,
                                        ],
                                        spacing=10,
                                        # Căn giữa các con theo chiều ngang của Column
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    )
                                )
                            ],
                        )
                    )
                ]
            )
        ]

    def show_error(self, messages):
        # Sử dụng lại logic Alert hoặc hiển thị error_text trực tiếp
        self.contact_input.error_text = messages[0]
        self.contact_input.update()

    async def send_otp(self, e):
        account = str(self.contact_input.value).strip()

        if not account:
            self.show_snack("Vui lòng nhập Email hoặc Số điện thoại!")
            return

        # 1. Hiển thị loading (Sửa lỗi gán sai biến)
        self.button_send_otp.disabled = True
        self.button_send_otp.content = ft.ProgressRing(width=20, height=20, color="white")
        self.update()

        try:
            print("Đang gọi Backend...")
            from Backend.Services.AuthService import AuthService

            # 2. Tạo mã OTP và thời gian hết hạn (Dùng timestamp cho đồng bộ)
            otp_code = str(random.randint(100000, 999999))
            # Hết hạn sau 5 phút (300 giây)
            expire_at = time.time() + 300

            # 3. Gửi OTP (Giữ nguyên logic Backend của bạn)
            success, message = await AuthService.request_otp_reset_password(account, otp_code)
            print(f"Backend trả về: {success}, {message}")
            if success:
                # 4. Lưu vào session (Đổi key cho khớp với logic VerifyOTP đã sửa)
                otp_data = {
                    "code": otp_code,
                    "expiry": expire_at,
                    "contact": account
                }
                self.page.session.store.set("otp_auth_data", otp_data)
                self.page.session.store.set("reset_contact", account)

                self.show_snack(f"Mã OTP đã được gửi tới {account}")

                # 5. CHUYỂN TRANG NGAY (Bỏ await countdown vì nó gây treo trang)
                self.page.go("/VerifyOTP")
            else:
                self.show_snack(message)
                # Reset lại nút nếu gửi thất bại
                self.button_send_otp.disabled = False
                self.button_send_otp.content = ft.Text("Gửi mã OTP", weight=ft.FontWeight.BOLD, color="#FFFFFF")
                self.update()

        except Exception as ex:
            print(f"Lỗi: {ex}")
            self.show_snack("Lỗi kết nối dịch vụ!")
            self.button_send_otp.disabled = False
            self.button_send_otp.content = ft.Text("Gửi mã OTP", weight=ft.FontWeight.BOLD, color="#FFFFFF")
            self.update()

    def show_snack(self, message):
        def show_snack(self, message):
            # Tạo mới SnackBar mỗi khi gọi để tránh xung đột trạng thái
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(message, color="#FFFFFF"),
                bgcolor=COLORS.get("primary", ft.Colors.BLUE_GREY_800),  # Màu nền
                action="Đã hiểu",
                duration=3000,  # Hiển thị trong 3 giây
            )
            self.page.snack_bar.open = True
            self.page.update()  # Bắt buộc dùng page.update() ở đây


async def main(page: ft.Page):

    page.views.append(ForgotPasswordScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)
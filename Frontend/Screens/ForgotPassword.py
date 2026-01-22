import flet as ft
from Frontend.Style import COLORS, FONTS, PRIMARY_BUTTON_STYLE
from Frontend.Services.APIService import ApiService
import asyncio

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
            label="Email ",
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
                                                value="Vui lòng nhập Email để nhận mã OTP khôi phục mật khẩu.",
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
            self.show_snack("Vui lòng nhập Email Đã Đăng kí!")
            return

        # 1. Hiển thị loading (Sửa lỗi gán sai biến)
        self.button_send_otp.disabled = True
        self.button_send_otp.content = ft.ProgressRing(width=20, height=20, color="white")
        self.update()

        try:
            # 2. GỌI BACKEND: Không tự tạo mã OTP tại đây nữa
            # Gửi email sang Backend, Backend sẽ tự tạo OTP, lưu DB và gửi mail cho khách
            result = await asyncio.to_thread(lambda: ApiService.send_otp_api(account))

            if result.get("status") == "success":
                # 3. Lưu email vào session để trang /VerifyOTP biết cần xác thực cho ai
                self.page.session.store.set("reset_email", account)

                self.show_snack(f"Mã OTP đã được gửi tới {account}")
                # Chuyển trang ngay lập tức
                self.page.go("/VerifyOTP")
            else:
                # Hiện lỗi nếu email không tồn tại hoặc lỗi hệ thống
                self.show_snack(result.get("message", "Gửi mã thất bại"))
                self.reset_button_state()

        except Exception as ex:
            print(f"Lỗi kết nối: {ex}")
            self.show_snack("Lỗi kết nối dịch vụ! Vui lòng kiểm tra Wi-Fi/IP.")
            self.reset_button_state()

    def reset_button_state(self):
        self.button_send_otp.disabled = False
        self.button_send_otp.content = ft.Text("Gửi mã OTP", weight=ft.FontWeight.BOLD, color="#FFFFFF")
        self.page.update()

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
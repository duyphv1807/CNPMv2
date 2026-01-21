import flet as ft
from Frontend.Style import COLORS, PRIMARY_BUTTON_STYLE
import asyncio
import datetime
import random
import time

class VerifyOTPScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/VerifyOTP",
            bgcolor=COLORS["bg"],
            padding=20,
        )
        self.countdown_active = False

        self.pin_fields = [self._create_pin_field(i) for i in range(6)]

        self.contact_info_text = ft.Text(
            value="Đang tải thông tin...",  # Giá trị tạm thời
            text_align=ft.TextAlign.CENTER,
            color=COLORS["muted"]
        )

        self.countdown_text = ft.Text(
            value="Gửi lại mã sau 10 giây",
            color=COLORS["muted"],
            size=14
        )

        self.btn_next = ft.FilledButton(
            content=ft.Text("Verify", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            style=PRIMARY_BUTTON_STYLE,
            width=300,  # <-- Thay đổi con số này để nút ngắn lại (ví dụ 150 hoặc 200)
            height=50,
            on_click=self.handle_verify
        )

        # 2. Xây dựng giao diện
        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=380,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.SafeArea(
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Container(height=120),
                                            ft.Text("Xác thực OTP", size=24, weight=ft.FontWeight.BOLD,
                                                    color=COLORS["text"]),
                                            self.contact_info_text,
                                            ft.Container(height=50),

                                            # --- PIN FIELDS ---
                                            ft.Row(
                                                controls=self.pin_fields,
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                spacing=10
                                            ),

                                            ft.Container(height=30),
                                            # Gom countdown và resend vào một hàng cho chuyên nghiệp
                                            ft.Row(
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                controls=[
                                                    self.countdown_text,
                                                    ft.TextButton(
                                                        content=ft.Text("Resend", weight=ft.FontWeight.W_300,
                                                                        color=COLORS["primary"], size=14),
                                                        on_click=self.resend_otp  # Đặt on_click ở đây mới đúng
                                                    ),
                                                ]
                                            ),
                                            ft.Container(height=20),
                                            self.btn_next,
                                        ]
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        ]

    # Hàm này được gọi tự động khi View đã được hiển thị trên Page
    def did_mount(self):
        self.update_info_from_session()
        # Chạy countdown trong một task riêng để không chặn main thread
        self.page.run_task(self.start_countdown)

    def update_info_from_session(self):
        """Lấy dữ liệu an toàn sau khi View đã mount"""
        try:
            # Sửa lại cách truy cập session store của bạn
            auth_data = self.page.session.store.get("otp_auth_data")
            if auth_data:
                contact = auth_data.get("contact", "***")
                self.contact_info_text.value = f"Mã đã được gửi tới {contact}\nOTP có hiệu lực trong 5 phút."
            else:
                self.contact_info_text.value = "Không tìm thấy dữ liệu phiên làm việc."
            self.update()
        except Exception as e:
            print(f"Lỗi cập nhật UI: {e}")

    def _create_pin_field(self, index):
        tf = ft.TextField(
            width=50,
            height=60,
            text_align=ft.TextAlign.CENTER,
            border_radius=10,
            value=" ",
            border_color=COLORS["border"],
            focused_border_color=COLORS["primary"],
            text_style=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD),
            keyboard_type=ft.KeyboardType.NUMBER,
            content_padding=0,
            data=index,
            cursor_color=COLORS["primary"],
            on_change=self._on_pin_change,
            enable_interactive_selection=False,
        )
        tf.counter_text = ""  # Ẩn counter
        return tf

    async def _on_pin_change(self, e):
        index = e.control.data
        val = e.control.value

        # --- CHẾ ĐỘ XÓA (Backspace) ---
        if val == "":
            if index > 0:
                # Nghỉ một chút để người dùng thấy ô đã trống
                await asyncio.sleep(0.05)
                await self.pin_fields[index - 1].focus()
            self.update()
            return

        # --- CHẾ ĐỘ NHẬP SỐ ---
        # Nếu nhập đè hoặc gõ nhanh dẫn đến > 1 ký tự
        if len(val) > 0:
            # 1. Chỉ lấy ký tự cuối cùng người dùng vừa gõ
            last_char = val[-1]

            # 2. Kiểm tra nếu là số thì mới xử lý
            if last_char.isdigit():
                e.control.value = last_char
                self.update()  # Cập nhật ngay để xóa ký tự thừa (nếu có)

                # 3. Delay một nhịp rất ngắn để hệ thống ổn định trước khi nhảy
                await asyncio.sleep(0.05)

                # 4. Nhảy tới ô tiếp theo
                if index < 5:
                    await self.pin_fields[index + 1].focus()
                else:
                    self.page.update()
            else:
                # Nếu nhập ký tự không phải số, xóa sạch ô đó
                e.control.value = ""

    async def start_countdown(self):
        self.countdown_active = True
        # Khi đang đếm: Chữ xám, mờ
        self.countdown_text.color = COLORS["muted"]
        self.countdown_text.opacity = 0.6

        for i in range(10, -1, -1):
            if not self.countdown_active: break
            if i > 0:
                self.countdown_text.value = f"Gửi lại mã sau {i} giây"
            else:
                # Khi hết giờ: Chữ đậm, màu Primary, rõ nét
                self.countdown_text.value = "Bạn có thể gửi lại mã ngay bây giờ"
                self.countdown_text.color = COLORS["primary"]
                self.countdown_text.opacity = 1.0
                self.countdown_text.weight = ft.FontWeight.BOLD

            self.update()
            await asyncio.sleep(1)

    async def handle_verify(self, e):
        entered_otp = "".join([f.value.strip() for f in self.pin_fields])
        auth_data = self.page.session.store.get("otp_auth_data")

        if not auth_data:
            self.show_snack("Dữ liệu không hợp lệ!")
            return

        # KIỂM TRA THỜI GIAN HẾT HẠN
        if time.time() > auth_data.get("expiry", 0):
            self.show_snack("Mã OTP đã hết hạn. Vui lòng gửi lại mã!")
            return

        # KIỂM TRA MÃ OTP
        if entered_otp == auth_data["code"]:
            self.page.go("/ResetPassword")
        else:
            self.show_snack("Mã OTP không chính xác!")

    async def resend_otp(self, e):
        if self.countdown_text.color == COLORS["muted"]:
            # Lấy số giây còn lại từ text để thông báo (tùy chọn)
            self.show_snack("Vui lòng đợi cho đến khi thời gian đếm ngược kết thúc!")
            return

        auth_data = self.page.session.store.get("otp_auth_data")
        if not auth_data:
            self.show_snack("Lỗi: Không tìm thấy thông tin phiên làm việc!")
            return

        contact = auth_data.get("contact")

        # 2. Tạo mã OTP mới (Giống hệt logic bên ForgotPassword)
        new_otp = str(random.randint(100000, 999999))
        new_expiry = datetime.datetime.now() + datetime.timedelta(minutes=6)
        from Backend.Services.AuthService import AuthService

        # 3. Cập nhật lại session với mã mới
        auth_data["code"] = new_otp
        auth_data["expiry"] = new_expiry
        self.page.session.store.set("otp_auth_data", auth_data)

        print(f"Mã OTP mới cho {contact} là: {new_otp}")  # Debug
        await AuthService.request_otp_reset_password(contact, new_otp)

        # 3. Reset giao diện các ô PIN
        for field in self.pin_fields:
            field.value = " "  # Trả về dấu cách mặc định như logic đã thống nhất
            field.update()

        for field in self.pin_fields:
            field.value = " "  # Giữ dấu cách giả để lùi được
            field.update()

        self.countdown_active = False  # Dừng vòng lặp cũ
        await asyncio.sleep(0.1)
        self.page.run_task(self.start_countdown)  # Chạy countdown mới

        await self.pin_fields[0].focus()
        self.show_snack(f"Mã mới đã được gửi tới {contact}!")
        self.update()

    def show_snack(self, message):
        self.page.snack_bar = ft.SnackBar(ft.Text(message))
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    # Mock data
    page.session.store.set("otp_auth_data", {"code": "123456", "contact": "037xxxxxxx"})

    # Xử lý dọn dẹp khi đóng app để tránh lỗi session
    def on_disconnect(e):
        print("Session kết thúc")

    page.on_disconnect = on_disconnect
    page.views.append(VerifyOTPScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)
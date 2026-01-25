import flet as ft
from Frontend.Style import COLORS, PRIMARY_BUTTON_STYLE
import asyncio
from Frontend.Services.APIService import ApiService

class VerifyOTPScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/VerifyOTP",
            bgcolor=COLORS["bg"],
            padding=20,
        )
        self.countdown_active = False

        self.pin_fields = []
        for _ in range(6):
            field = ft.TextField(
                value="",
                text_align=ft.TextAlign.CENTER,
                width=45,
                height=55,
                # TĂNG ĐỘ ĐẬM TẠI ĐÂY:
                text_style=ft.TextStyle(
                    size=20,
                    weight=ft.FontWeight.BOLD,  # Ép kiểu đậm cho chữ số nhập vào
                    color=ft.Colors.BLACK
                ),
                # TĂNG ĐỘ ĐẬM CHO VIỀN (Border) ĐỂ NHÌN RÕ HƠN
                border_width=6,
                focused_border_color=ft.Colors.BLUE_ACCENT,
                # ... các thuộc tính khác
            )
            self.pin_fields.append(field)

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

        if len(entered_otp) < 6:
            self.show_snack("Vui lòng nhập đầy đủ 6 chữ số!")
            return

        email = self.page.session.store.get("reset_email")

        if not email:
            self.show_snack("Phiên làm việc hết hạn, vui lòng thử lại!")
            self.page.go("/ForgotPassword")
            return

        # Hiển thị loading nhẹ (tùy chọn)
        self.update()

        try:
            # 3. GỌI API XÁC THỰC: Để Backend đối soát với Database
            # Không còn so sánh với auth_data["code"] ở đây nữa để tránh bị hack
            result = ApiService.verify_otp_api(email, entered_otp)

            if result.get("status") == "success":
                # 4. Xác thực thành công -> Chuyển sang trang đặt mật khẩu mới
                # Bạn nên lưu một "token" hoặc cờ xác nhận vào session để trang ResetPassword biết là đã verify xong
                self.page.session.store.set("otp_verified", True)

                self.show_snack("Xác thực thành công!")
                self.page.go("/ResetPassword")
            else:
                # 5. Thông báo lỗi từ Backend (Mã sai, hết hạn, hoặc đã dùng rồi)
                self.show_snack(result.get("message", "Mã xác thực không đúng!"))

        except Exception as ex:
            print(f"Lỗi Verify: {ex}")
            self.show_snack("Lỗi kết nối máy chủ!")

    async def resend_otp(self, e):
        if self.countdown_text.color == COLORS["muted"]:
            # Lấy số giây còn lại từ text để thông báo (tùy chọn)
            self.show_snack("Vui lòng đợi cho đến khi thời gian đếm ngược kết thúc!")
            return

        contact = self.page.session.store.get("reset_email")
        if not contact:
            self.show_snack("Lỗi: Phiên làm việc đã hết hạn. Vui lòng thử lại từ đầu!")
            self.page.go("/ForgotPassword")
            return

        self.show_snack(f"Đang gửi lại mã tới {contact}...")

        try:
            # 3. GỌI API: Tương tự như lúc gửi lần đầu
            # Backend sẽ tự tạo mã mới và cập nhật vào bảng OTP
            result = ApiService.send_otp_api(contact)

            if result.get("status") == "success":
                # 4. Reset giao diện các ô PIN
                for field in self.pin_fields:
                    field.value = ""  # Hoặc " " tùy theo logic xóa của bạn
                    field.disabled = False

                # 5. Khởi động lại đếm ngược
                self.countdown_active = True
                self.page.run_task(self.start_countdown)

                # Focus lại ô đầu tiên
                await self.pin_fields[0].focus()

                self.show_snack(f"Mã mới đã được gửi tới {contact}!")
                self.page.update()
            else:
                self.show_snack(result.get("message", "Gửi lại mã thất bại"))

        except Exception as ex:
            print(f"Lỗi Resend OTP: {ex}")
            self.show_snack("Lỗi kết nối dịch vụ!")

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
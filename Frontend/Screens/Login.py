import flet as ft
from Frontend.Style import COLORS, FONTS, PRIMARY_BUTTON_STYLE
from Frontend.Services.APIService import ApiService

class LoginScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Login",
            bgcolor=COLORS["bg"],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # --- INPUT FIELDS ---
        self.account_imput = ft.TextField(
            label="Email or phone number",
            text_style=ft.TextStyle(weight=ft.FontWeight.W_300, size=16, color=COLORS["text"]),
            # Tăng độ đậm của nhãn (Label)
            label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=COLORS["muted"]),
            border_color=COLORS["border"],
            focused_border_color=COLORS["primary"],
            height=55,  # Giảm nhẹ height để cân đối hơn
            cursor_color=COLORS["primary"],
            content_padding=15,  # Thêm padding trong ô nhập
        )

        self.password_input = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border_color=COLORS["border"],
            text_style=ft.TextStyle(weight=ft.FontWeight.W_300, size=16, color=COLORS["text"]),
            # Tăng độ đậm của nhãn (Label)
            label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=COLORS["muted"]),
            focused_border_color=COLORS["primary"],
            height=55,
            cursor_color=COLORS["primary"],
            content_padding=15,
        )

        # --- CẢI THIỆN: BỌC NỘI DUNG VÀO CONTAINER CỐ ĐỊNH SIZE ---
        # Điều này đảm bảo dù cửa sổ to hay nhỏ, Form Login vẫn trông như trên điện thoại
        self.controls = [
            ft.Container(
                content=ft.Column(
                    tight=True,  # Ép các phần tử sát lại nhau theo spacing
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        # Logo Section
                        ft.Column(
                            controls=[
                                ft.Text(value="PiCar", size=FONTS["title"], weight=ft.FontWeight.BOLD,
                                        color=COLORS["text"]),
                                ft.Icon(ft.Icons.PERSON_PIN_ROUNDED, size=70, color=COLORS["text"]),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,
                        ),

                        ft.Container(height=10),  # Spacer nhỏ

                        self.account_imput,
                        self.password_input,

                        # Checkbox & Forgot Password
                        ft.Row(
                            controls=[
                                ft.Checkbox(label="Remember me", fill_color=COLORS["primary"], scale=0.9),
                                ft.TextButton(
                                    content=ft.Text(value="Forgot password?", size=13, color=COLORS["text"]),
                                    on_click=self.handle_forgot_password
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),

                        ft.Container(height=5),

                        # Login Button
                        ft.FilledButton(
                            content=ft.Text(value="Log in", weight=ft.FontWeight.BOLD, color="#FFFFFF", size=16),
                            width=float("inf"),
                            height=50,
                            style=PRIMARY_BUTTON_STYLE,
                            on_click=self.handle_login
                        ),

                        ft.Container(height=10),

                        # Footer Section
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(value="If you don't have an account yet, please", size=13, color=COLORS["muted"]),
                                        ft.TextButton(
                                            content=ft.Text(value="Register.", weight=ft.FontWeight.BOLD,
                                                            color=COLORS["primary"], size=13),
                                            on_click=self.handle_register
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=0,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ],
                ),
                # FIX then chốt: Giới hạn chiều ngang tối đa để không bị lệch
                width=350,
                padding=10,
            )
        ]

    def show_error_box(self, error_messages):
        # Tạo nội dung hiển thị: Đổi color sang WHITE để dễ đọc
        content_list = ft.Column(
            [ft.Text(f"• {msg}", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_400) for msg in error_messages],
            tight=True,
            spacing=8
        )

        self.error_dialog = ft.AlertDialog(
            modal=True,
            # Title nên để màu sáng hoặc đỏ nhạt
            title=ft.Row([
                ft.Icon(ft.Icons.REPORT_PROBLEM_ROUNDED, color=ft.Colors.RED_400),
                ft.Text("Lỗi nhập liệu", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ], spacing=10),
            content=content_list,
            actions=[
                ft.TextButton("Đã hiểu", on_click=self._close_error)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(self.error_dialog)
        self.error_dialog.open = True
        self.page.update()

    def _close_error(self):
        if hasattr(self, "error_dialog"):
            self.error_dialog.open = False
            self.page.update()

    async def handle_login(self, e):
        account_val = self.account_imput.value.strip()
        password_val = self.password_input.value.strip()

        self.account_imput.error_text = None
        self.password_input.error_text = None

        errors = []

        # Check mail
        if not account_val:
            errors.append("Vui lòng nhập tài khoản")
        if not password_val:
            errors.append("Vui lòng nhập mật khẩu")
        if errors:
            self.show_error_box(errors)
            return

        try:
            # 3. GỌI API QUA SERVICE (Đây là bước quan trọng nhất)
            # Hàm này sẽ gửi request sang Flask và đợi phản hồi
            result = ApiService.login_api(account_val, password_val)

            # 4. XỬ LÝ KẾT QUẢ TỪ BACKEND TRẢ VỀ
            if result.get("status") == "success":
                user_data = result.get("user_data")

                # Lưu thông tin người dùng vào Session để các màn hình khác dùng chung
                # (Không cần mật khẩu, chỉ cần FullName, Role, ID...)
                self.page.session.store.set("user_data", user_data)

                print(f"Đăng nhập thành công! Chào mừng {user_data.get('FullName')}")

                # Chuyển hướng sang màn hình chính
                self.page.go("/Dashboard")
            else:
                # Nếu thất bại (Sai pass, không tồn tại...), hiển thị lỗi từ Backend gửi về
                error_message = result.get("message", "Đăng nhập thất bại")
                self.show_error_box([error_message])

        except Exception as ex:
            # Xử lý khi có lỗi kết nối mạng hoặc lỗi code
            print(f"Lỗi khi gọi API: {ex}")
            self.show_error_box(["Không thể kết nối tới máy chủ. Vui lòng kiểm tra lại mạng!"])

    async def handle_register(self, e):
        if self.page:
            await self.page.push_route("/Register")
            self.page.update()

    async def handle_forgot_password(self, e):
        if self.page:
            await self.page.push_route("/ForgotPassword")
            self.page.update()

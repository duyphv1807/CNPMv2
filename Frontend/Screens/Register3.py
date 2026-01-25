import flet as ft
import re
from Frontend.Style import COLORS
from Frontend.Services.APIService import ApiService
import asyncio
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
        errors = []

        # 1. Kiểm tra logic mật khẩu
        if pw != re_pw:
            errors.append("Mật khẩu xác nhận không khớp!")

        is_valid, msg = self.validate_password(pw)
        if not is_valid:
            errors.append(msg)

        if errors:
            self.show_error_box(errors)  # Hiển thị danh sách lỗi bằng AlertDialog
            return

        # 2. Lấy dữ liệu tổng hợp từ Screens (Thông tin b1 + OCR b2)
        current_data = self.page.session.store.get("temp_data2")

        if not current_data:
            self.show_error_box(["Lỗi: Không tìm thấy dữ liệu đăng ký trong phiên làm việc!"])
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
            # Gửi toàn bộ current_data sang Flask Server
            result = await asyncio.to_thread(lambda: ApiService.register_api(current_data))

            loading_dlg.open = False
            self.page.update()

            # 5. Xử lý phản hồi từ Server
            if result.get("status") == "success":
                self.show_error_box([result.get("Thành công", "Chúc mừng bạn đăng kí thành công!")])
                self.page.session.store.clear()
                self.page.update()
                self.page.go("/Login")
            else:
                # Server trả về lỗi gì thì hiện lỗi đó (SĐT tồn tại, lỗi DB...)
                error_msg = result.get("message", "Đăng ký thất bại")
                self.show_error_box([result.get("message", "Lỗi không xác định khi lưu!")])

        except Exception as ex:
            if loading_dlg: loading_dlg.open = False
            self.page.update()
            self.show_error_box([f"Lỗi kết nối Server: {str(ex)}"])

    def _close_error(self):
        if hasattr(self, "error_dialog"):
            self.error_dialog.open = False
            self.page.update()
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

async def main(page: ft.Page):
    page.title = "Test Register Step 3"
    page.window_width = 400
    page.window_height = 800

    # 1. GIẢ LẬP DỮ LIỆU SESSION (Dựa trên log bạn đã chạy thành công trước đó)
    # Bước này cực kỳ quan trọng, thiếu key nào là Bước 3 sẽ bị lỗi key đó
    registration_data = {
        'fullname': 'duy',
        'nation_id': '082134658429',
        'dob': '07/07/1985',
        'phone': '0679753473',
        'email': 'coigaimupp@gamil.com',
        'license_no': '044463044045',
        'license_class': 'D',
        # Lưu ý: Đường dẫn ảnh phải là đường dẫn thực tế trên máy bạn để test ko bị lỗi
        'front_img': 'C:/Users/ASUS/OneDrive/Máy tính/bài tập/test/a1.jpg',
        'back_img': 'C:/Users/ASUS/OneDrive/Máy tính/bài tập/test/back.jpg'
    }

    # Lưu vào session của page
    page.session.store.set("temp_data2", registration_data)

    # Bạn cũng có thể lưu lẻ các key nếu Register3 gọi lẻ
    for key, value in registration_data.items():
        page.session.store.set(key, value)

    print("--- Đã giả lập dữ liệu Session thành công ---")

    # 2. ĐIỀU HƯỚNG THẲNG VÀO BƯỚC 3
    def route_change(route):
        page.views.clear()
        # Khởi tạo View Bước 3
        # Đảm bảo bạn truyền đúng các tham số mà Constructor của Register3View yêu cầu
        page.views.append(
            RegisterScreen3(page)
        )
        page.update()

    page.on_route_change = route_change
    await page.push_route("/Register3")

if __name__ == "__main__":
    ft.run(main)

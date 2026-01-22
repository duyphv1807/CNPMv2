import flet as ft
from typing import Any
import re
import datetime
try:
    import dns.resolver as dns_resolver

    DNS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    DNS_AVAILABLE = False
    dns_resolver = None

from Frontend.Style import COLORS

class RegisterScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Register",
            bgcolor=COLORS["bg"],
            padding=20,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ADAPTIVE
        )
        dropdown_style = {
            "menu_height": 450,
            "text_style": ft.TextStyle(weight=ft.FontWeight.BOLD),
        }
        self.sel_day = ft.Dropdown(label="Ngày", width=120, **dropdown_style,
                                   options=[ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 32)])
        self.sel_month = ft.Dropdown(label="Tháng", width=120, **dropdown_style,
                                     options=[ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 13)])
        self.sel_year = ft.Dropdown(label="Năm", width=120, **dropdown_style,
                                    options=[ft.dropdown.Option(str(i)) for i in range(1950, 2027)])

        self.date_dialog = ft.AlertDialog(
            title=ft.Text("Chọn ngày sinh", weight=ft.FontWeight.BOLD,),
            content=ft.Row([self.sel_day, self.sel_month, self.sel_year], tight=True),
            actions=[
                ft.TextButton("Xác nhận", on_click=self._confirm_date),
                ft.TextButton("Hủy", on_click=lambda _: self._close_dialog()),
            ],
        )

        # --- INPUT FIELDS ---
        self.fullname = self._create_input("Full name")

        self.nation_id = self._create_input(
            "ID card number",
            k_type=ft.KeyboardType.NUMBER,
        )

        self.dob = self._create_input("Date of birth", read_only=True)
        self.dob.on_click = self._open_date_dialog

        self.phone = self._create_input(
            "Phone number",
            k_type=ft.KeyboardType.PHONE,
        )

        self.email = self._create_input("Email address", k_type=ft.KeyboardType.EMAIL)

        # --- GIAO DIỆN ---
        self.controls = [
            ft.Container(
                width=350,
                content=ft.Column(
                    controls=[
                        # Đưa nút Back vào Container và ép lề trái
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_IOS_NEW,
                                icon_size=18,
                                icon_color=COLORS["text"],
                                on_click=lambda _: self.page.go("/Login")
                            ),
                            alignment=ft.Alignment(-1, -1),  # Ép về góc trái trên cùng
                            margin=ft.margin.only(left=-10)  # Chỉnh nhẹ để sát mép hơn nếu muốn
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(value="PiCar", size=32, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                                ft.Text(value="Create an account", size=18, weight=ft.FontWeight.BOLD,
                                        color=COLORS["text"]),
                                ft.Text(
                                    value="Enter your details to register an account.",
                                    size=12, color=COLORS["muted"], text_align=ft.TextAlign.CENTER
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5
                        ),
                        ft.Container(height=10),
                        self.fullname,
                        self.nation_id,
                        self.dob,
                        self.phone,
                        self.email,
                        ft.Container(height=10),
                        ft.FilledButton(
                            content=ft.Text("Continue", weight=ft.FontWeight.BOLD, color="#FFFFFF"),  # Dùng thuộc tính text trực tiếp
                            width=float("inf"),
                            height=50,
                            style=ft.ButtonStyle(
                                bgcolor=COLORS["primary"],
                                color="#FFFFFF",
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=self.handle_continue
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15
                )
            )
        ]

    # Đã fix: icon=None đưa xuống cuối cùng
    def _create_input(self, label: str, icon: str = None, k_type: Any = ft.KeyboardType.TEXT,
                      read_only=False):
        return ft.TextField(
            label=label,
            prefix_icon=icon,
            keyboard_type=k_type,
            read_only=read_only,
            # Tăng độ đậm nét chữ nhập vào
            text_style=ft.TextStyle(weight=ft.FontWeight.W_300, size=16, color=COLORS["text"]),
            # Tăng độ đậm của nhãn (Label)
            label_style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=COLORS["muted"]),
            border_color=COLORS["border"],
            focused_border_color=COLORS["primary"],
            border_width=1.5,
            content_padding=15,
            cursor_color=COLORS["primary"],
            selection_color=ft.Colors.BLUE_100,
        )

    def _open_date_dialog(self, e):
        # Đảm bảo dialog đã nằm trong overlay của trang
        if self.date_dialog not in self.page.overlay:
            self.page.overlay.append(self.date_dialog)

        self.date_dialog.open = True
        self.page.update()

    def _close_dialog(self):
        self.date_dialog.open = False
        self.page.update()

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

    def _confirm_date(self, e):
        if self.sel_day.value and self.sel_month.value and self.sel_year.value:
            date_str = f"{self.sel_day.value}/{self.sel_month.value}/{self.sel_year.value}"
            try:
                datetime.datetime.strptime(date_str, "%d/%m/%Y")
                self.dob.value = date_str
                self.dob.error_text = None
                self._close_dialog()
            except ValueError:
                self.sel_day.error_text = "!"
                self.page.update()
        else:
            self._close_dialog()

    def is_email_domain_valid(self, email):
        if not DNS_AVAILABLE or dns_resolver is None:
            return True
        try:
            domain = email.split('@')[1]
            dns_resolver.resolve(domain, 'MX')
            return True
        except Exception:
            return False

    async def handle_continue(self, e):
        for field in [self.fullname, self.nation_id, self.dob, self.phone, self.email]:
            field.error_text = None

        fullname_val = str(self.fullname.value).strip()
        nation_id_val = str(self.nation_id.value).strip()
        dob_val = str(self.dob.value).strip()
        phone_val = str(self.phone.value).strip()
        email_val = str(self.email.value).strip()

        errors = []
        name_pattern = r"^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪễệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵýỷỹ\s]+$"

        if not fullname_val or not re.match(name_pattern, fullname_val):
            self.fullname.error_text = "!"  # Đánh dấu chấm than nhỏ ở ô nhập
            errors.append("Họ và tên không hợp lệ.")

        if not nation_id_val or len(nation_id_val) != 12 or not nation_id_val.isdigit() :
            self.nation_id.error_text = "!"
            errors.append("CCCD phải có đúng 12 chữ số.")

        if not dob_val:
            self.dob.error_text = "!"
            errors.append("Bạn chưa chọn ngày sinh.")

            # 4. Check SĐT (Sửa lại logic nation_id_val.isdigit thành phone_val.isdigit)
        if not phone_val or not (phone_val.startswith("0") and 10 <= len(phone_val) <= 11) or not phone_val.isdigit():
            self.phone.error_text = "!"
            errors.append("Số điện thoại không hợp lệ.")

            # 5. Check Email
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not email_val or not re.match(email_regex, email_val):
            self.email.error_text = "!"
            errors.append("Định dạng Email không đúng.")
        elif not self.is_email_domain_valid(email_val):
            self.email.error_text = "!"
            errors.append("Tên miền email này không tồn tại.")

        # KIỂM TRA: Nếu có lỗi thì show MessageBox
        if errors:
            self.show_error_box(errors)
            self.update()# Gọi hàm MessageBox
            return

        data = {
            "fullname": fullname_val,
            "nation_id": nation_id_val,
            "dob": dob_val,
            "phone": phone_val,
            "email": email_val
        }

        if self.page:
            self.page.session.store.set("temp_data1", data)
            print(f"Dữ liệu nhận được: {data}")
            self.page.go("/Register2")


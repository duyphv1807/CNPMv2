import flet as ft
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from datetime import date, datetime
from Backend.Picar.ExcuteDatabase import supabase
from Frontend.Services.APIService import ApiService
from Frontend.Style import COLORS


class AccountScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/Account", bgcolor=ft.Colors.WHITE)

        self.user = {}
        self.user_id = None
        self.dob_value = ""
        self.avatar_path = ""
        # Tạo vòng xoay chờ
        self.loader = ft.Row([ft.ProgressRing()], alignment=ft.MainAxisAlignment.CENTER, expand=True)
        self.controls = [self.loader]

    def did_mount(self):
        # Lấy data từ session đã lưu khi Login thành công
        user_data = self.page.session.store.get("user_data")

        if user_data:
            self.user_id = user_data.get("UserID")
            print(f"--- DEBUG: Đang gọi account cho UserID: {self.user_id} ---")
            self.load_account()
        else:
            print("--- DEBUG: Không tìm thấy session user_data ---")
            self.page.go("/Login")

    def load_account(self):
        try:
            result = ApiService.get_account_api(self.user_id)
            print(f"--- DEBUG: Kết quả từ API sau khi cập nhật: {result} ---")

            if result.get("status") == "success":
                self.user = result.get("data")
                self.page.session.store.set("user_data", self.user)

                # Cập nhật giá trị hiển thị cho các ô nhập nếu UI đã tồn tại
                if hasattr(self, 'fullname_input'):
                    self.fullname_input.value = self.user.get("FullName", "")
                    self.email_input.value = self.user.get("Email", "")
                    self.client_input.value = self.user.get("PhoneNumber", "")
                    self.dob_input.value = self.user.get("DateOfBirth", "")

                    # CẬP NHẬT ẢNH TẠI ĐÂY
                    default_avatar = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
                    self.avatar_view.src = self.user.get("Avatar") or default_avatar

                    self.page.update()
                else:
                    self.build_ui()
                    self.page.update()
            else:
                self.show_error_on_screen(result.get("message"))
        except Exception as e:
            print(f"Lỗi load_account: {e}")

    def show_error_on_screen(self, msg):
        self.controls = [
            ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color="red", size=50),
                ft.Text(f"Lỗi kết nối: {msg}", color="red", weight="bold"),
                ft.ElevatedButton("Thử lại", on_click=lambda _: self.load_account())
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        ]
        self.page.update()
    def build_ui(self):
        label_bold = ft.TextStyle(weight=ft.FontWeight.BOLD)

        self.fullname_input = ft.TextField(
            label="Full name",
            value=self.user.get("FullName", ""),
            label_style=label_bold,
        )

        self.email_input = ft.TextField(
            label="Email",
            value=self.user.get("Email", ""),
            label_style=label_bold,
        )
        # --- THÊM Ô SỐ ĐIỆN THOẠI Ở ĐÂY ---
        self.client_input = ft.TextField(
            label="Phone Number",
            value=self.user.get("PhoneNumber", ""),  # Lấy từ cột PhoneNumber trong DB
            label_style=label_bold,
            keyboard_type=ft.KeyboardType.PHONE,
            prefix_icon=ft.Icons.PHONE,
        )
        # Tạo nút Wallet với style đồng bộ
        self.wallet_button = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, color="white"),
                    ft.Text("My Wallet", color="white", weight=ft.FontWeight.BOLD),
                    ft.VerticalDivider(width=10),
                    ft.Text("0.00 VNĐ", color="white"),  # Sau này có thể lấy từ API
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.ORANGE_800,
            padding=15,
            border_radius=15,
            on_click=lambda _: self.page.go("/Wallet"),  # Điều hướng sang trang ví
        )

        self.dob_input = ft.TextField(
            label="Date of birth",
            value=self.dob_value,
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.open_dob_dialog,
            label_style=label_bold,
        )

        # ===== DOB DROPDOWN (GIỐNG REGISTER) =====
        dropdown_style = {
            "menu_height": 450,
            "text_style": ft.TextStyle(weight=ft.FontWeight.BOLD),
        }

        self.sel_day = ft.Dropdown(
            label="Ngày",
            width=120,
            **dropdown_style,
            options=[ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 32)]
        )

        self.sel_month = ft.Dropdown(
            label="Tháng",
            width=120,
            **dropdown_style,
            options=[ft.dropdown.Option(str(i).zfill(2)) for i in range(1, 13)]
        )

        self.sel_year = ft.Dropdown(
            label="Năm",
            width=120,
            **dropdown_style,
            options=[ft.dropdown.Option(str(i)) for i in range(1950, 2027)]
        )

        self.date_dialog = ft.AlertDialog(
            title=ft.Text("Chọn ngày sinh", weight=ft.FontWeight.BOLD),
            content=ft.Row(
                [self.sel_day, self.sel_month, self.sel_year],
                tight=True,
            ),
            actions=[
                ft.TextButton("Xác nhận", on_click=self.confirm_dob),
                ft.TextButton("Hủy", on_click=self.close_dob_dialog),
            ],
        )

        # ===== XỬ LÝ ẢNH AVATAR =====
        # Nếu self.user.get("Avatar") trống hoặc None, sẽ dùng link ảnh icon người mặc định
        default_avatar = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

        # Ưu tiên: 1. Ảnh vừa chọn (avatar_path) -> 2. Ảnh từ DB -> 3. Ảnh mặc định
        current_src = self.avatar_path if self.avatar_path else (self.user.get("Avatar") or default_avatar)

        self.avatar_view = ft.Image(
            src=current_src,
            width=90,
            height=90,
            fit=ft.BoxFit.COVER,
            # Thêm error_content để nếu link ảnh lỗi vẫn hiện icon mặc định
            error_content=ft.Icon(ft.Icons.PERSON, size=50, color=COLORS["muted"])
        )

        avatar = ft.Container(
            width=90,
            height=90,
            border_radius=45,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.border.all(2, COLORS["primary"]),
            content=self.avatar_view,
            on_click=self.pick_avatar,
        )
        # ===== HEADER =====
        header = ft.Container(
            padding=ft.Padding(20, 40, 20, 20),
            content=ft.Row(
                [
                    avatar,
                    ft.Column(
                        [
                            ft.Text("Account", size=13, color=COLORS["muted"]),
                            ft.Text(
                                self.fullname_input.value or "Guest",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLORS["primary"],
                            ),
                        ],
                        spacing=4,
                    ),
                ],
                spacing=15,
            ),
        )


        # ===== PASSWORD =====
        self.old_pw = ft.TextField(
            label="Current password",
            password=True,
            can_reveal_password=True,
            label_style=label_bold,
        )

        self.new_pw = ft.TextField(
            label="New password",
            password=True,
            can_reveal_password=True,
            label_style=label_bold,
        )

        self.password_panel = ft.Column(
            visible=False,
            spacing=12,
            controls=[
                self.old_pw,
                self.new_pw,
                ft.Divider(),
                ft.FilledButton(
                    content="Save password",
                    icon=ft.Icons.SAVE,
                    expand=True,
                    on_click=self.handle_change_password,
                ),
            ],
        )

        # ===== INFO CARD =====
        info_card = self.card(
            ft.Column(
                spacing=12,
                controls=[
                    # ===== TITLE =====
                    ft.Text(
                        "Edit profile",
                        weight=ft.FontWeight.BOLD,
                        color="black",
                        size=16,
                    ),

                    # ===== PROFILE INFO =====
                    self.fullname_input,
                    self.email_input,
                    self.client_input,  # <-- Đã thêm vào đây
                    self.dob_input,
                    self.wallet_button,
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                    ft.Divider(),

                    # ===== SAVE PROFILE =====
                    ft.FilledButton(
                        content="Save profile",
                        icon=ft.Icons.SAVE,
                        expand=True,
                        on_click=self.save_profile,
                    ),

                    ft.Divider(),

                    # ===== CHANGE PASSWORD (CHUNG CARD) =====
                    ft.Text(
                        "Change password",
                        weight=ft.FontWeight.BOLD,
                        color="black",
                        size=15,
                    ),

                    ft.FilledButton(
                        content="Edit password",
                        icon=ft.Icons.LOCK,
                        expand=True,
                        on_click=self.toggle_password_panel,
                    ),

                    self.password_panel,
                ],
            )
        )

        # ===== NAV BAR =====
        nav = ft.NavigationBar(
            selected_index=4,
            height=65,
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.CHAT, label="Chat"),
                ft.NavigationBarDestination(icon=ft.Icons.DIRECTIONS_CAR, label="Trip"),
                ft.NavigationBarDestination(icon=ft.Icons.SUPPORT_AGENT, label="Support"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON, label="Account"),
            ],
            on_change=self.on_nav_change,
        )

        # ===== LAYOUT TỐI ƯU =====
        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=380,
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Column(
                            spacing=0,
                            controls=[
                                # PHẦN NỘI DUNG (Có thể cuộn)
                                ft.Container(
                                    content=ft.Column(
                                        [header, info_card],
                                        scroll=ft.ScrollMode.AUTO,  # Bật cuộn ở đây
                                        spacing=0,
                                    ),
                                    expand=True,  # Chiếm toàn bộ diện tích còn lại
                                ),
                                # THANH ĐIỀU HƯỚNG (Cố định ở đáy)
                                nav,
                            ],
                        ),
                    )
                ],
            )
        ]
    # ===== UI HELPERS =====
    def card(self, content):
        return ft.Container(
            margin=ft.Margin.only(left=20, right=20, bottom=15),
            padding=20,
            bgcolor="white",
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=15,
                color=ft.Colors.with_opacity(0.1, "black"),
            ),
            content=content,
        )

    def open_dob_dialog(self, e):
        # add dialog vào overlay nếu chưa có
        if self.date_dialog not in self.page.overlay:
            self.page.overlay.append(self.date_dialog)

        # nếu đã có DOB thì set lại dropdown
        if self.dob_input.value:
            try:
                y, m, d = self.dob_input.value.split("-")
                self.sel_year.value = y
                self.sel_month.value = m
                self.sel_day.value = d
            except:
                pass

        self.date_dialog.open = True
        self.page.update()

    def close_dob_dialog(self, e=None):
        self.date_dialog.open = False
        self.page.update()

    def confirm_dob(self, e):
        if self.sel_day.value and self.sel_month.value and self.sel_year.value:
            date_str = f"{self.sel_year.value}-{self.sel_month.value}-{self.sel_day.value}"
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                self.dob_input.value = date_str
                self.dob_value = date_str
                self.close_dob_dialog()
            except ValueError:
                self.show_error("Ngày sinh không hợp lệ")

    def calc_age(self):
        dob = datetime.strptime(self.dob_value, "%Y-%m-%d").date()
        today = date.today()
        return today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day)
        )

    # ===== FILE PICK =====
    @staticmethod
    def open_file(title):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title=title,
            filetypes=[("Image files", "*.jpg *.jpeg *.png")],
        )
        root.destroy()
        return path

    def pick_avatar(self, _):
        path = self.open_file("Choose avatar")
        if not path:
            return
        os.makedirs("assets/avatars", exist_ok=True)
        ext = os.path.splitext(path)[1]
        new_path = f"assets/avatars/{self.user_id}{ext}"
        shutil.copy(path, new_path)
        self.avatar_view.src = new_path
        self.avatar_path = new_path
        self.page.update()

    # ===== SAVE PROFILE =====
    def save_profile(self, e):
        # Thu thập dữ liệu
        payload = {
            "user_id": self.user_id,
            "full_name": self.fullname_input.value,
            "email": self.email_input.value,
            "client": self.client_input.value,
            "dob": self.dob_input.value,
            "password": self.new_pw.value if self.new_pw.value else None
        }

        # BƯỚC QUAN TRỌNG: Hiện thông báo THÀNH CÔNG NGAY LẬP TỨC
        self.show_success_dialog()

        # Gọi API chạy ngầm bằng Threading để UI không bị khựng (lag)
        import threading
        def call_api_silent():
            ApiService.update_account_api(payload)

        threading.Thread(target=call_api_silent, daemon=True).start()

        # Reset các ô mật khẩu
        self.new_pw.value = ""
        self.old_pw.value = ""
        self.page.update()
#=====UPDATE NOT==========
    def show_success_dialog(self):
        self.success_dialog = ft.AlertDialog(
            title=ft.Text("Thành công", weight=ft.FontWeight.BOLD),
            content=ft.Text("Thông tin tài khoản đã được cập nhật!"),
            actions=[ft.TextButton("OK", on_click=self.close_success_dialog)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(self.success_dialog)
        self.success_dialog.open = True
        self.page.update()

    def close_success_dialog(self, e):
        self.success_dialog.open = False

        # 1. Cập nhật dữ liệu mới vào biến self.user để đồng bộ bộ nhớ local
        self.user["FullName"] = self.fullname_input.value
        self.user["Email"] = self.email_input.value
        self.user["PhoneNumber"] = self.client_input.value
        self.user["DateOfBirth"] = self.dob_input.value

        # 2. Lưu lại vào Session để các trang khác (như Dashboard) cũng thấy thay đổi
        self.page.session.store.set("user_data", self.user)

        # 3. Cập nhật ngay lập tức tên hiển thị ở phần Header (phía trên ảnh đại diện)
        # Trong build_ui, Header là Column nằm bên cạnh avatar.
        # Chúng ta cần tìm đến Text đó để cập nhật:
        try:
            # Truy cập vào cấu trúc Row -> Column -> Text thứ 2 (tên người dùng)
            header_name_text = self.controls[0].controls[0].content.controls[0].controls[1].controls[1]
            header_name_text.value = self.fullname_input.value
        except:
            # Nếu cấu trúc UI phức tạp, bạn có thể gọi build_ui() nhưng chỉ cập nhật UI local
            self.build_ui()

            # 4. Làm mới trang
        self.page.update()

    # 3. Thêm hàm hiển thị lỗi nhanh nếu cần
    def show_error(self, msg):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="red")
        self.page.snack_bar.open = True
        self.page.update()
    # ===== PASSWORD =====
    def toggle_password_panel(self, _):
        self.password_panel.visible = not self.password_panel.visible
        self.page.update()

    def handle_change_password(self, _):
        res = (
            supabase
            .table("User_Admin")
            .select("Password")
            .eq("UserID", self.user_id)
            .single()
            .execute()
        )

        if res.data["Password"] != self.old_pw.value:
            self.show_error("Wrong password")
            return

        supabase.table("User_Admin").update({
            "Password": self.new_pw.value
        }).eq("UserID", self.user_id).execute()

        self.show_success("Password changed")

    # ===== NAV =====
    def on_nav_change(self, e):
        routes = ["/Dashboard", "/Chat", "/Trip", "/Support", "/Account"]
        self.page.go(routes[e.control.selected_index])

    # ===== TOAST =====
    def show_error(self, msg):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()

    def show_success(self, msg):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg))
        self.page.snack_bar.open = True
        self.page.update()


def main(page: ft.Page):
    page.views.append(AccountScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)

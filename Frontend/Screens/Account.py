import flet as ft
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from datetime import date, datetime
from Backend.Helpers import update_user_profile, change_password
from Frontend.Style import COLORS

class AccountScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Account",
            bgcolor=COLORS["bg"],
            padding=0
        )
        try:
            user_data = self.page.session.store.get("user_data")
        except:
            user_data = None

        if not user_data:
            user_data = {"FullName": "Guest", "id": "0"}

        self.user_id = user_data.get("id") or user_data.get("ID")
        self.avatar_path = user_data.get("Avatar") or "assets/default_avatar.png"
        self.license_image_path = user_data.get("DrivingLicense")
        self.dob_value = user_data.get("DateOfBirth")

        # --- UI COMPONENTS ---
        self.avatar_view = ft.Image(
            src=self.avatar_path,
            width=120,
            height=120,
            fit="cover",
        )

        self.avatar_circle = ft.Container(
            width=120,
            height=120,
            border_radius=ft.BorderRadius.all(60),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.Border.all(2, ft.Colors.GREY_400),
            content=self.avatar_view,
            on_click=self.pick_avatar,
        )

        self.fullname = ft.TextField(
            label="Họ tên",
            width=350,
            value=user_data.get("FullName", ""),
            border_radius=ft.BorderRadius.all(8)
        )

        self.email = ft.TextField(
            label="Email",
            width=350,
            value=user_data.get("Email", ""),
            border_radius=ft.BorderRadius.all(8)
        )

        self.dob_text = ft.Text(
            value=self.dob_value if self.dob_value else "Chưa chọn ngày sinh",
            size=14,
        )

        self.date_picker = ft.DatePicker(
            on_change=self.on_date_selected,
        )
        page.overlay.append(self.date_picker)

        self.dob_picker = ft.Container(
            width=350,
            padding=ft.Padding(12, 12, 12, 12),
            border=ft.Border.all(1, ft.Colors.GREY_400),
            border_radius=ft.BorderRadius.all(8),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.dob_text,
                    ft.Icon(ft.Icons.CALENDAR_MONTH),
                ],
            ),
            on_click=lambda _: self.show_picker(),
        )

        self.license_text = ft.Text(
            value="Đã cập nhật ảnh GPLX" if self.license_image_path else "Chưa tải ảnh GPLX",
            size=13,
            color=ft.Colors.GREY,
        )

        # FIX: Sử dụng tham số 'text' thay vì 'content' nếu là chuỗi đơn thuần 
        # để tránh lỗi TypeError trên bản Flet cũ
        self.license_button = ft.FilledButton(
            content="Cập nhật ảnh GPLX",
            icon=ft.Icons.CAMERA_ALT,
            on_click=self.pick_license_image,
            width=350,
        )

        self.old_pw = ft.TextField(label="Mật khẩu cũ", password=True, can_reveal_password=True, width=350)
        self.new_pw = ft.TextField(label="Mật khẩu mới", password=True, can_reveal_password=True, width=350)
        self.password_panel = ft.Column(
            visible=False,
            controls=[
                self.old_pw,
                self.new_pw,
                ft.FilledButton("Xác nhận đổi mật khẩu", on_click=self.handle_change_password, width=350),
            ],
        )

        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=390,
                        padding=ft.Padding(20, 20, 20, 20),
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=15,
                            controls=[
                                ft.Text("Quản lý tài khoản", size=22, weight=ft.FontWeight.BOLD),
                                self.avatar_circle,
                                self.fullname,
                                self.dob_picker,
                                self.email,
                                ft.Divider(height=10),
                                self.license_button,
                                self.license_text,
                                ft.Divider(height=10),
                                ft.OutlinedButton("Đổi mật khẩu", icon=ft.Icons.LOCK,
                                                  on_click=self.toggle_password_panel, width=350),
                                self.password_panel,
                                ft.FilledButton("Lưu thông tin", icon=ft.Icons.SAVE, on_click=self.save_profile,
                                                width=350, bgcolor=COLORS["primary"]),
                                ft.Container(height=20)
                            ],
                        ),
                    )
                ],
            )
        ]

    def show_picker(self):
        self.date_picker.open = True
        self.page.update()

    def on_date_selected(self, e):
        if e.control.value:
            self.dob_value = e.control.value.strftime("%Y-%m-%d")
            self.dob_text.value = self.dob_value
            self.page.update()

    def pick_avatar(self, _):
        path = self.open_file("Chọn ảnh đại diện")
        if path:
            os.makedirs("assets/avatars", exist_ok=True)
            ext = os.path.splitext(path)[1]
            new_path = f"assets/avatars/{self.user_id}{ext}"
            shutil.copy(path, new_path)
            self.avatar_path = new_path
            self.avatar_view.src = new_path
            self.page.update()

    def pick_license_image(self, _):
        path = self.open_file("Chọn ảnh GPLX")
        if path:
            os.makedirs("assets/licenses", exist_ok=True)
            ext = os.path.splitext(path)[1]
            new_path = f"assets/licenses/{self.user_id}{ext}"
            shutil.copy(path, new_path)
            self.license_image_path = new_path
            self.license_text.value = "Đã cập nhật ảnh GPLX"
            self.page.update()

    @staticmethod
    def open_file(title):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(parent=root, title=title, filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        root.destroy()
        return path

    def save_profile(self, _):
        if not self.dob_value:
            self.show_snack("Vui lòng chọn ngày sinh", True)
            return

        try:
            dob = datetime.strptime(self.dob_value, "%Y-%m-%d").date()
            age = (date.today() - dob).days // 365
            if age < 18:
                self.show_snack("Bạn phải đủ 18 tuổi", True)
                return
        except Exception:
            self.show_snack("Định dạng ngày sinh không hợp lệ", True)
            return

        update_user_profile(
            self.user_id,
            {
                "FullName": self.fullname.value,
                "DateOfBirth": self.dob_value,
                "Email": self.email.value,
                "Avatar": self.avatar_path,
                "DrivingLicense": self.license_image_path,
            }
        )

        current_user = self.page.session.store.get("user_data")
        if current_user:
            current_user.update({
                "FullName": self.fullname.value,
                "Avatar": self.avatar_path,
                "DateOfBirth": self.dob_value
            })
            self.page.session.store.set("user_data", current_user)

        self.show_snack("Lưu thông tin thành công!")

    def toggle_password_panel(self, _):
        self.password_panel.visible = not self.password_panel.visible
        self.page.update()

    def handle_change_password(self, _):
        if change_password(self.user_id, self.old_pw.value, self.new_pw.value):
            self.show_snack("Đổi mật khẩu thành công!")
            self.password_panel.visible = False
        else:
            self.show_snack("Mật khẩu cũ không đúng", True)
        self.page.update()

    def show_snack(self, msg, is_error=False):
        self.page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor="red" if is_error else "green")
        self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    # Dùng .set() thay vì .store.set()
    page.session.store.set("user_data", {"FullName": "Test User", "id": "1"})
    page.views.append(AccountScreen(page))
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
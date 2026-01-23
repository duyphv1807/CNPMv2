import flet as ft
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from datetime import date, datetime
from Backend.Picar.ExcuteDatabase import get_current_user
from Backend.Picar.Services.ChangeUserInfoFunctional import change_password, update_user_profile

from Frontend.Style import COLORS


class AccountScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(route="/Account", bgcolor=COLORS["bg"], padding=0)


        # ===== USER =====
        user = get_current_user() or {}
        self.user_id = user.get("UserID")
        self.avatar_path = user.get("Avatar") or "assets/default_avatar.png"
        self.dob_value = user.get("DateOfBirth", "")

        # ===== INPUTS =====
        self.fullname_input = ft.TextField(
            label="Full name",
            value=user.get("FullName", ""),
        )

        self.email_input = ft.TextField(
            label="Email",
            value=user.get("Email", ""),
        )

        self.dob_input = ft.TextField(
            label="Date of birth",
            value=self.dob_value,
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.open_dob_dialog,
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

        # ===== AVATAR =====
        self.avatar_view = ft.Image(
            src=self.avatar_path,
            width=90,
            height=90,
            fit=ft.BoxFit.COVER,
        )

        avatar = ft.Container(
            width=90,
            height=90,
            border_radius=45,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.Border.all(2, COLORS["primary"]),
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

        # ===== INFO CARD =====
        info_card = self.card(
            ft.Column(
                spacing=12,
                controls=[
                    self.fullname_input,
                    self.email_input,
                    self.dob_input,
                    ft.Divider(),
                    ft.FilledButton(
                        content="Edit profile",
                        icon=ft.Icons.SAVE,
                        expand=True,
                        on_click=self.save_profile,
                    ),
                ],
            )
        )

        # ===== PASSWORD =====
        self.old_pw = ft.TextField(
            label="Current password",
            password=True,
            can_reveal_password=True,
        )

        self.new_pw = ft.TextField(
            label="New password",
            password=True,
            can_reveal_password=True,
        )

        self.password_panel = ft.Column(
            visible=False,
            spacing=10,
            controls=[
                self.old_pw,
                self.new_pw,
                ft.FilledButton(
                    content="Save password",
                    icon=ft.Icons.SAVE,
                    on_click=self.handle_change_password,
                ),
            ],
        )

        security_card = self.card(
            ft.Column(
                spacing=10,
                controls=[
                    ft.Text("Security", weight=ft.FontWeight.BOLD),
                    ft.FilledButton(
                        content="Change password",
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

        # ===== LAYOUT =====
        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=380,
                        content=ft.Column(
                            spacing=0,
                            controls=[
                                header,
                                info_card,
                                security_card,
                                ft.Container(expand=True),
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
    def save_profile(self, _):
        self.dob_value = self.dob_input.value

        if not self.dob_value:
            self.show_error("Date of birth is required")
            return

        if self.calc_age() < 18:
            self.show_error("User must be at least 18 years old")
            return

        update_user_profile(
            self.user_id,
            {
                "FullName": self.fullname_input.value,
                "Email": self.email_input.value,
                "DateOfBirth": self.dob_value,
                "Avatar": self.avatar_path,
            },
        )

        self.show_success("Profile saved successfully")
        self.page.go("/Account")

    # ===== PASSWORD =====
    def toggle_password_panel(self, _):
        self.password_panel.visible = not self.password_panel.visible
        self.page.update()

    def handle_change_password(self, _):
        ok = change_password(
            self.user_id,
            self.old_pw.value,
            self.new_pw.value,
        )
        if ok:
            self.show_success("Password changed successfully")
        else:
            self.show_error("Incorrect current password")

    # ===== NAV =====
    def on_nav_change(self, e):
        routes = ["/Home", "/Chat", "/Trip", "/Support", "/Account"]
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
    page.go("/Account")


if __name__ == "__main__":
    ft.run(main)
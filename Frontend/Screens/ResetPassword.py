import flet as ft
from Frontend.Style import COLORS, PRIMARY_BUTTON_STYLE
from Backend.Picar.Services.AuthService import AuthService

class ResetPasswordScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/ResetPassword",
            bgcolor=COLORS["bg"],
            padding=20,
        )

        self.new_password = ft.TextField(
            label="Mật khẩu mới",
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,  # Làm các dấu chấm mật khẩu to và rõ hơn
                size=18
            ),
            password=True,
            width=float("inf"),
            border_color=COLORS["border"],
            focused_border_color=COLORS["primary"],
        )

        self.confirm_password = ft.TextField(
            label="Xác nhận mật khẩu",
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,  # Làm các dấu chấm mật khẩu to và rõ hơn
                size=18
            ),
            password=True,
            width=float("inf"),
            border_color=COLORS["border"],
            focused_border_color=COLORS["primary"],
        )

        self.submit_btn = ft.FilledButton(
            content=ft.Text("Xác nhận", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            style=PRIMARY_BUTTON_STYLE,
            width=float("inf"),
            height=45,
            on_click=self.reset_password
        )

        # 🌟 GIAO DIỆN MOBILE 380px
        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=380,                 # ✅ MOBILE WIDTH
                        padding=20,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(height=60),

                                ft.Text(
                                    "Đặt lại mật khẩu",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLORS["text"],
                                    text_align=ft.TextAlign.CENTER
                                ),

                                ft.Text(
                                    "Vui lòng nhập mật khẩu mới cho tài khoản của bạn",
                                    size=14,
                                    color=COLORS["muted"],
                                    text_align=ft.TextAlign.CENTER
                                ),

                                ft.Container(height=30),

                                self.new_password,
                                ft.Container(height=10),
                                self.confirm_password,

                                ft.Container(height=25),
                                self.submit_btn,
                            ]
                        )
                    )
                ]
            )
        ]

    async def reset_password(self, e):
        pwd = self.new_password.value
        confirm = self.confirm_password.value

        if not pwd or not confirm:
            self.show_snack("Vui lòng nhập đầy đủ mật khẩu")
            return

        if pwd != confirm:
            self.show_snack("Mật khẩu xác nhận không khớp")
            return

        contact = self.page.session.store.get("reset_contact")
        if not contact:
            self.show_snack("Phiên đặt lại mật khẩu đã hết hạn")
            self.page.go("/ForgotPassword")
            return

        try:
            result = await AuthService.update_password(contact, pwd)

            if not result:
                self.show_snack("Không thể đặt lại mật khẩu")
                return

            self.show_snack("Đặt lại mật khẩu thành công 🎉")
            self.page.go("/Login")

        except Exception as ex:
            self.show_snack(f"Lỗi: {ex}")

    def show_snack(self, message):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=COLORS["primary"],
        )
        self.page.snack_bar.open = True
        self.page.update()


async def main(page: ft.Page):

    page.views.append(ResetPasswordScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)
import flet as ft
from Frontend.Screens.Login import LoginScreen
from Frontend.Screens.Register import RegisterScreen
from Frontend.Screens.Register2 import RegisterScreen2
from Frontend.Screens.Register3 import RegisterScreen3
from Frontend.Screens.Dashboard import DashboardScreen
from Frontend.Screens.ForgotPassword import ForgotPasswordScreen
from Frontend.Screens.VerifyOTP import VerifyOTPScreen   # ❌ THIẾU
from Frontend.Screens.ResetPassword import ResetPasswordScreen

async def main(page: ft.Page):
    page.title = "PiCar - Rental Vehicle System"
    page.window_width = 393
    page.window_height = 853

    page.window_resizable = False
    page.update()

    async def route_change(e):
        page.views.clear()
        if page.route == "/Login":
            # Khởi tạo View Login
            page.views.append(LoginScreen(page))
        elif page.route == "/Register":
            page.views.append(RegisterScreen(page))
        elif page.route == "/Register2":
            page.views.append(RegisterScreen2(page))
        elif page.route == "/Register3":
            page.views.append(RegisterScreen3(page))
        elif page.route == "/Dashboard":
            page.views.append(DashboardScreen(page))
        elif page.route == "/ForgotPassword":
            page.views.append(ForgotPasswordScreen(page))
        elif page.route == "/":
            page.views.append(ForgotPasswordScreen(page))
        elif page.route == "/VerifyOTP":
            page.views.append(VerifyOTPScreen(page))
        elif page.route == "/ResetPassword":
            page.views.append(ResetPasswordScreen(page))

        # Luôn await khi update trong hàm async
        page.update()

    page.on_route_change = route_change

    # Sử dụng push_route chuẩn (không cần _async ở bản 0.80.2)
    await page.push_route("/Login")

    page.on_route_change = route_change
    # page.go("/ForgotPassword")
    await page.push_route("/ForgotPassword")

if __name__ == "__main__":
    # Dùng ft.run để xóa cảnh báo Deprecated
    ft.run(main)
import flet as ft
from Frontend.Style import COLORS


class NotificationScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Notification",
            bgcolor=ft.Colors.WHITE,
            controls=[
                # ===== WRAPPER (ÉP KIỂU MOBILE) =====
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                    content=ft.Container(
                        width=390,  # 👈 ép kiểu mobile
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Column(
                            controls=[
                                # ===== HEADER =====
                                ft.Container(
                                    padding=15,
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.VerticalAlignment.CENTER,
                                        controls=[
                                            ft.IconButton(
                                                icon=ft.Icons.ARROW_BACK_IOS_NEW,
                                                icon_size=18,
                                                icon_color=ft.Colors.BLACK,
                                                on_click=lambda _: page.go("/Dashboard"),
                                            ),
                                            ft.Text(
                                                "Thông báo",
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.BLACK,
                                            ),
                                            ft.Icon(ft.Icons.MORE_VERT, color=ft.Colors.BLACK),
                                        ],
                                    ),
                                ),

                                # ===== NOTIFICATION CARD =====
                                ft.Container(
                                    margin=ft.Margin.only(left=15, right=15, top=10),
                                    padding=15,
                                    border_radius=12,
                                    border=ft.border.all(1, ft.Colors.GREY_300),
                                    bgcolor=ft.Colors.WHITE,
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.NOTIFICATIONS_NONE,
                                                color=ft.Colors.BLACK,
                                            ),
                                            ft.Text(
                                                "Không có thông báo mới",
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.BLACK,
                                            ),
                                        ],
                                    ),
                                ),
                            ]
                        ),
                    ),
                )
            ],
        )


async def main(page: ft.Page):
    page.window_width = 430
    page.window_height = 800
    page.window_resizable = False

    page.views.append(NotificationScreen(page))
    page.update()


if __name__ == "__main__":
    ft.run(main)

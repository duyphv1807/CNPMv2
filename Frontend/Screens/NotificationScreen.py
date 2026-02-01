import flet as ft
from Frontend.Style import COLORS

class NotificationScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Notification",
            bgcolor=ft.Colors.WHITE,
            padding=0,
        )

        self.navigation_bar_custom = ft.NavigationBar(
            destinations=[
                ft.NavigationBarDestination(icon=ft.Icons.HOME, label="Home"),
                ft.NavigationBarDestination(icon=ft.Icons.CHAT_BUBBLE_OUTLINE, label="Chat"),
                ft.NavigationBarDestination(icon=ft.Icons.DIRECTIONS_CAR, label="Trip"),
                ft.NavigationBarDestination(icon=ft.Icons.NOTIFICATIONS, label="Notification"),
                ft.NavigationBarDestination(icon=ft.Icons.PERSON_OUTLINE, label="Account"),
            ],
            selected_index=3,
            height=65,
            on_change=self.on_nav_change
        )

        self.controls = [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=380,  # Ép chuẩn mobile
                        bgcolor=COLORS["bg"],
                        content=ft.Column(
                            spacing=0,
                            controls=[
                                ft.Container(
                                    padding=ft.Padding(10, 40, 10, 10),
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,  # Căn giữa các thành phần trong Row
                                        vertical_alignment=ft.VerticalAlignment.CENTER,
                                        controls=[
                                            ft.Container(width=48),
                                            ft.Container(
                                                expand=True,
                                                content=ft.Text(
                                                    "Notification",
                                                    size=20,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=COLORS["primary"],
                                                    text_align=ft.TextAlign.CENTER,
                                                ),
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.MORE_VERT,
                                                icon_color=COLORS["primary"],
                                                width=48,  # Cố định chiều rộng để khớp với Container đối trọng bên trái
                                                on_click=lambda _: print("More clicked"),
                                            ),
                                        ],
                                    ),
                                ),
                                ft.Container(
                                    padding=ft.Padding(20, 10, 20, 10),
                                    expand=True,  # Lấy phần diện tích còn lại giữa Header và Nav
                                    content=ft.Column(
                                        scroll=ft.ScrollMode.AUTO,  # Chỉ cuộn trong vùng này
                                        controls=[
                                            # NOTIFICATION CARD
                                            ft.Container(
                                                padding=15,
                                                bgcolor="#FFFFFF",
                                                border_radius=16,
                                                shadow=ft.BoxShadow(
                                                    blur_radius=10,
                                                    color=ft.Colors.with_opacity(0.05, "black"),
                                                    offset=ft.Offset(0, 4)
                                                ),
                                                content=ft.Row(
                                                    spacing=15,
                                                    controls=[
                                                        ft.Container(
                                                            content=ft.Icon(ft.Icons.NOTIFICATIONS_NONE_ROUNDED,
                                                                            color=COLORS["primary"], size=28),
                                                            bgcolor="#F8F9FA",
                                                            padding=10,
                                                            border_radius=10
                                                        ),
                                                        ft.Column([
                                                            ft.Text("No new notificattion", weight=ft.FontWeight.BOLD,
                                                                    size=15, color="#1A1A1A"),
                                                            ft.Text("We will notify you when there is new information.",
                                                                    color=ft.Colors.GREY_500, size=13),
                                                        ], expand=True, spacing=4),
                                                    ]
                                                )
                                            ),
                                        ],
                                    )
                                ),
                                self.navigation_bar_custom
                            ]
                        )
                    )
                ]
            )
        ]

    def on_nav_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.page.go("/Dashboard")
        elif index == 1:
            self.page.go("/Chat")
        elif index == 2:
            self.page.go("/Trip")
        elif index == 3:
            self.page.go("/Notification")
        elif index == 4:
            self.page.go("/Account")

    def append_notification(self):
        pass

async def main(page: ft.Page):

    # Reset views và hiển thị
    page.views.clear()
    page.views.append(NotificationScreen(page))
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
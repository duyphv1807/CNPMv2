import flet as ft


class ChatScreen(ft.View):
    def __init__(self):
        super().__init__(
            route="/Chat",
            bgcolor="#E5E7EB",
            padding=0
        )

        # ================= HEADER =================
        header = ft.Container(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK_IOS_NEW,
                        icon_size=18,
                        icon_color = "black",
                        on_click=lambda e: self.page.go("/Dashboard")
                    ),
                    ft.Text(
                        "Chat",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#111827"
                    ),
                    ft.Icon(ft.Icons.MORE_VERT)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=15,
            bgcolor="white",
            border=ft.border.only(
                bottom=ft.BorderSide(1, "#E5E7EB")
            )
        )

        # ================= CHAT LIST =================
        self.chat_list = ft.Column(
            expand=True,
            spacing=12,
            scroll=ft.ScrollMode.AUTO
        )

        chat_area = ft.Container(
            expand=True,
            padding=16,
            content=self.chat_list
        )

        # ================= INPUT =================
        self.input_message = ft.TextField(
            hint_text="Nhập tin nhắn...",
            expand=True,
            border_radius=25,
            filled=True,
            bgcolor="#F9FAFB",
            text_size=14,
            color="#111827",
            hint_style=ft.TextStyle(color="#9CA3AF"),
            border=ft.InputBorder.NONE
        )

        send_button = ft.ElevatedButton(
            "Gửi",
            on_click=self.send_message,
            style=ft.ButtonStyle(
                bgcolor="#2563EB",
                color="white",
                shape=ft.RoundedRectangleBorder(radius=25)
            )
        )

        input_bar = ft.Container(
            content=ft.Row(
                [self.input_message, send_button],
                spacing=10
            ),
            padding=12,
            bgcolor="white",
            border=ft.border.only(
                top=ft.BorderSide(1, "#E5E7EB")
            )
        )

        # ================= MOBILE FRAME =================
        mobile_frame = ft.Container(
            width=420,                 # 👈 ép kiểu mobile
            height=float("inf"),
            bgcolor="white",
            border_radius=16,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Column(
                [
                    header,
                    chat_area,
                    input_bar
                ],
                expand=True
            )
        )

        # ================= CENTER =================
        self.controls = [
            ft.Row(
                [
                    mobile_frame
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=True
            )
        ]

        # ================= WELCOME =================
        self.add_bot_message("Xin chào 👋 Tôi có thể hỗ trợ gì cho bạn?")

    # ================= USER MESSAGE =================
    def add_user_message(self, text):
        self.chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            text,
                            color="#111827",
                            weight=ft.FontWeight.W_600
                        ),
                        bgcolor="#E8F0FF",
                        padding=14,
                        border_radius=18,
                        width=300
                    )
                ],
                alignment=ft.MainAxisAlignment.END
            )
        )

    # ================= BOT MESSAGE =================
    def add_bot_message(self, text):
        self.chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Text(
                            text,
                            color="#111827",
                            weight=ft.FontWeight.W_500
                        ),
                        bgcolor="#F3F4F6",
                        padding=14,
                        border_radius=18,
                        width=300
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            )
        )

    # ================= SEND =================
    def send_message(self, e):
        text = self.input_message.value.strip()
        if not text:
            return

        self.add_user_message(text)
        self.input_message.value = ""

        self.add_bot_message("Cảm ơn bạn đã nhắn tin 😊")
        self.page.update()

# --- Chạy main ---
async def main(page: ft.Page):

    page.views.append(ChatScreen())
    page.update()

if __name__ == "__main__":
    ft.run(main)
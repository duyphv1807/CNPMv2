import flet as ft


class ChatScreen(ft.View):
    def __init__(self):
        super().__init__(
            route="/Chat",
            bgcolor="#F5F6FA",
            padding=0
        )

        # ================= HEADER =================
        header = ft.Container(
            content=ft.Row(
                [
                    ft.TextButton(
                        "← Quay lại",
                        on_click=lambda e: self.page.go("/Dashboard"),
                        style=ft.ButtonStyle(
                            color="#2563EB"
                        )
                    ),
                    ft.Text(
                        "Chat hỗ trợ",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#111827"
                    )
                ],
                spacing=15
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
            padding=20,
            content=self.chat_list
        )

        # ================= INPUT =================
        self.input_message = ft.TextField(
    hint_text="Nhập tin nhắn...",
    expand=True,
    border_radius=25,
    filled=True,
    bgcolor="white",
    text_size=14,
    color="#111827",          
    hint_style=ft.TextStyle(  
        color="#9CA3AF"
    )
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
            padding=15,
            bgcolor="white",
            border=ft.border.only(
                top=ft.BorderSide(1, "#E5E7EB")
            )
        )

        self.controls = [
            header,
            chat_area,
            input_bar
        ]

        # ================= WELCOME MESSAGE =================
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
                        width=400
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
                        bgcolor="white",
                        padding=14,
                        border_radius=18,
                        width=400
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

        # Trả lời tự động (demo)
        self.add_bot_message("Cảm ơn bạn đã nhắn tin 😊")

        self.page.update()
        



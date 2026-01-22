import flet as ft
from Frontend.Style import COLORS, FONTS
from Backend.ExcuteDatabase import supabase


class WalletScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Wallet",
            bgcolor=COLORS["bg"],
            padding=10,
        )

        # ================= BIẾN =================
        self.user_id = None
        self.balance = 0
        self.show_balance = True
        self.is_bank_linked = False

        # ================= SỐ DƯ =================
        self.balance_text = ft.Text(
            "0",
            size=34,
            weight=ft.FontWeight.BOLD,
            color=COLORS["primary"]
        )

        self.eye_button = ft.IconButton(
            icon=ft.Icons.VISIBILITY,
            on_click=self.toggle_balance
        )

        # ================= INPUT =================
        self.amount_input = ft.TextField(
            label="Amount (VND)",
            width=320,
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.PAYMENTS
        )

        self.message_text = ft.Text("", size=14)

        self.bank_status_text = ft.Text(
            "Bank not yet linked",
            color=ft.Colors.RED
        )

        # ================= CARD VÍ =================
        wallet_card = ft.Container(
            width=360,
            padding=25,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=15,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 6)
            ),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
                controls=[
                    ft.Icon(
                        ft.Icons.ACCOUNT_BALANCE_WALLET,
                        size=70,
                        color=COLORS["primary"]
                    ),

                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[self.balance_text, self.eye_button]
                    ),

                    ft.Text("VNĐ", color=COLORS["muted"]),
                ]
            )
        )

        # ================= CARD GIAO DỊCH =================
        action_card = ft.Container(
            width=360,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=12,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 4)
            ),
            content=ft.Column(
                spacing=12,
                controls=[
                    self.amount_input,

                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.FilledButton(
                                "Deposit",
                                width=150,
                                on_click=lambda e: self.page.run_task(self.deposit_money)
                            ),
                            ft.FilledButton(
                                "Withdraw",
                                width=150,
                                bgcolor=ft.Colors.RED_400,
                                on_click=lambda e: self.page.run_task(self.withdraw_money)
                            ),
                        ]
                    ),

                    self.message_text
                ]
            )
        )

        # ================= CARD NGÂN HÀNG =================
        bank_card = ft.Container(
            width=360,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=12,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 4)
            ),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Text(
                        "Bank",
                        size=18,
                        weight=ft.FontWeight.BOLD
                    ),

                    self.bank_status_text,

                    ft.FilledButton(
                        "Bank Links",
                        width=220,
                        on_click=lambda _: self.page.push_route("/LinkBank")
                    )
                ]
            )
        )

        # ================= LAYOUT MOBILE =================
        self.controls = [
            ft.Stack(
                expand=True,
                controls=[
                    # ===== BACK BUTTON =====
                    ft.Container(
                        top=10,
                        left=10,
                        content=ft.TextButton(
                            "← Come back",
                            on_click=lambda _: self.page.push_route("/Account")
                        )
                    ),

                    # ===== MOBILE CENTER =====
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=22,
                            controls=[
                                ft.Text(
                                    "MY WALLET",
                                    size=FONTS["title"],
                                    weight=ft.FontWeight.BOLD
                                ),

                                wallet_card,
                                action_card,
                                bank_card,
                            ]
                        )
                    )
                ]
            )
        ]

    # ================= LOAD WALLET =================
    def did_mount(self):
        self.page.run_task(self.load_wallet, None)

    async def load_wallet(self, e):
        user = self.page.session.store.get("user")
        if not user:
            return

        self.user_id = user["UserID"]

        result = supabase.table("User_Admin") \
            .select("Balance, BankName") \
            .eq("UserID", self.user_id) \
            .single() \
            .execute()

        self.balance = result.data.get("Balance", 0)

        bank_name = result.data.get("BankName")
        if bank_name:
            self.is_bank_linked = True
            self.bank_status_text.value = f"Linked: {bank_name}"
            self.bank_status_text.color = ft.Colors.GREEN
        else:
            self.is_bank_linked = False
            self.bank_status_text.value = "Bank not yet linked"
            self.bank_status_text.color = ft.Colors.RED

        self.update_balance_text()
        self.update()

    # ================= TIỆN ÍCH =================
    def update_balance_text(self):
        self.balance_text.value = (
            f"{self.balance:,.0f}" if self.show_balance else "••••••"
        )

    def toggle_balance(self, e):
        self.show_balance = not self.show_balance
        self.eye_button.icon = (
            ft.Icons.VISIBILITY if self.show_balance else ft.Icons.VISIBILITY_OFF
        )
        self.update_balance_text()
        self.update()

    # ================= NẠP TIỀN =================
    async def deposit_money(self):
        if not self.is_bank_linked:
            self.message_text.value = "Please link your bank account"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        try:
            amount = int(self.amount_input.value)
            if amount <= 0:
                raise ValueError
        except:
            self.message_text.value = "Invalid amount"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        self.balance += amount
        supabase.table("User_Admin").update(
            {"Balance": self.balance}
        ).eq("UserID", self.user_id).execute()

        self.amount_input.value = ""
        self.message_text.value = "Deposit successful"
        self.message_text.color = ft.Colors.GREEN
        self.update_balance_text()
        self.update()

    # ================= RÚT TIỀN =================
    async def withdraw_money(self):
        if not self.is_bank_linked:
            self.message_text.value = "Please link your bank account"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        try:
            amount = int(self.amount_input.value)
            if amount <= 0 or amount > self.balance:
                raise ValueError
        except:
            self.message_text.value = "Invalid amount"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        self.balance -= amount
        supabase.table("User_Admin").update(
            {"Balance": self.balance}
        ).eq("UserID", self.user_id).execute()

        self.amount_input.value = ""
        self.message_text.value = "Withdrawal successful"
        self.message_text.color = ft.Colors.GREEN
        self.update_balance_text()
        self.update()


# ================= MAIN =================
async def main(page: ft.Page):
    # GIẢ LẬP MÀN HÌNH MOBILE
    page.window_width = 420
    page.window_height = 820
    page.window_resizable = False

    page.views.append(WalletScreen(page))
    page.update()


if __name__ == "__main__":
    ft.run(main)

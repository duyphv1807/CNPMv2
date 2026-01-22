import flet as ft
from Backend.ExcuteDatabase import supabase


class LinkBankScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/LinkBank",
            bgcolor=ft.Colors.GREY_100,
            padding=0
        )

        # ================= INPUT =================
        self.owner_name = ft.TextField(
            label="Account holder's full name",
            width=300,
            prefix_icon=ft.Icons.PERSON
        )

        self.cccd = ft.TextField(
            label="Citizen Identification Number",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.BADGE
        )

        self.bank_name = ft.TextField(
            label="Bank name",
            width=300,
            prefix_icon=ft.Icons.ACCOUNT_BALANCE
        )

        self.bank_account = ft.TextField(
            label="Account number",
            width=300,
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.CREDIT_CARD
        )

        self.message = ft.Text(size=14)

        # ================= FORM KHUNG (QUAN TRỌNG) =================
        form_box = ft.Container(
            width=340,
            padding=16,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=12,
            content=ft.Column(
                spacing=12,
                controls=[
                    self.owner_name,
                    self.cccd,
                    self.bank_name,
                    self.bank_account,
                ]
            )
        )

        # ================= CARD MOBILE =================
        card = ft.Container(
            width=380,
            padding=24,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                blur_radius=15,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 5)
            ),
            content=ft.Column(
                spacing=18,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # ===== TITLE =====
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.ACCOUNT_BALANCE, size=30),
                            ft.Text(
                                "Liên kết ngân hàng",
                                size=22,
                                weight=ft.FontWeight.BOLD
                            )
                        ]
                    ),

                    ft.Text(
                        "Vui lòng nhập thông tin ngân hàng để nạp / rút tiền",
                        size=13,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    ),

                    ft.Divider(),

                    # ===== FORM TRONG 1 KHUNG =====
                    form_box,

                    ft.FilledButton(
                        content=ft.Text("SAVE BANK"),
                        width=300,
                        height=46,
                        on_click=self.save_bank
                    ),

                    self.message
                ]
            )
        )

        # ================= STACK LAYOUT =================
        self.controls = [
            ft.Stack(
                expand=True,
                controls=[
                    # ===== CENTER CARD =====
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=card
                    ),

                    # ===== BACK BUTTON GÓC TRÊN =====
                    ft.Container(
                        top=10,
                        left=10,
                        content=ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip="Quay lại",
                            on_click=lambda e: self.page.push_route("/Wallet")
                        )
                    )
                ]
            )
        ]

    # ================= SAVE BANK =================
    async def save_bank(self, e):
        user = self.page.session.store.get("user")
        if not user:
            self.message.value = "❌ Bạn chưa đăng nhập"
            self.message.color = ft.Colors.RED
            self.update()
            return

        if not all([
            self.owner_name.value,
            self.cccd.value,
            self.bank_name.value,
            self.bank_account.value
        ]):
            self.message.value = "❌ Vui lòng nhập đầy đủ thông tin"
            self.message.color = ft.Colors.RED
            self.update()
            return

        supabase.table("User_Admin").update({
            "BankOwnerName": self.owner_name.value,
            "CCCD": self.cccd.value,
            "BankName": self.bank_name.value,
            "BankAccount": self.bank_account.value
        }).eq("UserID", user["UserID"]).execute()

        self.message.value = "✅ Liên kết ngân hàng thành công"
        self.message.color = ft.Colors.GREEN
        self.update()


# ================= MAIN (TEST RIÊNG) =================
async def main(page: ft.Page):
    page.views.append(LinkBankScreen(page))
    page.update()


if __name__ == "__main__":
    ft.run(main)

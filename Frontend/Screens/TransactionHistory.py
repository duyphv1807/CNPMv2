import flet as ft
from Backend.Picar.ExcuteDatabase import supabase
from datetime import datetime


class TransactionHistoryScreen(ft.View):

    # ================= NAVIGATION =================
    async def go_back(self, _):
        await self.page.push_route("/Wallet")

    # ================= INIT =================
    def __init__(self, _page: ft.Page):
        super().__init__(
            route="/TransactionHistory",
            bgcolor=ft.Colors.GREY_200,
            padding=0
        )

        self.tx_list = ft.Column(spacing=12)

        self.controls = [
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    # ========== MOBILE FRAME ==========
                    ft.Container(
                        width=390,
                        height=780,
                        bgcolor=ft.Colors.GREY_100,
                        border_radius=24,
                        border=ft.Border.all(1, ft.Colors.GREY_300),
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        content=ft.Column(
                            expand=True,
                            controls=[
                                # ========== APP BAR ==========
                                ft.Container(
                                    height=60,
                                    padding=ft.padding.symmetric(horizontal=12),
                                    bgcolor=ft.Colors.WHITE,
                                    shadow=ft.BoxShadow(
                                        blur_radius=10,
                                        color=ft.Colors.GREY_300,
                                        offset=ft.Offset(0, 2)
                                    ),
                                    content=ft.Row(
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.IconButton(
                                                icon=ft.Icons.ARROW_BACK,
                                                on_click=self.go_back
                                            ),
                                            ft.Text(
                                                "Transaction History",
                                                size=18,
                                                weight=ft.FontWeight.BOLD
                                            )
                                        ]
                                    )
                                ),

                                # ========== BODY ==========
                                ft.Container(
                                    expand=True,
                                    padding=16,
                                    content=ft.ListView(
                                        expand=True,
                                        spacing=12,
                                        controls=[self.tx_list]
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        ]

    # ================= LIFECYCLE =================
    def did_mount(self):
        self.page.run_task(self.load_transactions)

    # ================= LOAD DATA =================
    async def load_transactions(self):
        user = self.page.session.store.get("user")
        if not user:
            return

        result = (
            supabase.table("Transaction")
            .select("Type, Amount, BalanceBefore, BalanceAfter, CreatedAt")
            .eq("UserID", user["UserID"])
            .order("CreatedAt", desc=True)
            .execute()
        )

        self.tx_list.controls.clear()

        if not result.data:
            self.tx_list.controls.append(
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.RECEIPT_LONG, size=48, color=ft.Colors.GREY),
                        ft.Text("No transactions yet", color=ft.Colors.GREY)
                    ]
                )
            )
        else:
            for tx in result.data:
                self.tx_list.controls.append(
                    self.build_transaction_item(tx)
                )

        self.update()

    # ================= ITEM UI =================
    @staticmethod
    def build_transaction_item(tx):
        is_deposit = tx["Type"] == "DEPOSIT"

        created_at_raw = tx.get("CreatedAt")
        created_at = (
            datetime.fromisoformat(created_at_raw.replace("Z", ""))
            .strftime("%d/%m/%Y %H:%M")
            if created_at_raw else ""
        )

        return ft.Container(
            padding=14,
            border_radius=14,
            bgcolor=ft.Colors.WHITE,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.CircleAvatar(
                                bgcolor=ft.Colors.GREEN_100 if is_deposit else ft.Colors.RED_100,
                                content=ft.Icon(
                                    ft.Icons.ARROW_DOWNWARD if is_deposit else ft.Icons.ARROW_UPWARD,
                                    color=ft.Colors.GREEN if is_deposit else ft.Colors.RED
                                )
                            ),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        "Deposit" if is_deposit else "Withdraw",
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    ft.Text(
                                        created_at,  # ✅ BIẾN ĐƯỢC DÙNG Ở ĐÂY
                                        size=12,
                                        color=ft.Colors.GREY
                                    )
                                ]
                            )
                        ]
                    ),
                    ft.Text(
                        f"{'+' if is_deposit else '-'}{tx['Amount']:,.0f} VNĐ",
                        color=ft.Colors.GREEN if is_deposit else ft.Colors.RED,
                        weight=ft.FontWeight.BOLD
                    )
                ]
            )
        )


# ================= TEST RUN =================
async def main(page: ft.Page):
    page.views.append(TransactionHistoryScreen(page))
    page.update()


if __name__ == "__main__":
    ft.run(main)

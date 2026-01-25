import flet as ft
from Frontend.Style import COLORS
from Backend.Picar.ExcuteDatabase import supabase


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
                        on_click=lambda _: self.page.go("/LinkBank")
                    )
                ]
            )
        )

        # ================= LAYOUT MOBILE =================
        MAX_WIDTH = 420

        self.controls = [
            ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[

                    # ================= HEADER =================
                    ft.Container(
                        width=float("inf"),
                        padding=ft.padding.symmetric(vertical=10),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    width=MAX_WIDTH,
                                    padding=ft.padding.symmetric(horizontal=12),
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            # ⬅ Back
                                            ft.IconButton(
                                                icon=ft.Icons.ARROW_BACK,
                                                on_click=lambda _: self.page.go("/Account")
                                            ),

                                            # Title
                                            ft.Text(
                                                "MY WALLET",
                                                size=22,
                                                weight=ft.FontWeight.BOLD
                                            ),

                                            # Spacer cân layout
                                            ft.Container(width=40)
                                        ]
                                    )
                                )
                            ]
                        )
                    ),

                    # ================= CONTENT =================
                    wallet_card,
                    action_card,
                    bank_card,
                ]
            )
        ]

    # ================= LOAD WALLET =================
    def did_mount(self):
        # Thử lấy cả 2 key phổ biến bạn thường đặt
        user_data = self.page.session.store.get("user_data") or self.page.session.store.get("user")

        if user_data:
            # Gán ID tự động từ dữ liệu tìm thấy
            self.user_id = user_data.get("UserID")
            print(f"--- WALLET DEBUG: Đã nhận diện UserID: {self.user_id} ---")

            # Chạy hàm load ví
            self.page.run_task(self.load_wallet)
        else:
            # Nếu vẫn trống, in ra toàn bộ session để kiểm tra tên key thực tế là gì
            print(f"--- WALLET DEBUG: Session hiện tại: {self.page.session.store._data}")
            print("--- WALLET DEBUG: Session trống, chuyển về Login ---")
            self.page.go("/Login")

    async def load_wallet(self, e=None):
        try:
            # SỬA TÊN BẢNG: Thay "User_Admin" bằng tên bảng bạn thấy trong ảnh (ví dụ: "Wallet")
            result = supabase.table("Wallet") \
                .select("Balance") \
                .eq("UserID", self.user_id) \
                .execute()

            if result.data:
                record = result.data[0]
                # Lấy tiền từ bảng Wallet
                self.balance = float(record.get("Balance", 0))

                print(f"--- WALLET DEBUG: Đã tìm thấy tiền ở bảng Wallet: {self.balance}")
                self.update_balance_text()
                self.update()
            else:
                # Nếu không tìm thấy trong bảng Wallet, có thể User này chưa có ví
                print(f"--- WALLET DEBUG: User {self.user_id} chưa có bản ghi trong bảng Wallet")
                self.balance = 0
                self.update_balance_text()
                self.update()

        except Exception as ex:
            print(f"--- WALLET DEBUG: Lỗi truy vấn bảng Wallet: {ex}")
    # ================= REFRESH BALANCE REALTIME =================
    def refresh_balance_from_db(self):

        # Gọi lại DB để lấy balance mới nhất
        # Đảm bảo Wallet realtime – KHÔNG tự cộng trừ
        result = (
            supabase.table("User_Admin")
            .select("Balance")
            .eq("UserID", self.user_id)
            .single()
            .execute()
        )

        if result.data:
            self.balance = result.data["Balance"]
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
        # Chưa liên kết ngân hàng
        if not self.is_bank_linked:
            self.message_text.value = "Please link your bank account"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        # Kiểm tra số tiền nhập
        try:
            amount = int(self.amount_input.value)
            if amount <= 0:
                raise ValueError
        except:
            self.message_text.value = "Invalid amount"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        # LẤY balance từ DB
        result = (
            supabase.table("User_Admin")
            .select("Balance")
            .eq("UserID", self.user_id)
            .single()
            .execute()
        )

        new_balance = result.data["Balance"] + amount

        # Update DB
        supabase.table("User_Admin").update(
            {"Balance": new_balance}
        ).eq("UserID", self.user_id).execute()

        # REFRESH REALTIME
        self.refresh_balance_from_db()

        self.amount_input.value = ""
        self.message_text.value = "Deposit successful"
        self.message_text.color = ft.Colors.GREEN

    # ================= RÚT TIỀN =================
    async def withdraw_money(self):
        # Chưa liên kết ngân hàng
        if not self.is_bank_linked:
            self.message_text.value = "Please link your bank account"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        # Kiểm tra số tiền
        try:
            amount = int(self.amount_input.value)
            if amount <= 0:
                raise ValueError
        except:
            self.message_text.value = "Invalid amount"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        result = (
            supabase.table("User_Admin")
            .select("Balance")
            .eq("UserID", self.user_id)
            .single()
            .execute()
        )

        if amount > result.data["Balance"]:
            self.message_text.value = "Insufficient balance"
            self.message_text.color = ft.Colors.RED
            self.update()
            return

        new_balance = result.data["Balance"] - amount

        # Update DB
        supabase.table("User_Admin").update(
            {"Balance": new_balance}
        ).eq("UserID", self.user_id).execute()

        # Reset UI
        self.amount_input.value = ""
        self.message_text.value = "Withdrawal successful"
        self.message_text.color = ft.Colors.GREEN
        self.update_balance_text()
        self.update()


# ================= MAIN =================
async def main(page: ft.Page):
    page.views.append(WalletScreen(page))
    page.update()


if __name__ == "__main__":
    ft.run(main)

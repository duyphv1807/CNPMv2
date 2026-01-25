import flet as ft

class CancellationPolicyScreen(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/CancellationPolicy",
            padding=0,
            bgcolor="#F5F5F5",
        )

        # --- Header ---
        self.nav_top = ft.Container(
            padding=ft.Padding(10, 40, 10, 10),
            bgcolor="white",
            content=ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK_IOS_NEW, icon_color="black", on_click=lambda _: page.go("/Booking"), icon_size=18),
                # Chữ tiêu đề màu đen
                ft.Text("Chính sách hủy chuyến", size=18, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER, color="black"),
            ])
        )

        # --- Bảng chính sách ---
        self.policy_table = ft.Container(
            padding=15,
            content=ft.Column([
                # Header Table
                ft.Row([
                    ft.Container(
                        content=ft.Text("Thời Điểm Hủy Chuyến", weight=ft.FontWeight.BOLD, size=13, color="black"),
                        expand=True, alignment=ft.Alignment.CENTER, padding=10,
                        # Viền bảng đổi sang màu đen (hoặc grey)
                        border=ft.Border.all(1, "black")
                    ),
                    ft.Container(
                        content=ft.Text("Phí Hủy Chuyến", weight=ft.FontWeight.BOLD, size=13, color="black"),
                        expand=True, alignment=ft.Alignment.CENTER, padding=10,
                        border=ft.Border.all(1, "black")
                    ),
                ], spacing=0),
                # Các hàng dữ liệu
                self.table_row("Trong Vòng 1h Sau Giữ Chỗ", "Miễn phí", True),
                self.table_row("Trước Chuyến Đi > 7 Ngày\n(Sau 1h Giữ Chỗ)", "10% giá trị chuyến đi", True),
                self.table_row("Trong Vòng 7 Ngày Trước Chuyến Đi\n(Sau 1h Giữ Chỗ)", "40% giá trị chuyến đi", False),
            ], spacing=0)
        )

        # --- Các lưu ý bằng văn bản ---
        self.notes = ft.Container(
            padding=15,
            content=ft.Column([
                # Đổi toàn bộ color thành "black"
                ft.Text(
                    "* Chính sách hủy chuyến áp dụng chung cho cả khách thuê và chủ xe (ngoài ra, tùy vào thời điểm hủy chuyến, chủ xe có thể bị đánh giá từ 2-3* trên hệ thống).",
                    size=12, color="black"
                ),
                ft.Text(
                    "* Khách thuê không nhận xe sẽ mất phí hủy chuyến (40% giá trị chuyến đi).",
                    size=12, color="black"
                ),
                ft.Text(
                    "* Chủ xe không giao xe sẽ hoàn tiền giữ chỗ & bồi thường phí hủy chuyến cho khách thuê (40% giá trị chuyến đi).",
                    size=12, color="black"
                ),
                ft.Text(
                    "* Tiền giữ chỗ & bồi thường do chủ xe hủy chuyến (nếu có) sẽ được Mioto hoàn trả đến khách thuê bằng chuyển khoản ngân hàng trong vòng 1-3 ngày làm việc kế tiếp.",
                    size=12, color="black"
                ),
            ], spacing=0)
        )

        # --- Layout Mobile Center ---
        self.controls = [
            ft.Container(
                expand=True,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.VerticalAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=380,
                            height=800,
                            bgcolor="white",
                            border_radius=20,
                            shadow=ft.BoxShadow(blur_radius=20, color="black12"),
                            content=ft.Column([
                                self.nav_top,
                                ft.Column([
                                    self.policy_table,
                                    self.notes
                                ], scroll=ft.ScrollMode.AUTO, expand=True)
                            ], spacing=0)
                        )
                    ]
                )
            )
        ]

    def table_row(self, time_text, fee_text, is_success):
        icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color="green", size=20) if is_success else ft.Icon(ft.Icons.CANCEL, color="red", size=20)
        return ft.Row([
            ft.Container(
                # Chữ trong bảng màu đen
                content=ft.Text(time_text, size=12, text_align=ft.TextAlign.CENTER, color="black"),
                expand=True, alignment=ft.Alignment.CENTER, padding=10,
                # Viền hàng màu đen
                border=ft.Border.all(1, "black"), height=80
            ),
            ft.Container(
                content=ft.Column([
                    icon,
                    ft.Text(fee_text, size=12, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.NORMAL, color="black")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                expand=True, alignment=ft.Alignment.CENTER, padding=10,
                border=ft.Border.all(1, "black"), height=80
            ),
        ], spacing=0)

async def main(page: ft.Page):
    page.views.append(CancellationPolicyScreen(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)
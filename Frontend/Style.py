import flet as ft

# Định nghĩa bảng màu (Palette)
COLORS = {
    "bg": "#FFFFFF",
    "primary": "#000000",       # Màu chủ đạo (nút bấm, icon chính)
    "text": "#000000",          # Màu chữ chính
    "muted": "#757575",         # Màu chữ phụ, placeholder
    "border": "#BDBDBD",        # Màu viền input
    "error": "#B00020",         # Màu thông báo lỗi
    "white": "#FFFFFF"
}

# Định nghĩa kích thước và font (Tùy chỉnh thêm nếu cần)
FONTS = {
    "title": 32,
    "body": 16,
    "button": 18,
}

# Style cho nút bấm (Reusable Style)
PRIMARY_BUTTON_STYLE = ft.ButtonStyle(
    bgcolor=COLORS["primary"],
    color=COLORS["white"],
    shape=ft.RoundedRectangleBorder(radius=8),
)
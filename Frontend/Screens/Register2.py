import flet as ft
import cv2
import base64
import threading
import tkinter as tk
from Frontend.Style import COLORS
from tkinter import filedialog
from Frontend import Screens

class RegisterScreen2(ft.View):
    def __init__(self, page: ft.Page):
        super().__init__(
            route="/Register2",
            bgcolor=COLORS["bg"],
            padding=20,
            scroll=ft.ScrollMode.ADAPTIVE,
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        self.is_explorer_open = False
        # Biến lưu trữ ảnh
        self.images = {"Front photo": None, "Back photo": None}
        self.cam_running = False  # Đảm bảo dòng này có mặt trong __init__
        self.current_upload_side = None

        # FIX: Dùng chuỗi "contain" để tránh AttributeError trên bản Flet cũ
        self.front_preview = ft.Image(src=" ", width=300, height=150, fit=ft.BoxFit.CONTAIN, visible=False)
        self.back_preview = ft.Image(src=" ", width=300, height=150, fit=ft.BoxFit.CONTAIN, visible=False)

        self.front_text = ft.Text("Click to upload Front photo", color=COLORS["muted"])
        self.back_text = ft.Text("Click to upload Back photo", color=COLORS["muted"])

        # --- GIAO DIỆN CHÍNH ---
        self.controls = [
            ft.Container(
                width=350,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_IOS_NEW,
                                icon_size=18,
                                icon_color=COLORS["text"],
                                on_click=lambda _: self.page.go("/Login")
                            ),
                            alignment=ft.Alignment(-1, -1),
                            margin=ft.Margin.only(left=-10)
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "Driver's License Verification",
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLORS["text"]
                                ),
                                ft.Container(height=20),
                                self._create_upload_box("Front photo", self.front_preview, self.front_text),
                                ft.Container(height=20),
                                self._create_upload_box("Back photo", self.back_preview, self.back_text),
                                ft.Container(height=40),
                                ft.FilledButton(
                                    content=ft.Text("Confirm", weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                    width=350,
                                    height=50,
                                    style=ft.ButtonStyle(
                                        bgcolor=COLORS["primary"],
                                        color="#FFFFFF",
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                    on_click=self.handle_confirm
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
                    ],
                    spacing=0
                )
            )
        ]

    def _create_upload_box(self, side, img_control, text_control):
        return ft.Container(
            width=350,
            height=150,
            border=ft.Border.all(1, COLORS["border"]),
            border_radius=10,
            bgcolor=COLORS["bg"],
            content=ft.Column(
                [img_control, text_control],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            on_click=lambda _: self.show_source_dialog(side),
        )

    def show_source_dialog(self, side):
        self.current_upload_side = side

        dlg = ft.AlertDialog(
            title=ft.Text("Chọn nguồn ảnh"),
            content=ft.Row([
                ft.Column([
                    ft.IconButton(ft.Icons.CAMERA_ALT, icon_size=40,
                                  on_click=lambda _: [setattr(dlg, "open", False), self.page.update(),
                                                      self.open_camera(side)]),
                    ft.Text("Máy ảnh")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                ft.VerticalDivider(),
                ft.Column([
                    ft.IconButton(
                        ft.Icons.FOLDER,
                        icon_size=40,
                        # Đóng Dialog Flet trước khi bật Explorer của hệ thống
                        on_click=lambda _: [setattr(dlg, "open", False), self.page.update(), self.open_folder(side)],
                    ),
                    ft.Text("Thư mục")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20, height=100),
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def open_folder(self, side):
        # Kiểm tra nếu đã có cửa sổ Explorer đang mở thì thoát ngay
        if self.is_explorer_open:
            print("Explorer is already open!")
            return

        self.is_explorer_open = True

        try:
            # Khởi tạo Tkinter ngầm
            root = tk.Tk()
            root.withdraw()  # Ẩn cửa sổ chính của Tkinter

            # ÉP CỬA SỔ CHỌN FILE LÊN TRÊN CÙNG (Always on top)
            root.attributes("-topmost", True)

            # Mở hộp thoại chọn file
            file_path = filedialog.askopenfilename(
                parent=root,  # Gắn vào root để thừa hưởng thuộc tính topmost
                title=f"Select {side}",
                filetypes=[("Image files", "*.jpg *.jpeg *.png")]
            )

            # Đóng cửa sổ ngầm ngay lập tức
            root.destroy()

            if file_path:
                self.display_image(file_path, side)

        finally:
            # Luôn giải phóng khóa sau khi đóng cửa sổ (dù chọn ảnh hay hủy)
            self.is_explorer_open = False
            self.page.update()

    def open_camera(self, side):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cam_preview = ft.Image(src="", width=400, height=300)

        self.cam_running = True

        def stop_cam(e):
            self.cam_running = False
            cap.release()
            cam_dlg.open = False
            self.page.update()

        def capture(e):
            ret, frame = cap.read()
            if ret:
                self.display_image(frame, side, is_frame=True)
            stop_cam(e)

        cam_dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Capture {side}"),
            content=cam_preview,
            actions=[
                ft.TextButton("Hủy", on_click=stop_cam),
                ft.FilledButton("CAPTURE", bgcolor=COLORS["primary"], color="white", on_click=capture),
            ],
        )
        self.page.overlay.append(cam_dlg)
        cam_dlg.open = True
        self.page.update()

        def update_camera():
            while self.cam_running:
                ret, frame = cap.read()
                if not ret: break
                frame = cv2.flip(frame, 1)
                _, buffer = cv2.imencode(".jpg", frame)
                b64_string = base64.b64encode(buffer).decode("utf-8")
                cam_preview.src_base64 = b64_string
                self.page.update()

        threading.Thread(target=update_camera, daemon=True).start()

    def display_image(self, source, side, is_frame=False):
        target_img = self.front_preview if side == "Front photo" else self.back_preview
        target_text = self.front_text if side == "Front photo" else self.back_text
        if is_frame:
            _, buffer = cv2.imencode(".jpg", source)
            img_b64 = base64.b64encode(buffer).decode("utf-8")
            self.images[side] = source
            target_img.src_base64 = img_b64
        else:
            self.images[side] = source
            target_img.src = source
        target_img.visible = True
        target_text.visible = False
        self.page.update()

    async def handle_confirm(self, e):
        # 1. Kiểm tra đầu vào cơ bản
        if not self.images["Front photo"] or not self.images["Back photo"]:
            self.show_message("Thiếu ảnh", "Vui lòng tải lên cả 2 mặt bằng lái xe!")
            return

        # 2. Hiển thị vòng xoay Loading (Để người dùng biết hệ thống đang AI xử lý)
        loading_dlg = ft.AlertDialog(
            content=ft.Row([
                ft.ProgressRing(),
                ft.Container(content=ft.Text(" Đang nhận diện AI..."), padding=10)
            ], tight=True),
            modal=True
        )
        self.page.overlay.append(loading_dlg)
        loading_dlg.open = True
        self.page.update()

        # Lấy nguồn ảnh
        front_source = self.images.get("Front photo")
        back_source = self.images.get("Back photo")

        # 3. Chạy OCR (Nên chạy trong một thread để không treo UI nếu hàm này đồng bộ)
        from Backend.Helpers import Check_front_driving_license, Check_back_driving_license

        # Giả sử hàm này tốn 2-5 giây
        front_data = Check_front_driving_license(front_source)

        # Tắt loading trước khi hiện thông báo lỗi hoặc chuyển trang
        loading_dlg.open = False
        self.page.update()

        # 4. Kiểm tra kết quả mặt trước
        license_no = front_data.get("license_no")
        if not license_no or len(str(license_no)) != 12:
            self.show_message("Lỗi OCR", "Không nhận diện được Số GPLX (12 số). Hãy chụp lại ảnh rõ nét!")
            return

        license_class = front_data.get("license_class")
        if not license_class:
            self.show_message("Lỗi OCR", "Không nhận diện được Hạng GPLX. Hãy chụp lại ảnh rõ nét!")
            return

        # 5. Kiểm tra mặt sau
        if not Check_back_driving_license(back_source):
            self.show_message("Lỗi xác thực", "Ảnh mặt sau không hợp lệ hoặc thiếu phôi PET!")
            return
        current_data = self.page.session.store.get("temp_data1")
        if self.page:
            if not current_data:
                self.show_message("Lỗi", "Không tìm thấy thông tin từ bước trước!")
                self.page.go("/Register")
                return

            new_info ={
                "license_no": license_no,
                "license_class": license_class,
                "front_img": front_source,
                "back_img": back_source
            }
            current_data.update(new_info)
            self.page.session.store.set("temp_data2", current_data)
            print(f"Dữ liệu tổng hợp sau Step 2: {current_data}")
            self.page.go("/Register3")

    def show_message(self, title, msg):
        dlg = ft.AlertDialog(title=ft.Text(title), content=ft.Text(msg))
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()


async def main(page: ft.Page):

    page.views.append(RegisterScreen2(page))
    page.update()

if __name__ == "__main__":
    ft.run(main)
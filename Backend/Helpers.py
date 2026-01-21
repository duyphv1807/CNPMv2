import random
import string
import cv2
import easyocr
import numpy as np
import torch
from Backend.ExcuteDatabase import supabase
import re

def generate_id(prefix: str, length: int = 10):
    """
    Tạo mã ID ngẫu nhiên có độ dài cố định.
    Ví dụ: BK + 8 ký tự ngẫu nhiên = 10 ký tự.
    """
    prefix = prefix.upper()
    if len(prefix) >= length:
        return prefix[:length]  # Trường hợp prefix quá dài (hiếm gặp)

    # Tính số ký tự cần tạo thêm
    random_length = length - len(prefix)

    # Tạo chuỗi ngẫu nhiên gồm chữ in hoa và số
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=random_length))

    return f"{prefix}{random_part}"

_reader = None
def get_reader():
    global _reader
    if _reader is None:
        print("--> [SYSTEM] Đang khởi tạo EasyOCR lần đầu...")
        # Chỉ khi hàm này được gọi, Reader mới thực sự chạy
        _reader = easyocr.Reader(['vi', 'en'], gpu=True)
    return _reader

def load_image_flexible(source):
    """
    Hàm bổ trợ: Chấp nhận source là path (str) hoặc numpy array (image)
    """
    if isinstance(source, str):
        # Nếu là đường dẫn, dùng imread
        # Sử dụng imdecode để tránh lỗi đường dẫn có ký tự tiếng Việt/Windows
        try:
            nparr = np.fromfile(source, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        except Exception:
            return None
    elif isinstance(source, np.ndarray):
        # Nếu đã là mảng numpy (từ Camera), dùng luôn
        img = source.copy()
    else:
        return None
    return img
def extract_license_class(source):
    reader = get_reader()
    """Trích xuất hạng bằng lái (A1, B2, C...)"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    img = load_image_flexible(source)
    if img is None: return None

    # 1. Chuẩn hóa hướng ảnh (Giống hàm No.)
    h, w = img.shape[:2]
    if h > w:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        h, w = img.shape[:2]

    results_check = reader.readtext(img, paragraph=True)
    is_correct = False
    for (_, text) in results_check:
        if any(key in text.upper() for key in ["HANG", "CLASS", "HẠNG"]):
            is_correct = True
            break
    if not is_correct:
        img = cv2.rotate(img, cv2.ROTATE_180)

    # 2. Cắt vùng Hạng (ROI) - Góc dưới cùng bên trái
    h, w = img.shape[:2]
    roi_raw = img[int(h * 0.65):int(h * 0.98), int(w * 0.01):int(w * 0.48)]

    # Tạo 2 phiên bản: Màu phóng to và Đen trắng sắc nét
    roi_color = cv2.resize(roi_raw, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)
    gray = cv2.cvtColor(roi_color, cv2.COLOR_BGR2GRAY)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    roi_binary = cv2.adaptiveThreshold(sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

    # 3. OCR và xử lý logic hạng
    valid_classes = ["A1", "A2", "B1", "B2", "C", "D", "E", "FE", "FD"]
    fuzzy_map = {
        "AC": "A1", "A|": "A1", "41": "A1", "AI": "A1", "AL": "A1",
        "BEC3": "B1", "BE1": "B1", "B3": "B1", "B1": "B1",
        "82": "B2", "32": "B2", "BZ": "B2", "B2": "B2",
        "EC": "C", "CC": "C", "C1": "C", "D1": "D", "EE": "E"
    }

    for i, img_input in enumerate([roi_color, roi_binary]):
        results = reader.readtext(img_input, allowlist='0123456789ABCDE ')
        for (_, text, prob) in results:
            clean_text = "".join([c for c in text.upper() if c.isalnum()])
            if not clean_text: continue

            # Kiểm tra Map trước
            if clean_text in fuzzy_map:
                return fuzzy_map[clean_text]

            # Kiểm tra chứa hạng
            for vc in sorted(valid_classes, key=len, reverse=True):
                if vc in clean_text:
                    if vc in ["C", "E"] and len(clean_text) > 2: continue
                    return vc
    return None

def extract_license_no(image_path):
    reader = get_reader()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    img = load_image_flexible(image_path)
    if img is None:
        print(f"--> [ERROR] Không thể đọc ảnh từ: {image_path}")
        return None

    # 1. CHUẨN HÓA HƯỚNG
    h, w = img.shape[:2]
    if h > w:
        img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        h, w = img.shape[:2]

    # Kiểm tra xoay 180 độ
    results_check = reader.readtext(img, paragraph=True)
    is_correct = any(
        key in text.upper() for (_, text) in results_check for key in ["HANG", "CLASS", "HẠNG", "SO/NO", "GIẤY PHÉP"])
    if not is_correct:
        img = cv2.rotate(img, cv2.ROTATE_180)

    # 2. CROP SÂU (Mở rộng tọa độ một chút để tránh mất số)
    h, w = img.shape[:2]
    y_start, y_end = int(h * 0.25), int(h * 0.36)
    x_start, x_end = int(w * 0.60), int(w * 0.97)
    roi = img[y_start:y_end, x_start:x_end]

    if roi.size == 0: return None

    roi = cv2.resize(roi, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    gray_orig = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # --- 4. KHỞI TẠO BIẾN LƯU KẾT QUẢ TỐT NHẤT ---
    best_final_str = ""
    max_total_score = -9999

    # Thử nghiệm các mức Threshold khác nhau để đối phó với ánh sáng lóa
    threshold_steps = [0, 140, 150, 170]
    #threshold_steps = [0]  # 0 là Otsu tự động

    for th_val in threshold_steps:
        # Tiền xử lý
        gray = cv2.bilateralFilter(gray_orig, 5, 15, 15)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)

        if th_val == 0:
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            _, binary = cv2.threshold(gray, th_val, 255, cv2.THRESH_BINARY_INV)

        # A. Làm sạch nhiễu hạt
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

        # B. Bảo vệ số 1 bằng kernel dọc (tránh tạo thanh ngang làm nhầm sang số 4)
        v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
        mask = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, v_kernel)

        # C. Gọt mảnh (Erosion) để tách các số bị dính bụng (3-5)
        mask = cv2.erode(mask, np.ones((2, 2), np.uint8), iterations=1)

        # OCR
        final_img = cv2.bitwise_not(mask)
        # allowlist chỉ cho phép các ký tự số để tránh AI đoán ra chữ cái
        results = reader.readtext(final_img, allowlist='0123456789')
        results = sorted(results, key=lambda x: x[0][0][0])

        current_digits = []
        sum_prob = 0
        for res in results:
            bbox, text, prob = res
            w_box = bbox[1][0] - bbox[0][0]
            h_box = bbox[2][1] - bbox[0][1]
            char_count = len(text) if len(text) > 0 else 1
            ratio = (w_box / char_count) / float(h_box) if h_box != 0 else 0

            for char in text:
                char = char.upper()

                # --- LOGIC RATIO (CHỐNG NHẦM 1-4, 3-5) ---
                if char in ['1', '4']:
                    # Ratio > 0.35 thường là số 4 có chân ngang
                    char = '4' if ratio > 0.4 else '1'
                elif char == '3':
                    if ratio > 0.50 and prob < 0.92: char = '5'
                elif char == '5':
                    if ratio < 0.38: char = '3'
                elif char == '8' and ratio < 0.35:
                    char = '3'

                if char.isdigit():
                    current_digits.append(char)
                    sum_prob += prob

        raw_res = "".join(current_digits)
        if not raw_res: continue

        # --- 4. HẬU XỬ LÝ & CHẤM ĐIỂM ---
        potential_nums = re.findall(r'\d+', raw_res)
        if not potential_nums: continue

        # Chọn cụm số dài nhất (thường là dãy 12 số của GPLX)
        candidate = max(potential_nums, key=len)

        # Nếu cụm dính rác, lấy 12 số cuối
        if len(candidate) > 12:
            candidate = candidate[-12:]

        avg_p = sum_prob / len(current_digits) if len(current_digits) > 0 else 0
        score = avg_p * 100

        # Ưu tiên chuỗi 12 ký tự
        if len(candidate) == 12:
            score += 2000
            # Kiểm tra mã tỉnh Việt Nam (001 -> 096)
            try:
                ma_tinh = int(candidate[:3])
                if 1 <= ma_tinh <= 96:
                    score += 1000
                else:
                    score -= 1500
            except ValueError:
                pass
        else:
            score += (len(candidate) * 20)

        # Lưu kết quả tốt nhất qua các vòng lặp
        if score > max_total_score:
            max_total_score = score
            best_final_str = candidate

        # Thoát sớm nếu kết quả đã quá chuẩn (đúng mã tỉnh + đủ 12 số)
        if len(candidate) == 12 and 1 <= int(candidate[:3]) <= 96 and avg_p > 0.88:
            break

    print(f"--> [DEBUG] Max Score: {max_total_score:.2f}")
    print(f"--> [FINAL RESULT] GPLX No: {best_final_str}")

    return best_final_str

def Check_front_driving_license(image_path):
    # 1. Khởi tạo kết quả
    final_data = {
        "license_no": None,
        "license_class": None
    }

    # 2. Chạy nhận diện No (Số GPLX)
    # Hàm này bên trong đã có bước chuẩn hóa hướng ảnh
    no_result = extract_license_no(image_path)

    # 3. Chạy nhận diện Class (Hạng)
    # Hàm này cũng có bước chuẩn hóa hướng tương tự
    class_result = extract_license_class(image_path)

    # 4. LOGIC KIỂM TRA CHÉO
    # Nếu No ra mà Class không ra (hoặc ngược lại), có thể vùng Crop bị lệch
    # hoặc hướng ảnh đang bị hiểu sai giữa 2 hàm.
    if no_result and not class_result:
        print("Tìm thấy No nhưng thiếu Class, đang thử quét Class ở hướng ngược lại...")
        # Bạn có thể gọi một hàm extract_class với mode 'force_rotate' tại đây

    if class_result and not no_result:
        print("Tìm thấy Class nhưng thiếu No, đang tái cấu trúc vùng quét No...")

    final_data["license_no"] = no_result
    final_data["license_class"] = class_result

    no = final_data.get("license_no")
    cls = final_data.get("license_class")

    # Kiểm tra điều kiện
    if no and len(str(no)) == 12:
        if cls:
            print(f"--- THÀNH CÔNG RỰC RỠ: Số={no}, Hạng={cls} ---")
        else:
            # Trường hợp lấy được số định danh làm ID nhưng Class bị mờ
            print(f"--- CẢNH BÁO: Có Số ({no}) nhưng chưa có Hạng (None) ---")
            # Hướng xử lý: Có thể cho phép User nhập tay Hạng vì đã có ID chuẩn
    elif no:
        # Trường hợp có số nhưng không đủ 12 chữ số (đang bị 11/12)
        print(f"--- CHƯA ĐỦ: Tìm thấy chuỗi số '{no}' nhưng chỉ dài {len(str(no))} ký tự ---")
    else:
        # Trường hợp No hoàn toàn là None
        print("--- THẤT BẠI: Không tìm thấy bất kỳ dãy số No. nào trên ảnh ---")

    return final_data


def Check_back_driving_license(source):
    # 1. Sử dụng hàm bổ trợ để lấy dữ liệu ảnh (img luôn là numpy array sau bước này)
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    img = load_image_flexible(source)

    if img is None:
        print(f"--> [ERROR] Không thể load ảnh từ nguồn: {source}")
        return False

    # 2. Lấy kích thước ảnh (Lúc này img chắc chắn có thuộc tính .shape)
    h, w = img.shape[:2]
    total_area = h * w

    # 3. KIỂM TRA DẤU MỘC ĐỎ
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Dải màu đỏ (bao gồm cả vùng bắt đầu và vùng kết thúc của trục H)
    lower_red1, upper_red1 = np.array([0, 70, 50]), np.array([10, 255, 255])
    lower_red2, upper_red2 = np.array([160, 70, 50]), np.array([180, 255, 255])

    mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
    # Khử nhiễu để tránh các hạt bụi đỏ li ti
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    red_ratio = cv2.countNonZero(mask) / total_area

    # 4. KIỂM TRA ĐƯỜNG KẺ BẢNG (Canny + HoughLinesP)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    # Tìm đường thẳng dài tối thiểu bằng 1/10 chiều rộng ảnh
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80,
                            minLineLength=w // 10, maxLineGap=10)
    line_count = len(lines) if lines is not None else 0

    # 5. LOGIC QUYẾT ĐỊNH
    # Một ảnh mặt sau điển hình sẽ có mộc đỏ và các đường kẻ bảng hạng xe
    print(f"--> [DEBUG] Red Ratio: {red_ratio:.6f} | Lines Found: {line_count}")

    is_back = (red_ratio > 0.0005) or (red_ratio > 0.0002 and line_count > 5)

    return is_back


def save_driving_license_data(license_id, front_source, back_source, license_class):
    """
    1. Upload ảnh lên Storage
    2. Insert dữ liệu vào bảng 'DrivingLicense'
    """
    file_data = None
    try:
        bucket_name = "DrivingLicense"
        urls = {"front": "", "back": ""}

        # --- BƯỚC 1: UPLOAD ẢNH ---
        for side, source in [("front", front_source), ("back", back_source)]:
            if source is None: continue

            # Chuyển đổi sang bytes
            if isinstance(source, np.ndarray):
                _, buffer = cv2.imencode('.jpg', source)
                file_data = buffer.tobytes()
            else:
                with open(source, 'rb') as f:
                    file_data = f.read()

            # Upload (Sử dụng LicenseID làm tên thư mục để quản lý)
            storage_path = f"{license_id}/{side}.jpg"
            supabase.storage.from_(bucket_name).upload(
                path=storage_path,
                file=file_data,
                file_options={"content-type": "image/jpeg", "upsert": "true"}
            )

            # Lấy Public URL
            urls[side] = supabase.storage.from_(bucket_name).get_public_url(storage_path)

        # --- BƯỚC 2: INSERT VÀO TABLE 'DrivingLicense' ---
        license_payload = {
            "DrivingLicenseID": license_id,
            "FrontImage": urls["front"],
            "BackImage": urls["back"],
            "Class": license_class
        }

        response = supabase.table("DrivingLicense").insert(license_payload).execute()
        return response

    except Exception as e:
        print(f"--> [ERROR] Save Driving License failed: {e}")
        return None

def upload_image_to_storage(image_source, filename, bucket="DrivingLicense"):
    """
    Đẩy ảnh lên Supabase Storage và trả về Public URL.
    """
    file_data = None
    try:
        if image_source is None: return None

        # Chuyển đổi sang bytes
        if isinstance(image_source, np.ndarray):
            import cv2
            _, buffer = cv2.imencode('.jpg', image_source)
            file_data = buffer.tobytes()
        elif isinstance(image_source, str):
            with open(image_source, 'rb') as f:
                file_data = f.read()

        # Trường hợp 3: Byte data trực tiếp
        else:
            file_data = image_source

        storage_path = f"{filename}.jpg"

        # Upload lên bucket được chỉ định
        supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=file_data,
            file_options={"content-type": "image/jpeg", "upsert": "true"}
        )

        return supabase.storage.from_(bucket).get_public_url(storage_path)
    except Exception as e:
        print(f"Lỗi upload: {e}")
        return None

if __name__ == "__main__":
    path = r"C:\Users\ASUS\OneDrive\Máy tính\bài tập\test\a1.jpg"
    path1 = r"C:\Users\ASUS\OneDrive\Máy tính\bài tập\test\back.jpg"
    Check_back_driving_license(path1)



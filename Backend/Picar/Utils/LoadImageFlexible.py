import cv2
import numpy as np

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
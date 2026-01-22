import string
import random

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
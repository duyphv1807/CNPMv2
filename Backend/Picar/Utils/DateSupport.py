from datetime import datetime

class DateHelper:
    @staticmethod
    def parse_and_validate(start_str, end_str):
        """
        Chuyển đổi chuỗi từ Frontend sang Object Datetime và kiểm tra sơ bộ
        """
        fmt = "%d/%m/%Y %H:%M"
        try:
            start = datetime.strptime(start_str, fmt)
            end = datetime.strptime(end_str, fmt)

            # Kiểm tra logic: Ngày trả phải sau ngày nhận
            if end <= start:
                return None, None, "Ngày trả phải sau ngày nhận."

            return start, end, None
        except ValueError:
            return None, None, "Định dạng ngày giờ không hợp lệ."

    @staticmethod
    def calculate_rental_days(start, end):
        """
        Tính số ngày thuê để nhân với đơn giá
        """
        delta = end - start
        # Làm tròn lên: nếu quá 1 giờ vẫn tính thêm 1 ngày (tùy chính sách của bạn)
        days = delta.days
        if delta.seconds > 3600:  # Hơn 1 tiếng tính thêm 1 ngày
            days += 1
        return max(1, days)
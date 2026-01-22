from flask import Flask
from flask_cors import CORS

# 1. Khởi tạo ứng dụng Flask
app = Flask(__name__)

# 2. Cấu hình CORS để Flet có thể gọi API mà không bị chặn
CORS(app)

# 3. IMPORT ROUTES (Phải đặt ở cuối để tránh lỗi vòng lặp import)
from . import Routes
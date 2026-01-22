from Backend.Picar import app # Import đối tượng app đã khởi tạo trong Picar/__init__.py
import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    local_ip = get_local_ip()
    print("-" * 50)
    print(f" SERVER ĐANG CHẠY TRONG MẠNG NỘI BỘ")
    print(f" Gửi link này cho Team: http://{local_ip}:5000/api")
    print("-" * 50)

    app.run(host='0.0.0.0', port=5000, debug=True)
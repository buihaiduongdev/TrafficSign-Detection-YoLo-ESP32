import socket
import time

class SoundSender:
    def __init__(self, esp8266_ip, port=4210):
        self.ip = esp8266_ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # BẢNG ÁNH XẠ ĐẦY ĐỦ 56 BIỂN BÁO
        # Key: Tên Class từ YOLO -> Value: Số thứ tự bài hát (Track ID)
        self.mapping = {
            # --- KHÁC ---
            'DP-135': 1,    # Đường ưu tiên
            
            # --- NHÓM CẤM (PROHIBITION) ---
            'P-102': 2,     # Cấm đi ngược chiều
            'P-103a': 3,    # Cấm xe ô tô
            'P-103b': 4,    # Cấm xe ô tô rẽ phải
            'P-103c': 5,    # Cấm xe ô tô rẽ trái
            'P-104': 6,     # Cấm xe máy
            'P-106a': 7,    # Cấm xe tải
            'P-106b': 8,    # Cấm xe tải trên 3.5 tấn
            'P-107a': 9,    # Cấm xe khách
            'P-112': 10,    # Cấm người đi bộ
            'P-115': 11,    # Hạn chế trọng tải
            'P-117': 12,    # Hạn chế chiều cao
            'P-123a': 13,   # Cấm rẽ trái
            'P-123b': 14,   # Cấm rẽ phải
            'P-124a': 15,   # Cấm quay đầu
            'P-124b': 16,   # Cấm ô tô quay đầu
            'P-124c': 17,   # Cấm rẽ trái và quay đầu
            'P-127': 18,    # Giới hạn tốc độ 50
            'P-128': 19,    # Giới hạn tốc độ 60
            'P-130': 20,    # Cấm dừng và đỗ xe
            'P-131a': 21,   # Cấm dừng và đỗ xe (Cấm đỗ)
            'P-137': 22,    # Hết hạn chế
            'P-245a': 23,   # Cấm đỗ xe hai phía

            # --- NHÓM HIỆU LỆNH (MANDATORY) ---
            'R-301c': 24,   # Đi thẳng và rẽ phải
            'R-301d': 25,   # Đi thẳng và rẽ trái
            'R-301e': 26,   # Rẽ phải
            'R-302a': 27,   # Rẽ phải hoặc đi thẳng
            'R-302b': 28,   # Rẽ trái hoặc đi thẳng
            'R-303': 29,    # Đi thẳng
            'R-407a': 30,   # Hướng đi thẳng phải theo
            'R-409': 31,    # Hướng đi thẳng (Chỗ quay xe)
            'R-425': 32,    # Hướng rẽ phải
            'R-434': 33,    # Hướng rẽ trái
            'S-509a': 34,   # Đường cấm xe tải

            # --- NHÓM CẢNH BÁO (WARNING) ---
            'W-201a': 35,   # Chỗ ngoặt nguy hiểm bên trái
            'W-201b': 36,   # Chỗ ngoặt nguy hiểm bên phải
            'W-202a': 37,   # Đường cong vòng trái
            'W-202b': 38,   # Đường cong vòng phải
            'W-203b': 39,   # Đường bị thu hẹp bên phải
            'W-203c': 40,   # Đường bị thu hẹp bên trái
            'W-205a': 41,   # Đường giao nhau
            'W-205b': 42,   # Đường giao nhau kế tiếp
            'W-205d': 43,   # Đường giao nhau chữ T
            'W-207a': 44,   # Giao với đường không ưu tiên
            'W-207b': 45,   # Giao với đường không ưu tiên bên phải
            'W-207c': 46,   # Giao với đường không ưu tiên bên trái
            'W-208': 47,    # Giao nhau với đường ưu tiên
            'W-209': 48,    # Giao nhau có tín hiệu đèn
            'W-210': 49,    # Giao nhau với đường sắt có rào chắn
            'W-219': 50,    # Chú ý dốc xuống
            'W-224': 51,    # Chú ý đường trơn (người đi bộ cắt ngang)
            'W-225': 52,    # Chú ý: Trẻ em
            'W-227': 53,    # Chú ý đường hẹp (Công trường)
            'W-233': 54,    # Chú ý chướng ngại vật
            'W-235': 55,    # Chú ý chướng ngại vật
            'W-245a': 56    # Chú ý công trường (Đi chậm)
        }
        print(f"🔊 SoundSender initialized. Target: {self.ip}:{self.port}")

    def play_sound(self, class_name):
        # Tìm ID bài hát tương ứng
        track_id = self.mapping.get(class_name, 0)
        
        if track_id > 0:
            try:
                message = str(track_id).encode('utf-8')
                self.sock.sendto(message, (self.ip, self.port))
                print(f"Sent UDP command: Play track {track_id} ({class_name})")
            except Exception as e:
                print(f"UDP Error: {e}")
        else:
            print(f"No audio mapping for: {class_name}")
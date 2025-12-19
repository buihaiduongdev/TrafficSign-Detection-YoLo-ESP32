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
            'DP-135': 1,    # Hết tất cả các lệnh cấm

            # --- NHÓM CẤM (PROHIBITION) ---
            'P-102': 2,     # Cấm đi ngược chiều
            'P-103a': 3,    # Cấm xe ô tô
            'P-103b': 4,    # Cấm xe ô tô rẽ phải
            'P-103c': 5,    # Cấm xe ô tô rẽ trái
            'P-104': 6,     # Cấm xe máy
            'P-106a': 7,    # Cấm xe ô tô tải
            'P-106b': 8,    # Cấm xe tải (theo khối lượng)
            'P-107a': 9,    # Cấm xe khách và xe tải
            'P-112': 10,    # Cấm người đi bộ
            'P-115': 11,    # Hạn chế tải trọng toàn bộ xe
            'P-117': 12,    # Hạn chế chiều cao
            'P-123a': 13,   # Cấm rẽ trái
            'P-123b': 14,   # Cấm rẽ phải
            'P-124a': 15,   # Cấm quay đầu xe
            'P-124b': 16,   # Cấm ô tô quay đầu xe
            'P-124c': 17,   # Cấm rẽ trái và quay đầu xe
            'P-127': 18,    # Tốc độ tối đa cho phép (50km/h)
            'P-128': 19,    # Tốc độ tối đa cho phép (60km/h)
            'P-130': 20,    # Cấm dừng xe và đỗ xe
            'P-131a': 21,   # Cấm đỗ xe
            'P-137': 22,    # Cấm rẽ trái và rẽ phải
            'P-245a': 23,   # Đi chậm

            # --- NHÓM HIỆU LỆNH (MANDATORY) ---
            'R-301c': 24,   # Các xe chỉ được rẽ trái (Sau ngã 3,4)
            'R-301d': 25,   # Các xe chỉ được rẽ phải (Sau ngã 3,4)
            'R-301e': 26,   # Các xe chỉ được rẽ trái (Trước ngã 3,4)
            'R-302a': 27,   # Hướng phải đi vòng chướng ngại vật (sang phải)
            'R-302b': 28,   # Hướng phải đi vòng chướng ngại vật (sang trái)
            'R-303': 29,    # Nơi giao nhau chạy theo vòng xuyến
            'R-407a': 30,   # Đường một chiều
            'R-409': 31,    # Chỗ quay xe
            'R-425': 32,    # Cầu vượt qua đường cho người đi bộ
            'R-434': 33,    # Bến xe buýt
            'S-509a': 34,   # Biển phụ: Thuyết minh biển chính

            # --- NHÓM CẢNH BÁO (WARNING) ---
            'W-201a': 35,   # Chỗ ngoặt nguy hiểm vòng bên trái
            'W-201b': 36,   # Chỗ ngoặt nguy hiểm vòng bên phải
            'W-202a': 37,   # Nhiều chỗ ngoặt nguy hiểm (vòng trái)
            'W-202b': 38,   # Nhiều chỗ ngoặt nguy hiểm (vòng phải)
            'W-203b': 39,   # Đường bị thu hẹp về phía trái
            'W-203c': 40,   # Đường bị thu hẹp về phía phải
            'W-205a': 41,   # Đường giao nhau cùng cấp (Ngã tư)
            'W-205b': 42,   # Đường giao nhau cùng cấp (Ngã ba)
            'W-205d': 43,   # Đường giao nhau cùng cấp (Ngã ba)
            'W-207a': 44,   # Giao nhau với đường không ưu tiên
            'W-207b': 45,   # Giao nhau với đường không ưu tiên (bên phải)
            'W-207c': 46,   # Giao nhau với đường không ưu tiên (bên trái)
            'W-208': 47,    # Giao nhau với đường ưu tiên
            'W-209': 48,    # Giao nhau có tín hiệu đèn
            'W-210': 49,    # Giao nhau với đường sắt có rào chắn
            'W-219': 50,    # Dốc xuống nguy hiểm
            'W-224': 51,    # Đường người đi bộ cắt ngang
            'W-225': 52,    # Cảnh báo khu vực có trẻ em qua lại
            'W-227': 53,    # Công trường
            'W-233': 54,    # Nguy hiểm khác
            'W-235': 55,    # Chú ý ngừoi qua đường
            'W-245a': 56    # Đi chậm
        }
        print(f"SoundSender initialized. Target: {self.ip}:{self.port}")

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
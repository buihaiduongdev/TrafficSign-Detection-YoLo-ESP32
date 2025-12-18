from enum import Enum
from datetime import datetime


class AlertLevel(Enum):
    """Mức độ cảnh báo"""
    CRITICAL = " CRITICAL"     # Cấm, buộc phải
    WARNING = " WARNING"        # Cảnh báo tốc độ
    INFO = " INFO"              # Thông tin
    NONE = " NONE"              # Không có cảnh báo


class DecisionLogic:
    """
    Logic quyết định cảnh báo cho hệ thống hỗ trợ lái xe
    
    Quy tắc:
    1. Kiểm tra độ tin cậy (confidence >= 0.5)
    2. Kiểm tra khoảng cách (distance < warning_distance)
    3. Kiểm tra tốc độ (nếu là biển báo tốc độ)
    4. Quyết định cảnh báo và lệnh TTSc
    """
    
    def __init__(self, estimated_speed=50):
        self.estimated_speed = estimated_speed
        self.alert_cooldown = 3.0
        self.thresholds = {
            #  BIỂN BÁO GIỚI HẠN TỐC ĐỘ 
            'P-127': {
                'type': 'SPEED_LIMIT',
                'limit_speed': 50,
                'warning_distance': 40,
                'description': 'Giới hạn tốc độ 50'
            },
            'P-128': {
                'type': 'SPEED_LIMIT',
                'limit_speed': 60,
                'warning_distance': 40,
                'description': 'Giới hạn tốc độ 60'
            },
            
            # BIỂN BÁO CẤM 
            'P-102': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm đi ngược chiều'
            },
            'P-103a': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm dừng xe'
            },
            'P-103b': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm dừng xe'
            },
            'P-103c': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm dừng xe'
            },
            'P-104': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm đỗ xe'
            },
            'P-106a': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm vượt'
            },
            'P-106b': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm vượt'
            },
            'P-107a': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm vượt xe tải'
            },
            'P-112': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm rẽ trái'
            },
            'P-115': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm rẽ phải'
            },
            'P-117': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm quay đầu'
            },
            'P-123a': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm đi vào'
            },
            'P-123b': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm đi vào'
            },
            'P-124a': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm ô tô đi vào'
            },
            'P-124b': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm ô tô đi vào'
            },
            'P-124c': {
                'type': 'PROHIBITION',
                'warning_distance': 30,
                'description': 'Cấm ô tô đi vào'
            },
            'P-130': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm dừng và đỗ xe'
            },
            'P-131a': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm dừng và đỗ xe'
            },
            'P-245a': {
                'type': 'PROHIBITION',
                'warning_distance': 20,
                'description': 'Cấm đỗ xe hai phía'
            },
            
            #  BIỂN BÁO BẮT BUỘC 
            'R-301c': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Đi thẳng và rẽ phải'
            },
            'R-301d': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Đi thẳng và rẽ trái'
            },
            'R-301e': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Rẽ phải'
            },
            'R-302a': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Rẽ phải hoặc đi thẳng'
            },
            'R-302b': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Rẽ trái hoặc đi thẳng'
            },
            'R-303': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Đi thẳng'
            },
            'R-407a': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Hướng đi thẳng phải theo'
            },
            'R-409': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Hướng đi thẳng'
            },
            'R-425': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Hướng rẽ phải'
            },
            'R-434': {
                'type': 'MANDATORY',
                'warning_distance': 20,
                'description': 'Hướng rẽ trái'
            },
            
            #  BIỂN BÁO CẢNH BÁO 
            'W-201a': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Đường cong vòng trái'
            },
            'W-201b': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Đường cong vòng phải'
            },
            'W-202a': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Đường cong vòng trái'
            },
            'W-202b': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Đường cong vòng phải'
            },
            'W-203b': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Đường giao nhau'
            },
            'W-203c': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Đường giao nhau'
            },
            'W-205a': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Giao nhau với đường ưu tiên'
            },
            'W-205b': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Giao nhau với đường ưu tiên'
            },
            'W-205d': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Giao nhau với đường ưu tiên'
            },
            'W-207a': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Giao nhau với đường không ưu tiên'
            },
            'W-207b': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Giao nhau với đường không ưu tiên'
            },
            'W-207c': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Giao nhau với đường không ưu tiên'
            },
            'W-208': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Giao nhau với đường sắt'
            },
            'W-209': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Giao nhau với đường sắt'
            },
            'W-210': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Giao nhau với đường sắt'
            },
            'W-219': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Chú ý dốc xuống'
            },
            'W-224': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Chú ý đường trơn'
            },
            'W-225': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Chú ý: Trẻ em'
            },
            'W-227': {
                'type': 'WARNING_SIGN',
                'warning_distance': 40,
                'description': 'Chú ý đường hẹp'
            },
            'W-233': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Chú ý chướng ngại vật'
            },
            'W-235': {
                'type': 'WARNING_SIGN',
                'warning_distance': 50,
                'description': 'Chú ý chướng ngại vật'
            },
            'W-245a': {
                'type': 'WARNING_SIGN',
                'warning_distance': 60,
                'description': 'Chú ý công trường'
            },
            
            #  BIỂN BÁO THÔNG TIN 
            'DP-135': {
                'type': 'INFO',
                'warning_distance': 30,
                'description': 'Đường ưu tiên'
            },
            'P-137': {
                'type': 'INFO',
                'warning_distance': 20,
                'description': 'Hết hạn chế'
            },
            'S-509a': {
                'type': 'INFO',
                'warning_distance': 30,
                'description': 'Đường cấm xe tải'
            },
        }   
        # Mapping lệnh TTS
        self.commands = {
            'SPEEDING_50': 'CMD_50_SPEEDING',
            'SPEEDING_60': 'CMD_60_SPEEDING',
            'NO_LEFT_TURN': 'CMD_NO_LEFT_TURN',
            'NO_RIGHT_TURN': 'CMD_NO_RIGHT_TURN',
            'NO_U_TURN': 'CMD_NO_U_TURN',
            'NO_PARKING': 'CMD_NO_PARKING',
            'NO_STOPPING': 'CMD_NO_STOPPING',
            'NO_REVERSE': 'CMD_NO_REVERSE',
            'NO_ENTRY': 'CMD_NO_ENTRY',
            'NO_OVERTAKING': 'CMD_NO_OVERTAKING',
            'MANDATORY_STRAIGHT': 'CMD_MANDATORY_STRAIGHT',
            'MANDATORY_RIGHT': 'CMD_MANDATORY_RIGHT',
            'MANDATORY_LEFT': 'CMD_MANDATORY_LEFT',
            'CHILDREN_ZONE': 'CMD_CHILDREN_ZONE',
            'RAILROAD_CROSSING': 'CMD_RAILROAD_CROSSING',
            'OBSTACLE': 'CMD_OBSTACLE',
            'CURVE_LEFT': 'CMD_CURVE_LEFT',
            'CURVE_RIGHT': 'CMD_CURVE_RIGHT',
            'INTERSECTION': 'CMD_INTERSECTION',
            'SLIPPERY_ROAD': 'CMD_SLIPPERY_ROAD',
            'STEEP_DESCENT': 'CMD_STEEP_DESCENT',
            'NARROW_ROAD': 'CMD_NARROW_ROAD',
            'CONSTRUCTION': 'CMD_CONSTRUCTION',
        }
        
        self.last_alert_time = {}  
        
        print(f"   DecisionLogic initialized")
        print(f"   Estimated speed: {self.estimated_speed} km/h")
        print(f"   Supported signs: {len(self.thresholds)}")
        print(f"   Alert cooldown: {self.alert_cooldown}s")
    
    def decide(self, class_name, distance, confidence):
        """
        Quyết định cảnh báo cần phát
        
        Args:
            class_name (str): Tên class YOLO (P-127, P-112, ...)
            distance (float): Khoảng cách ước tính (mét)
            confidence (float): Độ tin cậy YOLO (0-1)
            
        Returns:
            tuple: (command, message, alert_level)
                - command: TTS command cần gửi (hoặc None)
                - message: Thông điệp cảnh báo chi tiết
                - alert_level: AlertLevel enum
        """  
        # 1. Kiểm tra độ tin cậy
        if confidence < 0.5:
            return None, "", AlertLevel.NONE

        if class_name not in self.thresholds:
            return None, "", AlertLevel.NONE
        
        threshold = self.thresholds[class_name]
        warning_dist = threshold['warning_distance']
        sign_type = threshold['type']
        description = threshold['description']
        
        # 2. Kiểm tra khoảng cách
        if distance > warning_dist:
            return None, "", AlertLevel.NONE

        current_time = datetime.now()
        if class_name in self.last_alert_time:
            elapsed = (current_time - self.last_alert_time[class_name]).total_seconds()
            if elapsed < self.alert_cooldown:
                return None, "", AlertLevel.NONE
        timestamp = current_time.isoformat()
        command = None
        message = ""
        alert_level = AlertLevel.NONE
        
        #  BIỂN BÁO GIỚI HẠN TỐC ĐỘ 
        if sign_type == 'SPEED_LIMIT':
            limit_speed = threshold['limit_speed']
            
            if self.estimated_speed > limit_speed:
                speeding_amount = self.estimated_speed - limit_speed
                
                if limit_speed == 50:
                    command = self.commands['SPEEDING_50']
                elif limit_speed == 60:
                    command = self.commands['SPEEDING_60']
                
                message = (
                    f"   CẢNH BÁO TỐC ĐỘ\n"
                    f"   Biển báo: {description}\n"
                    f"   Khoảng cách: {distance:.1f}m\n"
                    f"   Giới hạn: {limit_speed} km/h\n"
                    f"   Tốc độ hiện tại: {self.estimated_speed} km/h\n"
                    f"   Vượt quá: {speeding_amount:.1f} km/h"
                )
                
                alert_level = AlertLevel.WARNING
        
        #  BIỂN BÁO CẤM 
        elif sign_type == 'PROHIBITION':
            prohibition_commands = {
                'P-112': 'NO_LEFT_TURN',
                'P-115': 'NO_RIGHT_TURN',
                'P-117': 'NO_U_TURN',
                'P-130': 'NO_PARKING',
                'P-131a': 'NO_PARKING',
                'P-103a': 'NO_STOPPING',
                'P-103b': 'NO_STOPPING',
                'P-103c': 'NO_STOPPING',
                'P-104': 'NO_PARKING',
                'P-102': 'NO_REVERSE',
                'P-123a': 'NO_ENTRY',
                'P-123b': 'NO_ENTRY',
                'P-124a': 'NO_ENTRY',
                'P-124b': 'NO_ENTRY',
                'P-124c': 'NO_ENTRY',
                'P-106a': 'NO_OVERTAKING',
                'P-106b': 'NO_OVERTAKING',
                'P-107a': 'NO_OVERTAKING',
                'P-245a': 'NO_PARKING',
            }
            
            cmd_key = prohibition_commands.get(class_name)
            if cmd_key:
                command = self.commands.get(cmd_key)
            
            message = (
                f"   CẢNH BÁO: BIỂN CẤM\n"
                f"   Biển báo: {description}\n"
                f"   Khoảng cách: {distance:.1f}m\n"
                f"   Hành động: {description.lower()}"
            )
            
            alert_level = AlertLevel.CRITICAL
        
        #  BIỂN BÁO BUỘC PHẢI 
        elif sign_type == 'MANDATORY':
            mandatory_commands = {
                'R-301c': 'MANDATORY_RIGHT',
                'R-301d': 'MANDATORY_LEFT',
                'R-301e': 'MANDATORY_RIGHT',
                'R-302a': 'MANDATORY_RIGHT',
                'R-302b': 'MANDATORY_LEFT',
                'R-303': 'MANDATORY_STRAIGHT',
                'R-407a': 'MANDATORY_STRAIGHT',
                'R-409': 'MANDATORY_STRAIGHT',
                'R-425': 'MANDATORY_RIGHT',
                'R-434': 'MANDATORY_LEFT',
            }
            
            cmd_key = mandatory_commands.get(class_name)
            if cmd_key:
                command = self.commands.get(cmd_key)
            
            message = (
                f"   HƯỚNG DẪN\n"
                f"   Biển báo: {description}\n"
                f"   Khoảng cách: {distance:.1f}m\n"
                f"   Hành động: {description.lower()}"
            )
            
            alert_level = AlertLevel.CRITICAL
        
        #  BIỂN BÁO CẢNH BÁO 
        elif sign_type == 'WARNING_SIGN':
            warning_commands = {
                'W-225': 'CHILDREN_ZONE',
                'W-208': 'RAILROAD_CROSSING',
                'W-209': 'RAILROAD_CROSSING',
                'W-210': 'RAILROAD_CROSSING',
                'W-235': 'OBSTACLE',
                'W-233': 'OBSTACLE',
                'W-202a': 'CURVE_LEFT',
                'W-201a': 'CURVE_LEFT',
                'W-202b': 'CURVE_RIGHT',
                'W-201b': 'CURVE_RIGHT',
                'W-207a': 'INTERSECTION',
                'W-207b': 'INTERSECTION',
                'W-207c': 'INTERSECTION',
                'W-203b': 'INTERSECTION',
                'W-203c': 'INTERSECTION',
                'W-205a': 'INTERSECTION',
                'W-205b': 'INTERSECTION',
                'W-205d': 'INTERSECTION',
                'W-224': 'SLIPPERY_ROAD',
                'W-219': 'STEEP_DESCENT',
                'W-227': 'NARROW_ROAD',
                'W-245a': 'CONSTRUCTION',
            }
            
            cmd_key = warning_commands.get(class_name)
            if cmd_key:
                command = self.commands.get(cmd_key)
            
            message = (
                f"   CẢNH BÁO\n"
                f"   Biển báo: {description}\n"
                f"   Khoảng cách: {distance:.1f}m\n"
                f"   Hãy giảm tốc độ và chú ý"
            )
            
            alert_level = AlertLevel.WARNING
        
        # BIỂN BÁO THÔNG TIN 
        elif sign_type == 'INFO':
            message = (
                f"   THÔNG TIN\n"
                f"   Biển báo: {description}\n"
                f"   Khoảng cách: {distance:.1f}m"
            )
            
            alert_level = AlertLevel.INFO
        if command or alert_level != AlertLevel.NONE:
            self.last_alert_time[class_name] = current_time
        
        return command, message, alert_level
    
    
    def update_speed(self, new_speed):
        """
        Cập nhật tốc độ ước tính
        
        Args:
            new_speed (float): Tốc độ mới (km/h)
        """
        old_speed = self.estimated_speed
        self.estimated_speed = new_speed
        print(f"Speed updated: {old_speed} → {new_speed} km/h")
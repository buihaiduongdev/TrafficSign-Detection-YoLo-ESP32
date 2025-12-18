import sys
import os
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from distance_estimator import DistanceEstimator
from decision_logic import DecisionLogic
import json
import easyocr
from datetime import datetime
import time
from sound_sender import SoundSender 

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QSlider, QComboBox,
                             QFileDialog, QTableWidget, QTableWidgetItem, QProgressBar,
                             QSpinBox, QDoubleSpinBox, QStatusBar, QTabWidget, QFrame,
                             QGraphicsDropShadowEffect, QRadioButton, QButtonGroup,
                             QGroupBox, QSplitter, QLineEdit, QMessageBox)
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QIcon, QPalette
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, QRect, QSize

# Khởi tạo EasyOCR
reader = easyocr.Reader(['en'], gpu=False)

# Vietnamese sign name mapping
VIETNAMESE_SIGN_NAMES = {
    'DP-135': 'Đường ưu tiên',
    'P-102': 'Cấm đi ngược chiều',
    'P-103a': 'Cấm dừng xe',
    'P-103b': 'Cấm dừng xe',
    'P-103c': 'Cấm dừng xe',
    'P-104': 'Cấm đỗ xe',
    'P-106a': 'Cấm vượt',
    'P-106b': 'Cấm vượt',
    'P-107a': 'Cấm vượt xe tải',
    'P-112': 'Cấm rẽ trái',
    'P-115': 'Cấm rẽ phải',
    'P-117': 'Cấm quay đầu',
    'P-123a': 'Cấm đi vào',
    'P-123b': 'Cấm đi vào',
    'P-124a': 'Cấm ô tô đi vào',
    'P-124b': 'Cấm ô tô đi vào',
    'P-124c': 'Cấm ô tô đi vào',
    'P-127': 'Giới hạn tốc độ 50',
    'P-128': 'Giới hạn tốc độ 60',
    'P-130': 'Cấm dừng và đỗ xe',
    'P-131a': 'Cấm dừng và đỗ xe',
    'P-137': 'Hết hạn chế',
    'P-245a': 'Cấm đỗ xe hai phía',
    'R-301c': 'Đi thẳng và rẽ phải',
    'R-301d': 'Đi thẳng và rẽ trái',
    'R-301e': 'Rẽ phải',
    'R-302a': 'Rẽ phải hoặc đi thẳng',
    'R-302b': 'Rẽ trái hoặc đi thẳng',
    'R-303': 'Đi thẳng',
    'R-407a': 'Hướng đi thẳng phải theo',
    'R-409': 'Hướng đi thẳng',
    'R-425': 'Hướng rẽ phải',
    'R-434': 'Hướng rẽ trái',
    'S-509a': 'Đường cấm xe tải',
    'W-201a': 'Đường cong vòng trái',
    'W-201b': 'Đường cong vòng phải',
    'W-202a': 'Đường cong vòng trái',
    'W-202b': 'Đường cong vòng phải',
    'W-203b': 'Đường giao nhau',
    'W-203c': 'Đường giao nhau',
    'W-205a': 'Giao nhau với đường ưu tiên',
    'W-205b': 'Giao nhau với đường ưu tiên',
    'W-205d': 'Giao nhau với đường ưu tiên',
    'W-207a': 'Giao nhau với đường không ưu tiên',
    'W-207b': 'Giao nhau với đường không ưu tiên',
    'W-207c': 'Giao nhau với đường không ưu tiên',
    'W-208': 'Giao nhau với đường sắt',
    'W-209': 'Giao nhau với đường sắt',
    'W-210': 'Giao nhau với đường sắt',
    'W-219': 'Chú ý dốc xuống',
    'W-224': 'Chú ý đường trơn',
    'W-225': 'Chú ý: Trẻ em',
    'W-227': 'Chú ý đường hẹp',
    'W-233': 'Chú ý chướng ngại vật',
    'W-235': 'Chú ý chướng ngại vật',
    'W-245a': 'Chú ý công trường'
}

def get_vietnamese_sign_name(class_name):
    return VIETNAMESE_SIGN_NAMES.get(class_name, class_name)

PASTEL_STYLE = """
QMainWindow { background-color: #f5f5f5; }
QPushButton { background-color: #b8e0d2; border: none; border-radius: 12px; padding: 12px 24px; color: #2d5f5d; font-weight: bold; font-size: 13px; min-height: 40px; }
QPushButton:hover { background-color: #95d5c4; }
QPushButton:pressed { background-color: #7bc7b5; }
QPushButton#camera_btn { background-color: #d4a5a5; color: #5d2d2d; }
QPushButton#camera_btn:hover { background-color: #c88888; }
QPushButton#video_btn { background-color: #ffd6a5; color: #664d29; }
QPushButton#video_btn:hover { background-color: #ffcc88; }
QPushButton#image_btn { background-color: #caffbf; color: #2d5d2d; }
QPushButton#image_btn:hover { background-color: #b8f5aa; }
QPushButton#live_btn { background-color: #e0c3fc; color: #4a148c; } 
QPushButton#live_btn:hover { background-color: #d1a3f5; }
QPushButton#stop_btn { background-color: #ffadad; color: #5d2d2d; }
QPushButton#stop_btn:hover { background-color: #ff9999; }
QLabel#video_label { background-color: #ffffff; border: 3px solid #d4e9e2; border-radius: 15px; padding: 10px; }
QLabel#header_label { background-color: #9fd3c7; border-radius: 15px; padding: 20px; color: #2d5f5d; font-size: 24px; font-weight: bold; border: 2px solid #7bc7b5; }
QGroupBox { background-color: #ffffff; border: 2px solid #d4e9e2; border-radius: 12px; padding: 15px; margin-top: 10px; font-weight: bold; color: #2d5f5d; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 5px 10px; background-color: #b8e0d2; border-radius: 6px; color: #2d5f5d; }
QLineEdit { background-color: #ffffff; border: 2px solid #d4e9e2; border-radius: 8px; padding: 8px; color: #2d5f5d; font-weight: bold; }
QLineEdit:focus { border: 2px solid #9fd3c7; }
QTabWidget::pane { background-color: #ffffff; border: 2px solid #d4e9e2; border-radius: 12px; padding: 8px; }
QTabBar::tab { background-color: #e8f4f2; border: 2px solid #d4e9e2; border-radius: 8px; padding: 12px 20px; min-height: 20px; min-width: 100px; margin: 2px; color: #2d5f5d; font-weight: bold; }
QTabBar::tab:selected { background-color: #b8e0d2; color: #1a4d4a; }
"""

class TrafficSignDetectorApp(QMainWindow):
    """Ứng dụng GUI PyQt5 cho nhận diện biển báo với multi-model + IoT"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚦 Traffic Sign Detection System - Multi-Model & IoT")
        self.setGeometry(100, 100, 1800, 1000)
        self.setStyleSheet(PASTEL_STYLE)

        self.MODEL_YOLO8_PATH = r"./v11/best.pt"
        self.MODEL_YOLO11_PATH = r"./v8/best.pt"

        self.model_yolo8 = None
        self.model_yolo11 = None
        self.current_mode = "yolo8"  
        
        self.estimator = None
        self.logic = None
        self.sound_sender = None  # Init SoundSender
        
        self.load_models()
        
        if self.model_yolo8 is None and self.model_yolo11 is None:
            self.show_error("Failed to load any models")
            return

        self.init_ui()

        self.cap = None
        self.current_frame = None
        self.detections_yolo8 = []
        self.detections_yolo11 = []
        self.frame_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        self.detection_log_yolo8 = []
        self.detection_log_yolo11 = []
        self.start_time = datetime.now()

        self.inference_times_yolo8 = []
        self.inference_times_yolo11 = []
    
        self.frame_count = 0

        # FPS
        self.fps_frame_counter = 0
        self.fps_last_time = time.time()
        self.current_fps = 0.0

        # Skip frame
        self.process_interval = 3   # chạy YOLO mỗi 3 frame
        self.last_latency_ms = 0.0

    def load_models(self):
        """Tải cả 2 models YOLO"""
        print("="*60)
        print("LOADING MODELS...")
        print("="*60)
        
        try:
            print("Loading YOLOv8...")
            self.model_yolo8 = YOLO(self.MODEL_YOLO8_PATH)
            print(" YOLOv8 loaded successfully!")
        except Exception as e:
            print(f" YOLOv8 Error: {e}")
            self.model_yolo8 = None
        
        try:
            print("Loading YOLOv11...")
            self.model_yolo11 = YOLO(self.MODEL_YOLO11_PATH)
            print(" YOLOv11 loaded successfully!")
        except Exception as e:
            print(f" YOLOv11 Error: {e}")
            self.model_yolo11 = None

        self.estimator = DistanceEstimator(focal_length=800)
        self.logic = DecisionLogic(estimated_speed=60)
        print("="*60)
    
    def init_ui(self):
        """Khởi tạo giao diện"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QLabel("TRAFFIC SIGN DETECTION - MULTI-MODEL & IOT")
        header.setObjectName("header_label")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Mode Selection
        mode_group = QGroupBox("Model Selection Mode")
        mode_layout = QHBoxLayout()
        
        self.radio_yolo8 = QRadioButton("YOLOv8 Only")
        self.radio_yolo11 = QRadioButton("YOLOv11 Only")
        self.radio_compare = QRadioButton("Compare Both Models")
        
        self.radio_yolo8.setChecked(True)
        
        self.mode_button_group = QButtonGroup()
        self.mode_button_group.addButton(self.radio_yolo8)
        self.mode_button_group.addButton(self.radio_yolo11)
        self.mode_button_group.addButton(self.radio_compare)
        
        self.radio_yolo8.toggled.connect(self.on_mode_changed)
        self.radio_yolo11.toggled.connect(self.on_mode_changed)
        self.radio_compare.toggled.connect(self.on_mode_changed)
        
        if self.model_yolo8 is None: self.radio_yolo8.setEnabled(False)
        if self.model_yolo11 is None: self.radio_yolo11.setEnabled(False)
        if self.model_yolo8 is None or self.model_yolo11 is None:
            self.radio_compare.setEnabled(False)
        
        mode_layout.addWidget(self.radio_yolo8)
        mode_layout.addWidget(self.radio_yolo11)
        mode_layout.addWidget(self.radio_compare)
        mode_layout.addStretch()
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)
        
        # Main Content 
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Panel trái
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Video display container
        self.video_container = QWidget()
        self.video_layout = QHBoxLayout()
        self.video_layout.setSpacing(10)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label_yolo8 = QLabel("YOLOv8: No video loaded")
        self.video_label_yolo8.setObjectName("video_label")
        self.video_label_yolo8.setMinimumSize(700, 500)
        self.video_label_yolo8.setAlignment(Qt.AlignCenter)
        self.video_label_yolo8.setStyleSheet("font-size: 14px; color: #95a5a6;")
        
        self.video_label_yolo11 = QLabel("YOLOv11: No video loaded")
        self.video_label_yolo11.setObjectName("video_label")
        self.video_label_yolo11.setMinimumSize(700, 500)
        self.video_label_yolo11.setAlignment(Qt.AlignCenter)
        self.video_label_yolo11.setStyleSheet("font-size: 14px; color: #95a5a6;")
        self.video_label_yolo11.hide()
        
        self.video_layout.addWidget(self.video_label_yolo8)
        self.video_layout.addWidget(self.video_label_yolo11)
        self.video_container.setLayout(self.video_layout)
        left_panel.addWidget(self.video_container, 1)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.btn_camera = QPushButton("Camera")
        self.btn_camera.setObjectName("camera_btn")
        self.btn_camera.clicked.connect(self.open_camera)
        control_layout.addWidget(self.btn_camera)
        
        self.btn_video = QPushButton("Video")
        self.btn_video.setObjectName("video_btn")
        self.btn_video.clicked.connect(self.open_video)
        control_layout.addWidget(self.btn_video)
        
        self.btn_image = QPushButton("Image")
        self.btn_image.setObjectName("image_btn")
        self.btn_image.clicked.connect(self.open_image)
        control_layout.addWidget(self.btn_image)

        # NÚT LIVE MỚI
        self.btn_live = QPushButton("LIVE (ESP32)")
        self.btn_live.setObjectName("live_btn")
        self.btn_live.clicked.connect(self.open_live_stream)
        control_layout.addWidget(self.btn_live)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setObjectName("stop_btn")
        self.btn_stop.clicked.connect(self.stop_detection)
        control_layout.addWidget(self.btn_stop)
        
        left_panel.addLayout(control_layout)
        
        # Panel phải
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Tab 1: Settings
        settings_widget = QWidget()
        settings_widget.setObjectName("settings_container")
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(15)
        
        # CẤU HÌNH IP
        ip_label = QLabel("Network Configuration (IoT)")
        ip_label.setObjectName("section_label")
        settings_layout.addWidget(ip_label)
        
        settings_layout.addWidget(QLabel("ESP32-CAM IP Address:"))
        self.cam_ip_input = QLineEdit("10.34.117.102") 
        settings_layout.addWidget(self.cam_ip_input)
        
        settings_layout.addWidget(QLabel("ESP8266 Audio IP Address:"))
        self.audio_ip_input = QLineEdit("10.34.117.147") 
        settings_layout.addWidget(self.audio_ip_input)

        # Confidence
        conf_label = QLabel("Confidence Threshold")
        conf_label.setObjectName("section_label")
        settings_layout.addWidget(conf_label)
        
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setMinimum(0)
        self.confidence_slider.setMaximum(100)
        self.confidence_slider.setValue(50)
        self.confidence_label = QLabel("0.50")
        self.confidence_label.setObjectName("value_label")
        self.confidence_label.setAlignment(Qt.AlignCenter)
        self.confidence_slider.valueChanged.connect(self.update_confidence)
        settings_layout.addWidget(self.confidence_slider)
        settings_layout.addWidget(self.confidence_label)
        
        # Speed
        speed_label = QLabel("Estimated Speed (km/h)")
        speed_label.setObjectName("section_label")
        settings_layout.addWidget(speed_label)
        
        self.speed_spinbox = QSpinBox()
        self.speed_spinbox.setMinimum(0)
        self.speed_spinbox.setMaximum(200)
        self.speed_spinbox.setValue(60)
        self.speed_spinbox.valueChanged.connect(self.update_speed)
        settings_layout.addWidget(self.speed_spinbox)
        
        # Focal length
        focal_label = QLabel("Focal Length (pixels)")
        focal_label.setObjectName("section_label")
        settings_layout.addWidget(focal_label)
        
        self.focal_spinbox = QDoubleSpinBox()
        self.focal_spinbox.setMinimum(100)
        self.focal_spinbox.setMaximum(2000)
        self.focal_spinbox.setValue(800)
        self.focal_spinbox.valueChanged.connect(self.update_focal_length)
        settings_layout.addWidget(self.focal_spinbox)
        
        settings_layout.addStretch()
        settings_widget.setLayout(settings_layout)
        tab_widget.addTab(settings_widget, "Settings")
        
        # Tab 2: Detections
        detections_widget = QWidget()
        detections_layout = QVBoxLayout()
        
        self.detections_table = QTableWidget()
        self.detections_table.setColumnCount(6)
        self.detections_table.setHorizontalHeaderLabels([
            "Model", "Class", "Confidence", "Dist (m)", "Alert", "Time"
        ])
        
        detections_layout.addWidget(self.detections_table)
        detections_widget.setLayout(detections_layout)
        tab_widget.addTab(detections_widget, "Detections")

        # Tab 3: Statistics
        stats_widget = QWidget()
        stats_layout = QVBoxLayout()
        self.stats_text = QLabel()
        self.stats_text.setObjectName("stats_label")
        self.stats_text.setFont(QFont("Segoe UI", 10))
        self.stats_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.stats_text.setWordWrap(True)
        stats_layout.addWidget(self.stats_text)
        stats_widget.setLayout(stats_layout)
        tab_widget.addTab(stats_widget, "Statistics")
        
        # Tab 4: Comparison
        comparison_widget = QWidget()
        comparison_layout = QVBoxLayout()
        self.comparison_text = QLabel()
        self.comparison_text.setObjectName("comparison_label")
        self.comparison_text.setFont(QFont("Consolas", 10))
        self.comparison_text.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.comparison_text.setWordWrap(True)
        comparison_layout.addWidget(self.comparison_text)
        comparison_widget.setLayout(comparison_layout)
        self.comparison_tab_index = tab_widget.addTab(comparison_widget, "Comparison")
        tab_widget.setTabEnabled(self.comparison_tab_index, False)
        
        right_panel.addWidget(tab_widget)
        self.tab_widget = tab_widget
        
        content_layout.addLayout(left_panel, 3)
        content_layout.addLayout(right_panel, 1)
        main_layout.addLayout(content_layout)
        
        self.statusBar().showMessage("Ready to detect traffic signs")
        main_widget.setLayout(main_layout)
    
    def on_mode_changed(self):
        if self.radio_yolo8.isChecked():
            self.current_mode = "yolo8"
            self.video_label_yolo11.hide()
            self.video_label_yolo8.show()
            self.video_label_yolo8.setMinimumSize(700, 500)
            self.tab_widget.setTabEnabled(self.comparison_tab_index, False)
            self.statusBar().showMessage("Mode: YOLOv8 Only")
            
        elif self.radio_yolo11.isChecked():
            self.current_mode = "yolo11"
            self.video_label_yolo8.hide()
            self.video_label_yolo11.show()
            self.video_label_yolo11.setMinimumSize(700, 500)
            self.tab_widget.setTabEnabled(self.comparison_tab_index, False)
            self.statusBar().showMessage("Mode: YOLOv11 Only")
            
        elif self.radio_compare.isChecked():
            self.current_mode = "compare"
            self.video_label_yolo8.show()
            self.video_label_yolo11.show()
            self.video_label_yolo8.setMinimumSize(600, 450)
            self.video_label_yolo11.setMinimumSize(600, 450)
            self.tab_widget.setTabEnabled(self.comparison_tab_index, True)
            self.statusBar().showMessage("⚖️ Mode: Compare Both Models")
    
    def update_confidence(self, value):
        conf = value / 100.0
        self.confidence_label.setText(f"{conf:.2f}")
    
    def update_speed(self, value):
        self.logic.update_speed(value)
    
    def update_focal_length(self, value):
        self.estimator.focal_length = value
    
    # --- CÁC HÀM MỞ SOURCE ---
    def open_camera(self):
        self.stop_detection()
        self.sound_sender = None
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.show_error("Cannot open camera")
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.timer.start(30)
        self.statusBar().showMessage("Camera is running...")

    def open_live_stream(self):
        """Kết nối tới ESP32-CAM và ESP8266"""
        self.stop_detection()
        
        cam_ip = self.cam_ip_input.text().strip()
        audio_ip = self.audio_ip_input.text().strip()
        
        if not cam_ip or not audio_ip:
            self.show_error("Please enter both IPs in Settings tab!")
            return

        print(f"Connecting Audio to {audio_ip}...")
        self.sound_sender = SoundSender(audio_ip)
        
        stream_url = f"http://{cam_ip}:81/stream"
        print(f"Connecting Video to {stream_url}...")
        
        self.cap = cv2.VideoCapture(stream_url)
        
        if not self.cap.isOpened():
            stream_url_backup = f"http://{cam_ip}/"
            print(f"Retrying with {stream_url_backup}...")
            self.cap = cv2.VideoCapture(stream_url_backup)
            
        if self.cap.isOpened():
            self.timer.start(30)
            self.statusBar().showMessage(f"📡 LIVE: Connected to {cam_ip}")
            QMessageBox.information(self, "Success", f"Connected to ESP32-CAM!\nAudio target: {audio_ip}")
        else:
            self.show_error(f"Cannot connect to ESP32 stream at {cam_ip}")
    
    def open_video(self):
        self.stop_detection()
        self.sound_sender = None
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Video Files (*.mp4 *.avi *.mov);;All Files (*)"
        )
        if not file_path: return
        self.cap = cv2.VideoCapture(file_path)
        if not self.cap.isOpened():
            self.show_error("Cannot open video")
            return
        self.timer.start(30)
        self.statusBar().showMessage(f"📹 Playing: {Path(file_path).name}")
    
    def open_image(self):
        self.stop_detection()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image File", "",
            "Image Files (*.jpg *.png *.bmp);;All Files (*)"
        )
        if not file_path: return
        
        frame = cv2.imread(file_path)
        if frame is None:
            self.show_error("Cannot open image")
            return
        
        self.current_frame = frame

        if self.current_mode == "yolo8" and self.model_yolo8:
            self.detections_yolo8 = self.process_frame(frame, self.model_yolo8)
            self.display_frame_single(frame, self.detections_yolo8, self.video_label_yolo8)
        elif self.current_mode == "yolo11" and self.model_yolo11:
            self.detections_yolo11 = self.process_frame(frame, self.model_yolo11)
            self.display_frame_single(frame, self.detections_yolo11, self.video_label_yolo11)
        elif self.current_mode == "compare":
            if self.model_yolo8:
                self.detections_yolo8 = self.process_frame(frame, self.model_yolo8)
                self.display_frame_single(frame, self.detections_yolo8, self.video_label_yolo8, "YOLOv8")
            if self.model_yolo11:
                self.detections_yolo11 = self.process_frame(frame, self.model_yolo11)
                self.display_frame_single(frame, self.detections_yolo11, self.video_label_yolo11, "YOLOv11")
            self.update_comparison()
        
        self.update_detections_table()
        self.statusBar().showMessage(f"🖼️ Image: {Path(file_path).name}")
    
    # def update_frame(self):
    #     if self.cap is None or not self.cap.isOpened():
    #         self.timer.stop()
    #         return
        
    #     ret, frame = self.cap.read()
    #     if not ret:
    #         self.timer.stop()
    #         self.cap.release()
    #         self.cap = None
    #         self.statusBar().showMessage("Video finished")
    #         return
        
    #     self.frame_count += 1
    #     self.current_frame = frame
        
    #     import time

    #     if self.current_mode == "yolo8" and self.model_yolo8:
    #         start = time.time()
    #         self.detections_yolo8 = self.process_frame(frame, self.model_yolo8)
    #         self.inference_times_yolo8.append((time.time() - start) * 1000)
            
    #         self.display_frame_single(frame, self.detections_yolo8, self.video_label_yolo8)
    #         self.log_detections(self.detections_yolo8, self.detection_log_yolo8)
            
    #     elif self.current_mode == "yolo11" and self.model_yolo11:
    #         start = time.time()
    #         self.detections_yolo11 = self.process_frame(frame, self.model_yolo11)
    #         self.inference_times_yolo11.append((time.time() - start) * 1000)
            
    #         self.display_frame_single(frame, self.detections_yolo11, self.video_label_yolo11)
    #         self.log_detections(self.detections_yolo11, self.detection_log_yolo11)
            
    #     elif self.current_mode == "compare":
    #         if self.model_yolo8:
    #             start = time.time()
    #             self.detections_yolo8 = self.process_frame(frame, self.model_yolo8)
    #             self.inference_times_yolo8.append((time.time() - start) * 1000)
    #             self.display_frame_single(frame, self.detections_yolo8, self.video_label_yolo8, "YOLOv8")
    #             self.log_detections(self.detections_yolo8, self.detection_log_yolo8)
            
    #         if self.model_yolo11:
    #             start = time.time()
    #             self.detections_yolo11 = self.process_frame(frame, self.model_yolo11)
    #             self.inference_times_yolo11.append((time.time() - start) * 1000)
    #             self.display_frame_single(frame, self.detections_yolo11, self.video_label_yolo11, "YOLOv11")
    #             self.log_detections(self.detections_yolo11, self.detection_log_yolo11)
            
    #         self.update_comparison()
        
    #     self.update_detections_table()
    #     self.update_statistics()
    
    ## TOI UA, CHAY DETECT MOI 3 FRAME
    def update_frame(self):
        if self.cap is None or not self.cap.isOpened():
            self.timer.stop()
            return

        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()
            self.cap.release()
            self.cap = None
            self.statusBar().showMessage("Video finished")
            return

        self.frame_count += 1
        self.current_frame = frame

        import time

        # ================= FPS =================
        self.fps_frame_counter += 1
        now = time.time()
        if now - self.fps_last_time >= 1.0:
            self.current_fps = self.fps_frame_counter / (now - self.fps_last_time)
            self.fps_frame_counter = 0
            self.fps_last_time = now

        run_yolo = (self.frame_count % self.process_interval == 0)

        # ================= YOLOv8 =================
        if self.current_mode == "yolo8" and self.model_yolo8:
            if run_yolo:
                start = time.time()
                self.detections_yolo8 = self.process_frame(frame, self.model_yolo8)
                self.last_latency_ms = (time.time() - start) * 1000
                self.inference_times_yolo8.append(self.last_latency_ms)

                print(
                    f"[LIVE][YOLOv8] FPS: {self.current_fps:.1f} | "
                    f"Latency: {self.last_latency_ms:.1f} ms | "
                    f"Frame: {self.frame_count}"
                )

            self.display_frame_single(frame, self.detections_yolo8, self.video_label_yolo8)
            self.log_detections(self.detections_yolo8, self.detection_log_yolo8)

        # ================= YOLOv11 =================
        elif self.current_mode == "yolo11" and self.model_yolo11:
            if run_yolo:
                start = time.time()
                self.detections_yolo11 = self.process_frame(frame, self.model_yolo11)
                self.last_latency_ms = (time.time() - start) * 1000
                self.inference_times_yolo11.append(self.last_latency_ms)

                print(
                    f"[LIVE][YOLOv11] FPS: {self.current_fps:.1f} | "
                    f"Latency: {self.last_latency_ms:.1f} ms | "
                    f"Frame: {self.frame_count}"
                )

            self.display_frame_single(frame, self.detections_yolo11, self.video_label_yolo11)
            self.log_detections(self.detections_yolo11, self.detection_log_yolo11)

        # ================= COMPARE =================
        elif self.current_mode == "compare":
            if run_yolo:
                if self.model_yolo8:
                    start = time.time()
                    self.detections_yolo8 = self.process_frame(frame, self.model_yolo8)
                    latency8 = (time.time() - start) * 1000
                    self.inference_times_yolo8.append(latency8)

                if self.model_yolo11:
                    start = time.time()
                    self.detections_yolo11 = self.process_frame(frame, self.model_yolo11)
                    latency11 = (time.time() - start) * 1000
                    self.inference_times_yolo11.append(latency11)

                print(
                    f"[LIVE][COMPARE] FPS: {self.current_fps:.1f} | "
                    f"YOLOv8: {latency8:.1f} ms | "
                    f"YOLOv11: {latency11:.1f} ms | "
                    f"Frame: {self.frame_count}"
                )

            if self.model_yolo8:
                self.display_frame_single(frame, self.detections_yolo8, self.video_label_yolo8, "YOLOv8")
                self.log_detections(self.detections_yolo8, self.detection_log_yolo8)

            if self.model_yolo11:
                self.display_frame_single(frame, self.detections_yolo11, self.video_label_yolo11, "YOLOv11")
                self.log_detections(self.detections_yolo11, self.detection_log_yolo11)

            self.update_comparison()

        self.update_detections_table()
        self.update_statistics()


    def process_frame(self, frame, model):
        conf = self.confidence_slider.value() / 100.0
        results = model.predict(frame, conf=conf, verbose=False)
        result = results[0]
        
        detections = []
        
        if len(result.boxes) > 0:
            for box in result.boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                conf = float(box.conf[0])
                
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                bbox_width = x2 - x1

                # OCR Logic
                if class_name in ['P-127', 'P-128']:
                    crop = frame[y1:y2, x1:x2]
                    try:
                        ocr_results = reader.readtext(crop)
                        for (_, text, ocr_conf) in ocr_results:
                            if '60' in text and ocr_conf > 0.7:
                                class_name = 'P-128'
                            elif '50' in text and ocr_conf > 0.7:
                                class_name = 'P-127'
                    except:
                        pass
                
                distance = self.estimator.estimate_distance(bbox_width)
                
                command, message, alert_level = self.logic.decide(
                    class_name, distance, conf
                )
                
                # --- GỬI ÂM THANH IOT ---
                if command and self.sound_sender:
                    # Logic cooldown trong self.logic sẽ ngăn việc gửi spam
                    self.sound_sender.play_sound(class_name)
                
                detections.append({
                    'class_name': class_name,
                    'confidence': conf,
                    'distance': distance,
                    'bbox': (x1, y1, x2, y2),
                    'command': command,
                    'alert_level': alert_level,
                    'message': message
                })
        
        return detections
    
    def log_detections(self, detections, log_list):
        for det in detections:
            if det['command']:
                log_list.append({
                    'timestamp': datetime.now().isoformat(),
                    'frame': self.frame_count,
                    'class_name': det['class_name'],
                    'confidence': float(det['confidence']),
                    'distance': float(det['distance']),
                    'alert_level': det['alert_level'].value
                })
    
    def display_frame_single(self, frame, detections, label_widget, title=""):
        display_frame = frame.copy()
        if title:
            cv2.putText(display_frame, title, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
            cv2.putText(display_frame, title, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 150, 255), 2)
        for det in detections:
            x1, y1, x2, y2 = det['bbox']

            if det['alert_level'].name == 'CRITICAL':
                color = (100, 100, 255)
            elif det['alert_level'].name == 'WARNING':
                color = (100, 200, 255)
            else:
                color = (150, 255, 150)

            cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 3)

            label = f"{det['class_name']} {det['confidence']:.2%}"
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(display_frame, (x1, y1 - label_h - 10), (x1 + label_w + 10, y1), color, -1)
            cv2.putText(display_frame, label, (x1 + 5, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            dist_text = f"D: {det['distance']:.1f}m"
            cv2.putText(display_frame, dist_text, (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        if self.current_mode == "compare":
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaledToWidth(600, Qt.SmoothTransformation)
        else:
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaledToWidth(700, Qt.SmoothTransformation)
        
        label_widget.setPixmap(scaled_pixmap)
    
    def update_detections_table(self):
        all_detections = []
        if self.current_mode == "yolo8" or self.current_mode == "compare":
            for det in self.detections_yolo8: all_detections.append(("YOLOv8", det))
        if self.current_mode == "yolo11" or self.current_mode == "compare":
            for det in self.detections_yolo11: all_detections.append(("YOLOv11", det))
        
        self.detections_table.setRowCount(len(all_detections))
        for row, (model_name, det) in enumerate(all_detections):
            item = QTableWidgetItem(model_name)
            self.detections_table.setItem(row, 0, item)
            vietnamese_name = get_vietnamese_sign_name(det['class_name'])
            item = QTableWidgetItem(f"{vietnamese_name}")
            self.detections_table.setItem(row, 1, item)
            item = QTableWidgetItem(f"{det['confidence']:.2%}")
            self.detections_table.setItem(row, 2, item)
            item = QTableWidgetItem(f"{det['distance']:.1f}")
            self.detections_table.setItem(row, 3, item)
            alert_text = det['alert_level'].value if det['command'] else "No"
            item = QTableWidgetItem(alert_text)
            self.detections_table.setItem(row, 4, item)
            item = QTableWidgetItem(datetime.now().strftime("%H:%M:%S"))
            self.detections_table.setItem(row, 5, item)
    
    def update_statistics(self):
        elapsed = datetime.now() - self.start_time
        stats_html = f"""
<div style='font-family: Consolas; color: #2c3e50;'>
<h2 style='color: #5e35b1; text-align: center;'>SESSION STATISTICS</h2>
<hr style='border: 2px solid #b39ddb;'/>
<p><b>⏱️ Elapsed Time:</b> {elapsed}</p>
<p><b>📹 Frames Processed:</b> {self.frame_count}</p>
"""
        if self.current_mode == "yolo8" or self.current_mode == "compare":
            total = len(self.detection_log_yolo8)
            alerts = sum(1 for d in self.detection_log_yolo8 if d['alert_level'] != "⚪ NONE")
            avg_conf = np.mean([d['confidence'] for d in self.detection_log_yolo8]) if total > 0 else 0
            avg_time = np.mean(self.inference_times_yolo8) if self.inference_times_yolo8 else 0
            stats_html += f"""
<h3 style='color: #1976d2;'>YOLOv8</h3>
<p style='margin-left: 20px;'><b>Detections:</b> {total}</p>
<p style='margin-left: 20px;'><b>Alerts:</b> {alerts}</p>
<p style='margin-left: 20px;'><b>Avg Confidence:</b> {avg_conf:.2%}</p>
<p style='margin-left: 20px;'><b>Avg Inference:</b> {avg_time:.1f}ms</p>
"""
        if self.current_mode == "yolo11" or self.current_mode == "compare":
            total = len(self.detection_log_yolo11)
            alerts = sum(1 for d in self.detection_log_yolo11 if d['alert_level'] != "⚪ NONE")
            avg_conf = np.mean([d['confidence'] for d in self.detection_log_yolo11]) if total > 0 else 0
            avg_time = np.mean(self.inference_times_yolo11) if self.inference_times_yolo11 else 0
            stats_html += f"""
<h3 style='color: #388e3c;'>YOLOv11</h3>
<p style='margin-left: 20px;'><b>Detections:</b> {total}</p>
<p style='margin-left: 20px;'><b>Alerts:</b> {alerts}</p>
<p style='margin-left: 20px;'><b>Avg Confidence:</b> {avg_conf:.2%}</p>
<p style='margin-left: 20px;'><b>Avg Inference:</b> {avg_time:.1f}ms</p>
"""
        stats_html += "</div>"
        self.stats_text.setText(stats_html)
    
    def update_comparison(self):
        if self.current_mode != "compare": return
        yolo8_count = len(self.detections_yolo8)
        yolo11_count = len(self.detections_yolo11)
        yolo8_avg_conf = np.mean([d['confidence'] for d in self.detections_yolo8]) if yolo8_count > 0 else 0
        yolo11_avg_conf = np.mean([d['confidence'] for d in self.detections_yolo11]) if yolo11_count > 0 else 0
        yolo8_time = np.mean(self.inference_times_yolo8[-10:]) if self.inference_times_yolo8 else 0
        yolo11_time = np.mean(self.inference_times_yolo11[-10:]) if self.inference_times_yolo11 else 0
        
        comparison_html = f"""
<div style='font-family: Consolas; color: #2c3e50;'>
<h2 class='comp_header' style='color: #d32f2f; text-align: center;'>MODEL COMPARISON</h2>
<hr style='border: 2px solid #ef5350;'/>
<h3 class='frame_stats'>Current Frame Statistics</h3>
<table style='width: 100%; border-collapse: collapse;'>
<tr style='background-color: #e3f2fd;'>
    <th style='padding: 8px; border: 1px solid #90caf9;'>Metric</th>
    <th style='padding: 8px; border: 1px solid #90caf9;'>YOLOv8</th>
    <th style='padding: 8px; border: 1px solid #90caf9;'>YOLOv11</th>
</tr>
<tr>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'><b>Detections</b></td>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'>{yolo8_count}</td>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'>{yolo11_count}</td>
</tr>
<tr style='background-color: #f5f5f5;'>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'><b>Avg Confidence</b></td>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'>{yolo8_avg_conf:.2%}</td>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'>{yolo11_avg_conf:.2%}</td>
</tr>
<tr>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'><b>Inference Time</b></td>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'>{yolo8_time:.1f}ms</td>
    <td style='padding: 8px; border: 1px solid #e0e0e0;'>{yolo11_time:.1f}ms</td>
</tr>
</table>
</div>
"""
        self.comparison_text.setText(comparison_html)
    
    def stop_detection(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
            self.cap = None
        self.statusBar().showMessage("Stopped")
        self.save_logs()
    
    
    def save_logs(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        log_dir = "detec_log"
        os.makedirs(log_dir, exist_ok=True)

        # ===== YOLOv8 =====
        if self.detection_log_yolo8:
            log_file = os.path.join(
                log_dir, f"detection_log_yolo8_{timestamp}.json"
            )
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.detection_log_yolo8, f, indent=2, ensure_ascii=False)

        # ===== YOLOv11 =====
        if self.detection_log_yolo11:
            log_file = os.path.join(
                log_dir, f"detection_log_yolo11_{timestamp}.json"
            )
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(self.detection_log_yolo11, f, indent=2, ensure_ascii=False)

        print(f"[LOG] Detection logs saved to '{log_dir}/'")

    def show_error(self, message):
        self.statusBar().showMessage(f"{message}")
        QMessageBox.warning(self, "Error", message)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TrafficSignDetectorApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
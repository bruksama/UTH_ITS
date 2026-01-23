"""
File cấu hình cho hệ thống điều khiển đèn giao thông
"""
import os

# Cấu hình màu sắc
COLORS = {
    'background': (40, 40, 40),
    'text': (255, 255, 255),
    'text_secondary': (200, 200, 200),
    'primary': (0, 162, 255),  # Blue
    'success': (0, 255, 100),   # Green
    'warning': (0, 255, 255),   # Yellow
    'danger': (0, 0, 255),      # Red
    'info': (255, 100, 0),      # Orange
}

# Cấu hình đèn giao thông
TRAFFIC_LIGHT_CONFIG = {
    'min_green_time': 5,      # Thời gian xanh tối thiểu (giây)
    'max_green_time': 30,     # Thời gian xanh tối đa (giây)
    'yellow_time': 3,         # Thời gian vàng (giây)
    'threshold': 3,           # Ngưỡng số xe để chuyển đèn
}

# Cấu hình detection
DETECTION_CONFIG = {
    'confidence_threshold': 0.25,  # Ngưỡng confidence tối thiểu
    'model_path': 'yolov8n.pt',
    'vehicle_classes': [2, 3, 5, 7],  # car, motorcycle, bus, truck
}

# Cấu hình UI
UI_CONFIG = {
    'font_scale': 0.7,
    'font_thickness': 2,
    'line_thickness': 2,
    'dashboard_width': 300,
    'show_fps': True,
    'show_statistics': True,
    # Cấu hình cửa sổ hiển thị
    'fixed_window_size': True,  # True = kích thước cố định, False = theo video
    'window_width': 1280,       # Chiều rộng cửa sổ (pixels)
    'window_height': 720,       # Chiều cao cửa sổ (pixels)
}

# Cấu hình zones (có thể tùy chỉnh theo video)
ZONES_CONFIG = None  # None = tự động tạo zones mặc định

# Cấu hình output
OUTPUT_CONFIG = {
    'base_folder': 'output',              # Folder gốc chứa tất cả output
    'sessions_folder': 'sessions',        # Folder chứa các session
    'create_session': True,               # True = tạo session riêng cho mỗi lần chạy
    'session_name_format': '%Y%m%d_%H%M%S',  # Format timestamp cho session
    'create_screenshots_folder': True,    # True = tạo folder screenshots riêng
    'create_metadata': True,              # True = tạo file metadata.json cho session
}

# Cấu hình logging
LOGGING_CONFIG = {
    'enabled': True,
    'log_file': 'traffic_logs.csv',  # Sẽ được đặt trong output folder
    'log_interval': 1,  # Log mỗi N giây
}

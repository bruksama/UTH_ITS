# 🚦 Hệ Thống Nhận Diện Xe và Điều Khiển Đèn Giao Thông Thông Minh

Hệ thống AI thông minh sử dụng YOLOv8n để nhận diện xe tại ngã tư và tự động điều khiển đèn giao thông dựa trên mật độ xe thời gian thực. Phiên bản nâng cấp với giao diện trực quan, dashboard đầy đủ, và hệ thống phân tích thông minh.

## ✨ Tính năng

### 🎯 Tính năng chính

- ✅ **Nhận diện xe thông minh**: Sử dụng YOLOv8n để phát hiện các loại xe (ô tô, xe máy, xe bus, xe tải)
- ✅ **Đếm xe theo hướng**: Tự động chia ngã tư thành 4 zones và đếm số xe mỗi hướng
- ✅ **Điều khiển đèn tự động**: Thuật toán thông minh điều khiển đèn dựa trên số lượng xe
- ✅ **Dashboard real-time**: Hiển thị thống kê trực quan và đầy đủ
- ✅ **Logging và Export**: Ghi log chi tiết và export thống kê

### 🎨 Giao diện

- 🖥️ **Dashboard trực quan**: Panel thống kê với màu sắc chuyên nghiệp và dễ đọc
- 📊 **Phân bổ thời gian thông minh**:
  - Progress bar động với màu sắc thay đổi theo thời gian
  - Hiển thị thời gian đã chạy / tối đa (ví dụ: 10s / 30s)
  - Phần trăm hoàn thành và thời gian còn lại
  - Lý do chuyển đèn (đạt ngưỡng, hết thời gian, hướng khác đông hơn)
- 🎯 **Visualization chất lượng cao**:
  - Bounding boxes màu sắc theo loại xe
  - Zones trong suốt với hiệu ứng gradient
  - Đèn giao thông trực quan với glow effect
- ⌨️ **Điều khiển linh hoạt**: Pause/Resume (SPACE), Screenshot (S), Quit (Q)

### 📈 Thống kê và Logging

- 📝 **CSV Logging**: Ghi log chi tiết vào file CSV
- 📊 **Summary Export**: Tự động export thống kê tổng hợp
- 📈 **Real-time Stats**: Thống kê real-time trên dashboard

## 🛠️ Yêu cầu

- Python 3.8+
- OpenCV
- Ultralytics (YOLOv8)
- NumPy

## 📦 Cài đặt

1. **Clone hoặc tải project về**

2. **Cài đặt các thư viện cần thiết:**

```bash
pip install -r requirements.txt
```

3. **Model YOLOv8n sẽ được tự động tải về khi chạy lần đầu**

## 🚀 Sử dụng

### Chạy cơ bản:

```bash
python main.py --video video2.mp4 --show
```

### Sử dụng webcam:

```bash
python main.py --video 0 --show
```

### Chỉ xử lý và lưu (không hiển thị):

```bash
python main.py --video intersection_video.mp4 --output result.mp4 --no-show
```

### Các tham số:

- `--video`: Đường dẫn đến video hoặc số webcam (bắt buộc)
  - Ví dụ: `video2.mp4`, `traffic.mp4`, `0` (webcam)
- `--model`: Đường dẫn đến model YOLOv8n (mặc định: `yolov8n.pt`)
- `--output`: Đường dẫn lưu video output (mặc định: `output_video.mp4`)
- `--show`: Hiển thị video trong khi xử lý (mặc định: True)
- `--no-show`: Chỉ xử lý và lưu, không hiển thị video

### Điều khiển khi đang chạy:

- **Q**: Thoát chương trình
- **SPACE**: Tạm dừng/Tiếp tục
- **S**: Lưu screenshot

## 📁 Cấu trúc dự án

```
.
├── main.py                      # Script chính (phiên bản nâng cấp)
├── vehicle_detector.py          # Module nhận diện xe
├── traffic_counter.py           # Module đếm xe theo hướng
├── traffic_light_controller.py  # Module điều khiển đèn
├── ui_dashboard.py             # Module dashboard UI
├── logger.py                    # Module logging và export
├── config.py                    # File cấu hình
├── requirements.txt             # Dependencies
└── README.md                    # Tài liệu
```

## ⚙️ Cấu hình

Bạn có thể tùy chỉnh hệ thống trong file `config.py`:

### Cấu hình đèn giao thông:

```python
TRAFFIC_LIGHT_CONFIG = {
    'min_green_time': 5,      # Thời gian xanh tối thiểu (giây)
    'max_green_time': 30,     # Thời gian xanh tối đa (giây)
    'yellow_time': 3,         # Thời gian vàng (giây)
    'threshold': 3,           # Ngưỡng số xe để chuyển đèn
}
```

### Cấu hình detection:

```python
DETECTION_CONFIG = {
    'confidence_threshold': 0.25,  # Ngưỡng confidence tối thiểu
    'model_path': 'yolov8n.pt',
    'vehicle_classes': [2, 3, 5, 7],  # car, motorcycle, bus, truck
}
```

### Cấu hình UI:

```python
UI_CONFIG = {
    'font_scale': 0.7,
    'font_thickness': 2,
    'line_thickness': 2,
    'dashboard_width': 300,
    'show_fps': True,
    'show_statistics': True,
}
```

## 🧠 Nguyên lý hoạt động

### 1. Nhận diện xe

- Sử dụng YOLOv8n để phát hiện các loại xe trong frame
- Lọc theo confidence threshold và class ID
- Vẽ bounding boxes với màu sắc phân biệt theo loại xe

### 2. Đếm xe theo hướng

- Chia ngã tư thành 4 zones (Bắc, Nam, Đông, Tây)
- Sử dụng ray casting algorithm để kiểm tra xe nằm trong zone nào
- Đếm và hiển thị số lượng xe mỗi hướng

### 3. Điều khiển đèn thông minh

- **Đèn xanh tối thiểu**: 5 giây (đảm bảo xe có thời gian đi qua)
- **Đèn xanh tối đa**: 30 giây (tránh chờ quá lâu)
- **Thuật toán chuyển đèn thông minh**:
  - Đã hết thời gian xanh tối thiểu VÀ
  - (Hướng hiện tại ít xe < ngưỡng HOẶC có hướng khác nhiều xe hơn đáng kể)
  - Hoặc đã đạt thời gian xanh tối đa
- **Thời gian vàng**: 3 giây (cảnh báo trước khi chuyển)
- **Hiển thị trực quan**:
  - Progress bar màu động (xanh → cam → đỏ)
  - Thời gian đã chạy / tối đa
  - Phần trăm hoàn thành
  - Lý do sắp chuyển đèn (nếu có)

### 4. Dashboard và Logging

- Hiển thị thống kê real-time: FPS, số xe, trạng thái đèn
- Ghi log vào CSV file mỗi giây
- Tự động export summary khi kết thúc

## 📊 Output Files

Sau khi chạy, hệ thống sẽ tạo các file:

- `output_video.mp4`: Video đã xử lý với annotations
- `traffic_logs.csv`: Log chi tiết (timestamp, số xe mỗi hướng, trạng thái đèn, FPS)
- `traffic_summary.txt`: Thống kê tổng hợp
- `screenshot_*.jpg`: Screenshots (nếu nhấn S)

## 🎨 Giao diện

### Dashboard Panel (Bên trái):

- **FPS**: Tốc độ xử lý real-time
- **VEHICLES**: Số xe hiện tại theo từng hướng
  - North, South, East, West
- **TRAFFIC LIGHT**: Thông tin đèn giao thông chi tiết
  - Hướng và trạng thái hiện tại (GREEN/YELLOW)
  - Thời gian đã chạy / tối đa (10s / 30s)
  - Progress bar động với màu sắc thông minh:
    - 🟢 Xanh (0-50%): Còn nhiều thời gian
    - 🟠 Cam (50-80%): Gần hết thời gian
    - 🔴 Đỏ (80-100%): Sắp hết thời gian
  - Phần trăm hoàn thành và thời gian còn lại
  - Lý do chuyển đèn khi sắp chuyển:
    - "Gần hết thời gian tối đa (30s)"
    - "Ít xe (<5 xe)"
    - "Hướng khác đông hơn (+8 xe)"

### Main View:

- **Zones**: Các vùng đếm xe với màu sắc phân biệt
- **Bounding boxes**: Vẽ quanh các xe được phát hiện
- **Đèn giao thông**: Hiển thị trạng thái ở góc trên phải
- **Progress bar**: Hiển thị tiến độ xử lý

## 🔧 Tùy chỉnh Zones

Nếu video của bạn có góc nhìn khác, bạn có thể tùy chỉnh zones trong `traffic_counter.py`:

```python
def _create_default_zones(self):
    h, w = self.height, self.width

    return {
        'north': {
            'points': [(x1, y1), (x2, y2), ...],  # Tọa độ polygon
            'color': COLORS['primary']
        },
        # ... các hướng khác
    }
```

## 📹 Yêu cầu Video

### Định dạng được hỗ trợ:

- **MP4** (.mp4) - **Khuyến nghị** ⭐
- AVI, MOV, MKV, FLV, WMV, WEBM

### Yêu cầu kỹ thuật:

- **Độ phân giải**: Tối thiểu 320x240, khuyến nghị 720p-1080p
- **FPS**: 24-30 FPS (tự động phát hiện)
- **Codec**: H.264 (MPEG-4 AVC) - khuyến nghị
- **Nội dung**: Góc nhìn rõ ràng của ngã tư, ánh sáng đủ

### Xử lý lỗi:

- Hệ thống tự động kiểm tra file tồn tại
- Tự động thử các codec khác nếu codec mặc định không hoạt động
- Hỗ trợ webcam (số 0, 1, 2...)
- Thông báo lỗi rõ ràng và gợi ý giải pháp

**Xem chi tiết**: [VIDEO_REQUIREMENTS.md](VIDEO_REQUIREMENTS.md)

## 📝 Lưu ý

- Video đầu vào nên có góc nhìn rõ ràng của ngã tư
- Zones mặc định được chia đều, bạn có thể tùy chỉnh theo video cụ thể
- Hệ thống hoạt động tốt nhất với video có chất lượng tốt và ánh sáng đủ
- Model YOLOv8n được tối ưu cho tốc độ, có thể đổi sang YOLOv8s/m/l để độ chính xác cao hơn
- Nếu video không tương thích, sử dụng FFmpeg để chuyển đổi sang MP4 (H.264)

## 🚀 Cải tiến trong phiên bản này

- ✨ **Giao diện trực quan**: Dashboard chuyên nghiệp, dễ đọc, dễ hiểu
- 📊 **Phân bổ thời gian thông minh**:
  - Progress bar động với màu sắc thay đổi theo thời gian
  - Hiển thị lý do chuyển đèn để người dùng hiểu thuật toán
  - Thống kê chi tiết về thời gian và phần trăm hoàn thành
- 🎯 **Điều khiển đèn thông minh**: Thuật toán tối ưu dựa trên mật độ xe thực tế
- 📝 **Hệ thống logging**: Ghi log CSV và export summary tự động
- 🎨 **Visualization chất lượng cao**:
  - Bounding boxes màu sắc
  - Zones với gradient
  - Đèn giao thông với glow effect
- ⌨️ **Điều khiển linh hoạt**: Pause, screenshot, quit
- ⚙️ **Dễ tùy chỉnh**: File config.py tập trung tất cả cài đặt

## 📄 License

Dự án này sử dụng các thư viện mã nguồn mở. Vui lòng xem file requirements.txt để biết chi tiết.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Hãy tạo issue hoặc pull request.

---

**Phát triển bởi**: Hệ thống AI Traffic Control  
**Phiên bản**: 2.0 (Nâng cấp)

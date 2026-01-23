# Quản Lý Sessions - Output Structure

## Cấu Trúc Thư Mục Mới

Từ phiên bản này, mỗi lần chạy hệ thống sẽ tạo một **session riêng biệt** với cấu trúc như sau:

```
output/
├── sessions/
│   ├── 20260123_143052/           # Session 1
│   │   ├── metadata.json          # Thông tin chi tiết session
│   │   ├── output_video.mp4       # Video đã xử lý
│   │   ├── traffic_logs.csv       # Logs chi tiết từng frame
│   │   ├── traffic_summary.txt    # Báo cáo tổng kết
│   │   ├── zones_config.json      # Cấu hình zones (nếu đã lưu)
│   │   └── screenshots/           # Folder chứa screenshots
│   │       ├── screenshot_000001.jpg
│   │       ├── screenshot_000123.jpg
│   │       └── ...
│   │
│   ├── 20260123_150234/           # Session 2
│   │   ├── metadata.json
│   │   ├── output_video.mp4
│   │   └── ...
│   │
│   └── 20260123_161545/           # Session 3
│       └── ...
```

## Lợi Ích

1. **Tổ chức rõ ràng**: Mỗi lần chạy có folder riêng, dễ phân biệt
2. **Dễ so sánh**: So sánh kết quả giữa các lần chạy khác nhau
3. **Metadata đầy đủ**: File `metadata.json` chứa tất cả thông tin quan trọng
4. **Screenshots có thứ tự**: Screenshots được đánh số theo frame, dễ tìm
5. **Không bị ghi đè**: Không lo mất dữ liệu khi chạy nhiều lần

## File metadata.json

File `metadata.json` trong mỗi session chứa thông tin:

```json
{
  "session_info": {
    "timestamp": "2026-01-23 14:30:52",
    "session_id": "20260123_143052"
  },
  "video_info": {
    "source": "intersection_video.mp4",
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "total_frames": 1500,
    "processed_frames": 1500
  },
  "detection_config": {
    "model": "yolov8n.pt",
    "confidence_threshold": 0.25
  },
  "statistics": {
    "total_vehicles_detected": 1234,
    "average_vehicles_per_frame": 12.5,
    "vehicles_by_direction": {
      "north": 310,
      "south": 298,
      "east": 315,
      "west": 311
    },
    "traffic_light_switches": 45
  },
  "output_files": {
    "video": "output_video.mp4",
    "logs": "traffic_logs.csv",
    "summary": "traffic_summary.txt",
    "zones_config": "zones_config.json"
  }
}
```

## Cấu Hình

Trong `config.py`, bạn có thể tùy chỉnh:

```python
OUTPUT_CONFIG = {
    'base_folder': 'output',              # Folder gốc
    'sessions_folder': 'sessions',        # Folder chứa sessions
    'create_session': True,               # Bật/tắt tạo session riêng
    'session_name_format': '%Y%m%d_%H%M%S',  # Format timestamp
    'create_screenshots_folder': True,    # Tạo folder screenshots riêng
    'create_metadata': True,              # Tạo metadata.json
}
```

### Tắt chức năng Sessions

Nếu muốn dùng cấu trúc cũ (tất cả files vào 1 folder):

```python
OUTPUT_CONFIG = {
    'base_folder': 'output',
    'create_session': False,  # Tắt sessions
}
```

## Session Manager - Tool Quản Lý Sessions

Script `session_manager.py` cung cấp các lệnh để quản lý sessions:

### 1. Liệt kê tất cả sessions

```bash
# Liệt kê tất cả
python session_manager.py list

# Liệt kê 10 sessions mới nhất
python session_manager.py list --limit 10

# Sắp xếp theo số frames
python session_manager.py list --sort frames
```

Output:
```
========================================================================================================================
Session ID           Timestamp            Video                          Frames     Vehicles  
========================================================================================================================
20260123_161545      2026-01-23 16:15:45  intersection_video.mp4         1500       1234      
20260123_150234      2026-01-23 15:02:34  test_video.mp4                 750        650       
20260123_143052      2026-01-23 14:30:52  demo.mp4                       2000       1890      
========================================================================================================================
Tổng số sessions: 3
```

### 2. Xem chi tiết một session

```bash
python session_manager.py view 20260123_143052
```

Output:
```
============================================================
SESSION: 20260123_143052
============================================================

[SESSION INFO]
  Timestamp: 2026-01-23 14:30:52
  Session ID: 20260123_143052

[VIDEO INFO]
  Source: intersection_video.mp4
  Resolution: 1920x1080
  FPS: 30
  Total frames: 1500
  Processed frames: 1500

[DETECTION CONFIG]
  Model: yolov8n.pt
  Confidence threshold: 0.25

[STATISTICS]
  Total vehicles detected: 1234
  Average vehicles/frame: 12.50
  Vehicles by direction:
    North: 310
    South: 298
    East: 315
    West: 311
  Traffic light switches: 45

[OUTPUT FILES]
  Video: output_video.mp4 ✓
  Logs: traffic_logs.csv ✓
  Summary: traffic_summary.txt ✓
  Zones_config: zones_config.json ✓
  Screenshots: 15 files

[SESSION PATH]
  D:\htgttm\output\sessions\20260123_143052
============================================================
```

### 3. Xem session mới nhất

```bash
python session_manager.py latest
```

### 4. So sánh nhiều sessions

```bash
python session_manager.py compare 20260123_143052 20260123_150234 20260123_161545
```

Output:
```
========================================================================================================================
SO SÁNH 3 SESSIONS
========================================================================================================================

Metric                        20260123_143052          20260123_150234          20260123_161545         
------------------------------------------------------------------------------------------------------------------------
Timestamp                     2026-01-23 14:30:52      2026-01-23 15:02:34      2026-01-23 16:15:45     
Video source                  intersection_video.mp     test_video.mp4           demo.mp4                
Processed frames              1500                     750                      2000                    
Total vehicles                1234                     650                      1890                    
Avg vehicles/frame            12.50                    8.67                     9.45                    
Light switches                45                       23                       61                      
========================================================================================================================
```

### 5. Dọn dẹp sessions cũ

```bash
# Dry run - chỉ xem sẽ xóa gì (không xóa thật)
python session_manager.py clean --keep 5

# Thực thi xóa - giữ lại 5 sessions mới nhất
python session_manager.py clean --keep 5 --execute

# Giữ lại 10 sessions mới nhất
python session_manager.py clean --keep 10 --execute
```

## Quy Trình Làm Việc Khuyến Nghị

### 1. Chạy và Test

```bash
# Chạy với video test
python main.py --video test.mp4 --show

# Kiểm tra session vừa tạo
python session_manager.py latest
```

### 2. So sánh nhiều lần chạy

```bash
# Chạy với nhiều config khác nhau
python main.py --video video1.mp4
python main.py --video video2.mp4

# Liệt kê để lấy session IDs
python session_manager.py list --limit 5

# So sánh
python session_manager.py compare <session_id_1> <session_id_2>
```

### 3. Dọn dẹp định kỳ

```bash
# Xem trước sẽ xóa gì
python session_manager.py clean --keep 10

# Thực thi xóa
python session_manager.py clean --keep 10 --execute
```

## Tích Hợp với Git

Thêm vào `.gitignore`:

```gitignore
# Ignore tất cả sessions trừ 1 session example
output/sessions/*
!output/sessions/.gitkeep
!output/sessions/example_session/
```

## Tips & Tricks

### 1. Tìm session có nhiều xe nhất

```bash
python session_manager.py list --sort frames
```

### 2. Backup sessions quan trọng

```bash
# Copy session ra ngoài
cp -r output/sessions/20260123_143052 backups/
```

### 3. Sử dụng session name tùy chỉnh

Chỉnh trong `config.py`:

```python
# Format khác: YYYYMMDD_HHMMSS_videoname
'session_name_format': '%Y%m%d_%H%M%S',
```

### 4. Export session data sang Excel

```python
import pandas as pd

# Đọc logs
df = pd.read_csv('output/sessions/20260123_143052/traffic_logs.csv')
df.to_excel('analysis.xlsx', index=False)
```

## Troubleshooting

### Sessions không được tạo?

Kiểm tra `config.py`:
```python
OUTPUT_CONFIG = {
    'create_session': True,  # Phải là True
}
```

### Metadata.json không có?

Kiểm tra:
```python
OUTPUT_CONFIG = {
    'create_metadata': True,  # Phải là True
}
```

### Folder screenshots không có?

Kiểm tra:
```python
OUTPUT_CONFIG = {
    'create_screenshots_folder': True,  # Phải là True
}
```

Hoặc bạn chưa nhấn phím `[S]` để lưu screenshot khi chạy.

## Migration từ cấu trúc cũ

Nếu bạn có dữ liệu cũ trong folder `output/`, bạn có thể:

1. **Giữ nguyên** - Đặt `create_session: False`
2. **Di chuyển** - Tạo session manual:
   ```bash
   mkdir -p output/sessions/old_data
   mv output/*.mp4 output/sessions/old_data/
   mv output/*.csv output/sessions/old_data/
   mv output/*.txt output/sessions/old_data/
   ```

---

**Ghi chú**: Cấu trúc này được thiết kế để dễ mở rộng và tích hợp với các công cụ phân tích khác như Jupyter Notebook, Pandas, hoặc các dashboard monitoring.

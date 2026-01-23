# Tóm Tắt Thay Đổi - Cấu Trúc Output Mới

## Những Gì Đã Thay Đổi

### 1. **Cấu trúc folder mới** ✨
**Trước đây:**
```
output/
├── output_video.mp4
├── traffic_logs.csv
├── traffic_summary.txt
└── screenshot_xxx.jpg
```

**Bây giờ:**
```
output/
└── sessions/
    ├── 20260123_143052/        # Mỗi lần chạy = 1 session
    │   ├── metadata.json       # ← MỚI: Thông tin chi tiết
    │   ├── output_video.mp4
    │   ├── traffic_logs.csv
    │   ├── traffic_summary.txt
    │   ├── zones_config.json
    │   └── screenshots/        # ← MỚI: Folder riêng cho screenshots
    │       ├── screenshot_000001.jpg
    │       └── ...
    │
    └── 20260123_150234/        # Session khác
        └── ...
```

### 2. **Files đã cập nhật**

#### `config.py`
```python
# CŨ
OUTPUT_CONFIG = {
    'output_folder': 'output',
    'create_timestamp_folder': False,
}

# MỚI - Nhiều tùy chọn hơn
OUTPUT_CONFIG = {
    'base_folder': 'output',
    'sessions_folder': 'sessions',
    'create_session': True,              # Bật/tắt sessions
    'session_name_format': '%Y%m%d_%H%M%S',
    'create_screenshots_folder': True,
    'create_metadata': True,
}
```

#### `main.py`
- Tự động tạo session folder với timestamp khi chạy
- Tạo folder `screenshots/` riêng
- Tạo file `metadata.json` khi kết thúc
- Screenshots được đánh số theo frame (dễ tìm hơn)

### 3. **Tool mới: session_manager.py** 🔧

Script quản lý sessions với các lệnh:

```bash
# Xem tất cả sessions
python session_manager.py list

# Xem chi tiết session
python session_manager.py view 20260123_143052

# Xem session mới nhất
python session_manager.py latest

# So sánh 2-3 sessions
python session_manager.py compare 20260123_143052 20260123_150234

# Dọn dẹp sessions cũ (giữ 5 mới nhất)
python session_manager.py clean --keep 5 --execute
```

### 4. **File metadata.json** 📄

Mỗi session có file `metadata.json` chứa:
- Thông tin session (timestamp, ID)
- Thông tin video (source, resolution, FPS, frames)
- Cấu hình detection (model, threshold)
- Thống kê (số xe, số lần chuyển đèn, v.v.)
- Danh sách output files

## Cách Sử Dụng

### Chạy bình thường (tự động tạo session)
```bash
python main.py --video test.mp4 --show
```
→ Tạo session mới: `output/sessions/20260123_143052/`

### Xem session vừa tạo
```bash
python session_manager.py latest
```

### Tắt chế độ sessions (dùng cấu trúc cũ)
Trong `config.py`:
```python
OUTPUT_CONFIG = {
    'create_session': False,  # ← Đặt False
}
```

## Lợi Ích

✅ **Không bị ghi đè**: Mỗi lần chạy có folder riêng  
✅ **Dễ so sánh**: So sánh kết quả giữa các lần chạy  
✅ **Metadata đầy đủ**: File JSON chứa mọi thông tin  
✅ **Dễ quản lý**: Tool session_manager giúp list/view/compare/clean  
✅ **Screenshots có thứ tự**: Đánh số theo frame thay vì timestamp  
✅ **Dễ backup**: Copy cả folder session là xong  

## Tài Liệu

Xem chi tiết trong `SESSIONS_GUIDE.md` với:
- Hướng dẫn đầy đủ từng lệnh
- Ví dụ cụ thể
- Tips & tricks
- Troubleshooting

## Backward Compatibility

Code cũ vẫn hoạt động! Nếu không muốn dùng sessions:
```python
OUTPUT_CONFIG = {
    'base_folder': 'output',
    'create_session': False,  # Tắt sessions
}
```

---

**Ghi chú**: Tất cả thay đổi đều backward compatible. Bạn có thể tắt sessions bất cứ lúc nào trong `config.py`.

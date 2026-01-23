# 📹 Yêu Cầu Video Đầu Vào

Tài liệu này mô tả các yêu cầu và khuyến nghị cho video đầu vào của hệ thống.

## ✅ Định dạng được hỗ trợ

Hệ thống hỗ trợ các định dạng video phổ biến:

- **MP4** (.mp4) - **Khuyến nghị**
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- FLV (.flv)
- WMV (.wmv)
- WEBM (.webm)

## 📋 Yêu cầu kỹ thuật

### 1. Kích thước và độ phân giải
- **Tối thiểu**: 320x240 pixels
- **Khuyến nghị**: 1280x720 (HD) hoặc 1920x1080 (Full HD)
- **Tối đa**: Không giới hạn (nhưng video lớn sẽ xử lý chậm hơn)

### 2. Frame Rate (FPS)
- **Khuyến nghị**: 24-30 FPS
- Hệ thống tự động phát hiện FPS, nếu không có sẽ dùng mặc định 30 FPS

### 3. Codec Video
- **Khuyến nghị**: H.264 (MPEG-4 AVC)
- Các codec khác có thể hoạt động nhưng có thể gặp vấn đề khi ghi output

### 4. Nội dung video
- **Góc nhìn**: Video nên có góc nhìn rõ ràng của ngã tư
- **Ánh sáng**: Đủ ánh sáng để nhận diện xe tốt
- **Chất lượng**: Video rõ nét, không quá mờ hoặc nhiễu

## 🎥 Sử dụng Webcam

Bạn có thể sử dụng webcam thay vì video file:

```bash
python main.py --video 0 --show
```

**Lưu ý khi dùng webcam:**
- Webcam phải được kết nối và hoạt động
- Đảm bảo webcam có quyền truy cập
- FPS có thể thay đổi tùy theo webcam

## ⚠️ Xử lý lỗi thường gặp

### 1. "Không thể mở video"
**Nguyên nhân:**
- File không tồn tại
- Đường dẫn sai
- File bị hỏng
- Codec không được hỗ trợ

**Giải pháp:**
- Kiểm tra đường dẫn file
- Thử chuyển đổi video sang định dạng MP4 với codec H.264
- Sử dụng tool như FFmpeg để chuyển đổi:
  ```bash
  ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4
  ```

### 2. "Video có kích thước không hợp lệ"
**Nguyên nhân:**
- File video bị hỏng
- File không phải là video hợp lệ

**Giải pháp:**
- Kiểm tra file có phải video thật không
- Thử mở bằng trình phát video khác
- Chuyển đổi lại video

### 3. "Không thể ghi video output"
**Nguyên nhân:**
- Codec không được hỗ trợ
- Không có quyền ghi file
- Ổ đĩa đầy

**Giải pháp:**
- Hệ thống sẽ tự động thử các codec khác
- Kiểm tra quyền ghi file trong thư mục
- Kiểm tra dung lượng ổ đĩa

### 4. Video chạy nhưng không nhận diện được xe
**Nguyên nhân:**
- Video quá tối
- Góc nhìn không tốt
- Xe quá nhỏ trong frame

**Giải pháp:**
- Cải thiện ánh sáng
- Điều chỉnh góc camera
- Sử dụng video có độ phân giải cao hơn

## 🔧 Chuyển đổi video với FFmpeg

Nếu video của bạn không tương thích, sử dụng FFmpeg để chuyển đổi:

### Chuyển sang MP4 (H.264):
```bash
ffmpeg -i input_video.avi -c:v libx264 -preset medium -crf 23 -c:a aac -b:a 128k output.mp4
```

### Giảm kích thước video:
```bash
ffmpeg -i input.mp4 -vf scale=1280:720 -c:v libx264 -crf 28 output.mp4
```

### Cắt video:
```bash
ffmpeg -i input.mp4 -ss 00:00:10 -t 00:01:00 -c copy output.mp4
```

## 📝 Checklist trước khi sử dụng

- [ ] Video có định dạng được hỗ trợ
- [ ] File video tồn tại và có thể mở được
- [ ] Video có góc nhìn rõ ràng của ngã tư
- [ ] Ánh sáng đủ để nhìn thấy xe
- [ ] Độ phân giải hợp lý (không quá thấp)
- [ ] Có đủ dung lượng ổ đĩa để lưu output

## 💡 Mẹo tối ưu

1. **Sử dụng MP4 với H.264**: Định dạng này được hỗ trợ tốt nhất
2. **Độ phân giải vừa phải**: 720p-1080p là lý tưởng, không cần 4K
3. **FPS ổn định**: 24-30 FPS là đủ, không cần 60 FPS
4. **Góc nhìn tốt**: Camera nên ở vị trí cao để nhìn rõ ngã tư
5. **Ánh sáng đủ**: Tránh video quá tối hoặc quá sáng

## 🆘 Hỗ trợ

Nếu gặp vấn đề với video, vui lòng:
1. Kiểm tra log lỗi trong console
2. Thử với video mẫu khác
3. Kiểm tra các yêu cầu ở trên
4. Chuyển đổi video sang định dạng MP4 (H.264)

"""
Script chính để chạy hệ thống nhận diện xe và điều khiển đèn giao thông
Phiên bản nâng cấp với giao diện đẹp và đầy đủ tính năng
"""
import cv2
import argparse
import time
import os
import numpy as np
from vehicle_detector import VehicleDetector
from traffic_counter import TrafficCounter
from traffic_light_controller import TrafficLightController
from ui_dashboard import Dashboard
from logger import TrafficLogger
from zone_editor import ZoneEditor
from config import COLORS, UI_CONFIG, OUTPUT_CONFIG, DETECTION_CONFIG


class TrafficControlSystem:
    def __init__(self, video_path, model_path=None, output_path=None, show=True):
        """
        Khởi tạo hệ thống
        
        Args:
            video_path: Đường dẫn video
            model_path: Đường dẫn model YOLOv8n
            output_path: Đường dẫn output video
            show: Hiển thị video
        """
        self.video_path = video_path
        self.model_path = model_path
        self.show = show
        
        # Tạo output folder với cấu trúc session
        from datetime import datetime
        self.session_timestamp = datetime.now()
        
        base_folder = OUTPUT_CONFIG.get('base_folder', 'output')
        
        if OUTPUT_CONFIG.get('create_session', True):
            # Tạo session folder với timestamp
            sessions_folder = OUTPUT_CONFIG.get('sessions_folder', 'sessions')
            session_name = self.session_timestamp.strftime(
                OUTPUT_CONFIG.get('session_name_format', '%Y%m%d_%H%M%S')
            )
            self.output_folder = os.path.join(base_folder, sessions_folder, session_name)
        else:
            # Fallback: đặt trực tiếp vào base folder
            self.output_folder = base_folder
        
        os.makedirs(self.output_folder, exist_ok=True)
        
        # Tạo folder cho screenshots nếu cần
        if OUTPUT_CONFIG.get('create_screenshots_folder', True):
            self.screenshots_folder = os.path.join(self.output_folder, 'screenshots')
            os.makedirs(self.screenshots_folder, exist_ok=True)
        else:
            self.screenshots_folder = self.output_folder
        
        # Đặt output path trong folder
        if output_path:
            if not os.path.isabs(output_path) and os.path.dirname(output_path) == '':
                # Nếu chỉ có tên file, đặt vào output folder
                self.output_path = os.path.join(self.output_folder, output_path)
            else:
                self.output_path = output_path
        else:
            self.output_path = os.path.join(self.output_folder, 'output_video.mp4')
        
        # Khởi tạo các component
        print("=" * 60)
        print("HE THONG NHAN DIEN XE VA DIEU KHIEN DEN GIAO THONG")
        print("=" * 60)
        print("\nĐang khởi tạo các module...")
        
        print("  [1/5] Đang tải model YOLOv8n...")
        self.detector = VehicleDetector(model_path=model_path)
        
        print("  [2/5] Đang mở video...")
        
        # Kiểm tra video path
        is_webcam = isinstance(video_path, int) or (isinstance(video_path, str) and video_path.isdigit())
        
        if not is_webcam:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Không tìm thấy file video: {video_path}")
            
            # Kiểm tra extension
            valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm']
            file_ext = os.path.splitext(video_path)[1].lower()
            if file_ext not in valid_extensions:
                print(f"⚠️  Cảnh báo: Extension '{file_ext}' có thể không được hỗ trợ. Đề xuất: {', '.join(valid_extensions)}")
        
        # Mở video
        video_input = int(video_path) if is_webcam else video_path
        self.cap = cv2.VideoCapture(video_input)
        
        if not self.cap.isOpened():
            if is_webcam:
                raise ValueError(f"Không thể mở webcam: {video_path}. Kiểm tra webcam có được kết nối không.")
            else:
                raise ValueError(f"Không thể mở video: {video_path}. File có thể bị hỏng hoặc codec không được hỗ trợ.")
        
        # Lấy thông tin video
        self.fps_video = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps_video <= 0 or self.fps_video > 120:
            self.fps_video = 30  # Default FPS
            print(f"     ⚠️  Không thể đọc FPS, sử dụng mặc định: {self.fps_video}fps")
        else:
            self.fps_video = int(self.fps_video)
        
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Kiểm tra kích thước hợp lệ
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Video có kích thước không hợp lệ: {self.width}x{self.height}. File có thể bị hỏng.")
        
        # Hiển thị thông tin
        if is_webcam:
            print(f"     Webcam: {self.width}x{self.height} @ {self.fps_video}fps")
        else:
            frames_info = f"({self.total_frames} frames)" if self.total_frames > 0 else "(unknown length)"
            print(f"     Video: {self.width}x{self.height} @ {self.fps_video}fps {frames_info}")
        
        # Kiểm tra video writer
        if not self._check_video_writer():
            print("     ⚠️  Cảnh báo: Có thể không ghi được video output. Kiểm tra codec và quyền ghi file.")
        
        print("  [3/5] Đang khởi tạo Traffic Counter...")
        self.counter = TrafficCounter(frame_shape=(self.height, self.width))
        
        print("  [4/5] Đang khởi tạo Traffic Light Controller...")
        self.controller = TrafficLightController()
        
        print("  [5/5] Đang khởi tạo Dashboard và Logger...")
        self.dashboard = Dashboard(frame_shape=(self.height, self.width))
        
        # Logger với output folder
        log_file = os.path.join(self.output_folder, 'traffic_logs.csv')
        self.logger = TrafficLogger(log_file=log_file)
        
        # Zone editor
        self.zone_editor = ZoneEditor(self.counter.zones, (self.height, self.width))
        self.edit_zones_mode = False
        self.show_dashboard = True
        
        # Setup video writer
        self.out = self._create_video_writer()
        
        # Thống kê
        self.frame_count = 0
        self.fps = 0
        self.fps_start_time = time.time()
        self.fps_frame_count = 0
        
        # Cấu hình cửa sổ hiển thị
        self.fixed_window_size = UI_CONFIG.get('fixed_window_size', True)
        self.window_width = UI_CONFIG.get('window_width', 1280)
        self.window_height = UI_CONFIG.get('window_height', 720)
        
        # Tạo cửa sổ với kích thước cố định nếu cần
        if self.show and self.fixed_window_size:
            cv2.namedWindow('Traffic Control System', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Traffic Control System', self.window_width, self.window_height)
            # Set mouse callback cho zone editor
            cv2.setMouseCallback('Traffic Control System', self._mouse_callback)
            self._update_frame_on_edit = False
        
        print("\n✓ Khởi tạo hoàn tất!\n")
    
    def _check_video_writer(self):
        """Kiểm tra video writer có hoạt động không"""
        try:
            test_writer = cv2.VideoWriter('test_write.mp4', 
                                         cv2.VideoWriter_fourcc(*'mp4v'), 
                                         self.fps_video, 
                                         (self.width, self.height))
            if test_writer.isOpened():
                test_writer.release()
                if os.path.exists('test_write.mp4'):
                    os.remove('test_write.mp4')
                return True
            return False
        except:
            return False
    
    def _create_video_writer(self):
        """Tạo video writer với codec phù hợp"""
        # Thử các codec khác nhau
        codecs = [
            ('mp4v', '.mp4'),
            ('XVID', '.avi'),
            ('MJPG', '.avi'),
        ]
        
        for codec_name, ext in codecs:
            try:
                # Đổi extension nếu cần
                output_path = self.output_path
                if not output_path.endswith(ext):
                    base_name = os.path.splitext(output_path)[0]
                    output_path = base_name + ext
                    print(f"     Đổi output format sang {ext}")
                
                fourcc = cv2.VideoWriter_fourcc(*codec_name)
                writer = cv2.VideoWriter(output_path, fourcc, self.fps_video, (self.width, self.height))
                
                if writer.isOpened():
                    self.output_path = output_path  # Cập nhật output path
                    return writer
                else:
                    writer.release()
            except Exception as e:
                continue
        
        # Nếu không codec nào hoạt động, tạo writer với codec mặc định
        print("     ⚠️  Không tìm được codec phù hợp, sử dụng codec mặc định")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        return cv2.VideoWriter(self.output_path, fourcc, self.fps_video, (self.width, self.height))
    
    def calculate_fps(self):
        """Tính toán FPS"""
        self.fps_frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.fps_start_time
        
        if elapsed >= 1.0:
            self.fps = self.fps_frame_count / elapsed
            self.fps_frame_count = 0
            self.fps_start_time = current_time
    
    def _mouse_callback(self, event, x, y, flags, param):
        """Callback cho mouse events"""
        if self.edit_zones_mode:
            # Điều chỉnh tọa độ nếu có dashboard
            if self.show_dashboard:
                x = x - UI_CONFIG['dashboard_width']
                if x < 0:
                    return
            self.zone_editor.handle_mouse_event(event, x, y, flags, param)
    
    def _resize_for_display(self, frame):
        """
        Resize frame để hiển thị với kích thước cố định, giữ nguyên tỷ lệ
        
        Args:
            frame: Frame gốc
            
        Returns:
            Frame đã được resize
        """
        if not self.fixed_window_size:
            return frame
        
        h, w = frame.shape[:2]
        target_w = self.window_width
        target_h = self.window_height
        
        # Tính tỷ lệ để giữ nguyên aspect ratio
        scale_w = target_w / w
        scale_h = target_h / h
        scale = min(scale_w, scale_h)  # Chọn scale nhỏ hơn để fit vào cửa sổ
        
        # Tính kích thước mới
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize frame
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Tạo frame với kích thước cố định và padding nếu cần
        if new_w != target_w or new_h != target_h:
            # Tạo frame đen với kích thước cố định
            display_frame = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            
            # Tính vị trí để căn giữa
            y_offset = (target_h - new_h) // 2
            x_offset = (target_w - new_w) // 2
            
            # Đặt frame đã resize vào giữa
            display_frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            
            return display_frame
        
        return resized
    
    def draw_info_overlay(self, frame):
        """Vẽ thông tin overlay lên frame"""
        # Vẽ header bar
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (UI_CONFIG['dashboard_width'], 0),
            (self.width, 50),
            COLORS['background'],
            -1
        )
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
        
        # Vẽ border
        cv2.line(
            frame,
            (UI_CONFIG['dashboard_width'], 0),
            (UI_CONFIG['dashboard_width'], self.height),
            COLORS['primary'],
            3
        )
        
        # Thông tin frame
        progress = (self.frame_count / self.total_frames * 100) if self.total_frames > 0 else 0
        info_text = f"Frame: {self.frame_count}/{self.total_frames} ({progress:.1f}%)"
        
        cv2.putText(
            frame, info_text,
            (UI_CONFIG['dashboard_width'] + 10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,
            COLORS['text'], 2
        )
        
        return frame
    
    def process_frame(self, frame, skip_detection=False):
        """
        Xử lý một frame
        
        Args:
            frame: Frame video
            skip_detection: Nếu True, bỏ qua detection và counting (chỉ vẽ zones)
        """
        if not skip_detection:
            # Nhận diện xe
            detections = self.detector.detect(frame)
            
            # Cập nhật zones từ editor nếu đang chỉnh sửa
            if self.edit_zones_mode:
                self.counter.zones = self.zone_editor.get_zones()
            
            # Đếm xe theo hướng
            vehicle_counts = self.counter.count_vehicles(detections)
            
            # Tính toán trạng thái đèn
            light_states = self.controller.get_light_state(vehicle_counts)
            
            # Vẽ detections
            frame = self.detector.draw_detections(frame, detections)
            
            # Vẽ trạng thái đèn
            frame = self.controller.draw_lights(frame, light_states, (self.height, self.width))
            
            # Lấy thống kê (cần cho logging)
            vehicle_stats = self.detector.get_statistics()
            traffic_stats = self.counter.get_statistics()
            light_stats = self.controller.get_statistics(vehicle_counts)
            
            # Vẽ dashboard nếu bật
            if self.show_dashboard:
                frame = self.dashboard.draw_dashboard(
                    frame, vehicle_stats, traffic_stats, light_stats, self.fps
                )
            
            # Logging
            self.logger.log(vehicle_counts, light_stats, self.fps)
        else:
            # Khi skip_detection, chỉ cập nhật zones và vẽ
            if self.edit_zones_mode:
                self.counter.zones = self.zone_editor.get_zones()
        
        # Vẽ zones - dùng editor nếu đang chỉnh sửa
        if self.edit_zones_mode:
            frame = self.zone_editor.draw_zones_editable(frame)
        else:
            frame = self.counter.draw_zones(frame)
        
        # Vẽ info overlay
        frame = self.draw_info_overlay(frame)
        
        # Hiển thị thông báo chế độ chỉnh sửa
        if self.edit_zones_mode:
            cv2.putText(frame, "CHE DO CHINH SUA ZONES - Nhan [E] de thoat",
                       (10, self.height - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       COLORS['warning'], 2)
        
        return frame
    
    def run(self):
        """Chạy hệ thống"""
        print("Bắt đầu xử lý video...")
        print("Điều khiển:")
        print("  [Q] - Thoát")
        print("  [SPACE] - Tạm dừng/Tiếp tục")
        print("  [S] - Lưu screenshot")
        print("  [D] - Ẩn/Hiện Dashboard")
        print("  [E] - Chế độ chỉnh sửa Zones (kéo thả để di chuyển)")
        print("  [R] - Lưu zones hiện tại")
        print("-" * 60)
        
        paused = False
        current_frame = None  # Lưu frame hiện tại khi pause
        
        try:
            while True:
                if not paused:
                    ret, frame = self.cap.read()
                    if not ret:
                        # Kiểm tra nếu là webcam thì có thể chỉ là frame trống tạm thời
                        if isinstance(self.video_path, int) or (isinstance(self.video_path, str) and self.video_path.isdigit()):
                            print("\n⚠️  Không đọc được frame từ webcam. Kiểm tra kết nối.")
                            time.sleep(0.1)
                            continue
                        else:
                            print("\n✓ Đã xử lý hết video!")
                            break
                    
                    # Kiểm tra frame hợp lệ
                    if frame is None or frame.size == 0:
                        print("⚠️  Frame rỗng, bỏ qua...")
                        continue
                    
                    self.frame_count += 1
                    
                    # Lưu frame gốc (chưa xử lý) để dùng khi pause
                    current_frame = frame.copy()
                    
                    # Xử lý frame
                    frame = self.process_frame(frame)
                    
                    # Tính FPS
                    self.calculate_fps()
                    
                    # Ghi frame vào output video
                    self.out.write(frame)
                    
                    # Progress indicator
                    if self.frame_count % 30 == 0:
                        if self.total_frames > 0:
                            progress = (self.frame_count / self.total_frames * 100)
                            print(f"Đã xử lý: {self.frame_count}/{self.total_frames} frames ({progress:.1f}%) | FPS: {self.fps:.1f}")
                        else:
                            print(f"Đã xử lý: {self.frame_count} frames | FPS: {self.fps:.1f}")
                else:
                    # Khi paused, chỉ vẽ lại zones (không chạy detection và counting)
                    if current_frame is not None:
                        frame = self.process_frame(current_frame.copy(), skip_detection=True)
                
                # Hiển thị frame (luôn hiển thị khi paused để có thể chỉnh sửa)
                if self.show or paused:
                    # Resize frame về kích thước cố định nếu cần
                    display_frame = self._resize_for_display(frame)
                    cv2.imshow('Traffic Control System', display_frame)
                    
                    # Khi paused, dùng waitKey với timeout ngắn để có thể chỉnh sửa zones
                    # và cập nhật frame liên tục (chỉ vẽ zones, không chạy detection)
                    if paused:
                        # Xử lý lại frame để cập nhật zones (skip detection)
                        if current_frame is not None:
                            frame = self.process_frame(current_frame.copy(), skip_detection=True)
                            display_frame = self._resize_for_display(frame)
                            cv2.imshow('Traffic Control System', display_frame)
                        wait_time = 10  # 10ms để cập nhật frame liên tục
                    else:
                        wait_time = 1
                    
                    key = cv2.waitKey(wait_time) & 0xFF
                    if key == ord('q'):
                        print("\nĐã dừng bởi người dùng")
                        break
                    elif key == ord(' '):
                        paused = not paused
                        print(f"  {'Tạm dừng' if paused else 'Tiếp tục'}")
                    elif key == ord('s'):
                        screenshot_path = os.path.join(
                            self.screenshots_folder, 
                            f'screenshot_{self.frame_count:06d}.jpg'
                        )
                        cv2.imwrite(screenshot_path, frame)
                        print(f"  Đã lưu screenshot: {screenshot_path}")
                    elif key == ord('d'):
                        self.show_dashboard = not self.show_dashboard
                        print(f"  Dashboard: {'Hiện' if self.show_dashboard else 'Ẩn'}")
                    elif key == ord('e'):
                        self.edit_zones_mode = not self.edit_zones_mode
                        if self.edit_zones_mode:
                            # Cập nhật zones vào editor
                            self.zone_editor.zones = self.counter.zones.copy()
                            print("  Chế độ chỉnh sửa zones: BẬT")
                            print("    - Click và kéo điểm để di chuyển")
                            print("    - Click vào zone để di chuyển toàn bộ")
                            print("    - Nhấn [E] để tắt chế độ chỉnh sửa")
                        else:
                            # Cập nhật zones vào counter
                            self.counter.zones = self.zone_editor.get_zones()
                            print("  Chế độ chỉnh sửa zones: TẮT")
                    elif key == ord('r') and self.edit_zones_mode:
                        zones_file = os.path.join(self.output_folder, 'zones_config.json')
                        self.zone_editor.save_zones(zones_file)
                        print(f"  Đã lưu zones vào: {zones_file}")
        
        except KeyboardInterrupt:
            print("\n\nĐã dừng xử lý (Ctrl+C)")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Dọn dẹp tài nguyên"""
        print("\n" + "=" * 60)
        print("Đang dọn dẹp...")
        
        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        
        # Export summary
        summary_file = os.path.join(self.output_folder, 'traffic_summary.txt')
        self.logger.export_summary(summary_file)
        
        # Tạo metadata cho session nếu cần
        if OUTPUT_CONFIG.get('create_metadata', True):
            self._create_session_metadata()
        
        # Thống kê cuối cùng
        vehicle_stats = self.detector.get_statistics()
        traffic_stats = self.counter.get_statistics()
        light_stats = self.controller.get_statistics(vehicle_counts={})
        
        print("\n" + "=" * 60)
        print("THỐNG KÊ CUỐI CÙNG")
        print("=" * 60)
        print(f"Tổng số frames đã xử lý: {self.frame_count}")
        print(f"Tổng số xe phát hiện: {vehicle_stats['total']}")
        print(f"Trung bình xe/frame: {vehicle_stats['average_per_frame']:.2f}")
        print(f"\nTổng số xe đếm được theo hướng:")
        for direction, count in traffic_stats['total'].items():
            direction_name = {
                'north': 'North', 'south': 'South',
                'east': 'East', 'west': 'West'
            }.get(direction, direction)
            print(f"  {direction_name}: {count}")
        print(f"\nSố lần chuyển đèn: {light_stats['switch_count']}")
        print(f"\nSession folder: {self.output_folder}")
        print(f"Video output: {self.output_path}")
        print(f"Log file: {self.logger.log_file}")
        print(f"Summary file: {summary_file}")
        print("=" * 60)
    
    def _create_session_metadata(self):
        """Tạo file metadata.json cho session"""
        import json
        
        # Lấy thống kê cuối cùng
        vehicle_stats = self.detector.get_statistics()
        traffic_stats = self.counter.get_statistics()
        light_stats = self.controller.get_statistics(vehicle_counts={})
        
        # Lấy thông tin video
        video_name = os.path.basename(self.video_path) if isinstance(self.video_path, str) else f"webcam_{self.video_path}"
        
        # Tạo metadata
        metadata = {
            'session_info': {
                'timestamp': self.session_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'session_id': os.path.basename(self.output_folder),
            },
            'video_info': {
                'source': video_name,
                'width': self.width,
                'height': self.height,
                'fps': self.fps_video,
                'total_frames': self.total_frames,
                'processed_frames': self.frame_count,
            },
            'detection_config': {
                'model': self.model_path if self.model_path else 'yolov8n.pt',
                'confidence_threshold': DETECTION_CONFIG.get('confidence_threshold', 0.25),
            },
            'statistics': {
                'total_vehicles_detected': vehicle_stats['total'],
                'average_vehicles_per_frame': vehicle_stats['average_per_frame'],
                'vehicles_by_direction': traffic_stats['total'],
                'traffic_light_switches': light_stats['switch_count'],
            },
            'output_files': {
                'video': os.path.basename(self.output_path),
                'logs': 'traffic_logs.csv',
                'summary': 'traffic_summary.txt',
                'zones_config': 'zones_config.json' if os.path.exists(
                    os.path.join(self.output_folder, 'zones_config.json')
                ) else None,
            }
        }
        
        # Lưu metadata
        metadata_file = os.path.join(self.output_folder, 'metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Metadata file: {metadata_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Hệ thống nhận diện xe và điều khiển đèn giao thông - Phiên bản nâng cấp',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  python main.py --video intersection.mp4 --show
  python main.py --video intersection.mp4 --output result.mp4
  python main.py --video 0  # Sử dụng webcam
        """
    )
    
    parser.add_argument('--video', type=str, default='intersection_video.mp4',
                       help='Đường dẫn đến video ngã tư hoặc số webcam (mặc định: intersection_video.mp4)')
    parser.add_argument('--model', type=str, default=None,
                       help='Đường dẫn đến model YOLOv8n (mặc định: yolov8n.pt)')
    parser.add_argument('--output', type=str, default='output_video.mp4',
                       help='Đường dẫn lưu video output (mặc định: output_video.mp4)')
    parser.add_argument('--show', action='store_true', default=True,
                       help='Hiển thị video trong khi xử lý (mặc định: True)')
    parser.add_argument('--no-show', dest='show', action='store_false',
                       help='Không hiển thị video')
    
    args = parser.parse_args()
    
    # Xử lý video path (có thể là số webcam)
    try:
        if args.video.isdigit():
            video_path = int(args.video)
        else:
            video_path = args.video
            # Kiểm tra đường dẫn tuyệt đối hoặc tương đối
            if not os.path.isabs(video_path):
                # Thử tìm trong thư mục hiện tại
                if not os.path.exists(video_path):
                    print(f"⚠️  Không tìm thấy file: {video_path}")
                    print(f"   Đang tìm trong thư mục hiện tại: {os.getcwd()}")
    except Exception as e:
        video_path = args.video
        print(f"⚠️  Lỗi xử lý video path: {e}")
    
    try:
        system = TrafficControlSystem(
            video_path=video_path,
            model_path=args.model,
            output_path=args.output,
            show=args.show
        )
        system.run()
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

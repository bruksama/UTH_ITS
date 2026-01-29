"""
Module tạo dashboard hiển thị thống kê và thông tin - Phiên bản đơn giản
"""
import cv2
import numpy as np
from config import COLORS, UI_CONFIG


class Dashboard:
    def __init__(self, frame_shape):
        """
        Khởi tạo dashboard
        
        Args:
            frame_shape: Kích thước frame (height, width)
        """
        self.height, self.width = frame_shape[:2]
        self.dashboard_width = UI_CONFIG['dashboard_width']
        
    def draw_dashboard(self, frame, vehicle_stats, traffic_stats, light_stats, fps=0):
        """
        Vẽ dashboard đơn giản lên frame
        
        Args:
            frame: Frame video
            vehicle_stats: Thống kê từ VehicleDetector
            traffic_stats: Thống kê từ TrafficCounter
            light_stats: Thống kê từ TrafficLightController
            fps: FPS hiện tại
            
        Returns:
            Frame đã được vẽ dashboard
        """
        try:
            # Vẽ background panel đơn giản
            overlay = frame.copy()
            cv2.rectangle(
                overlay,
                (0, 0),
                (self.dashboard_width, self.height),
                (20, 20, 20),  # Màu tối đơn giản
                -1
            )
            cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
            
            y = 20
            
            # FPS đơn giản
            if UI_CONFIG['show_fps']:
                fps_text = f"FPS: {fps:.0f}" if fps and fps > 0 else "FPS: 0"
                cv2.putText(frame, fps_text, (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                y += 25
            
            # Đếm xe theo hướng - đơn giản
            y += 10
            cv2.putText(frame, "VEHICLES", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
            y += 20
            
            direction_names = {
                'north': 'North',
                'south': 'South',
                'east': 'East',
                'west': 'West'
            }
            
            # Đảm bảo traffic_stats có current
            if not traffic_stats or 'current' not in traffic_stats:
                traffic_stats = {'current': {'north': 0, 'south': 0, 'east': 0, 'west': 0}}
            
            for direction in ['north', 'south', 'east', 'west']:
                count = traffic_stats['current'].get(direction, 0)
                name = direction_names.get(direction, direction)
                
                text = f"{name}: {count}"
                cv2.putText(frame, text, (15, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
                y += 18
            
            # Đèn giao thông - cải thiện
            y += 15
            cv2.putText(frame, "TRAFFIC LIGHT", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
            y += 20
            
            # Hiển thị cặp hướng đang xanh - dùng ASCII để tránh lỗi encoding
            pair_names = {
                'north_south': 'Bac-Nam',
                'east_west': 'Dong-Tay'
            }
            
            # Đảm bảo các giá trị là kiểu đúng
            if not light_stats:
                # Nếu light_stats là None hoặc rỗng, dùng giá trị mặc định
                current_green = 'north_south'
                is_yellow = False
                remaining = 0
                elapsed = 0
                progress = 0
                min_time = 5
                max_time = 30
                switch_reason = None
            else:
                try:
                    current_green = str(light_stats.get('current_green', 'north_south'))
                    is_yellow = bool(light_stats.get('is_yellow', False))
                    remaining = float(light_stats.get('remaining_time', 0))
                    elapsed = float(light_stats.get('elapsed_time', 0))
                    progress = float(light_stats.get('progress_percent', 0))
                    min_time = float(light_stats.get('min_time', 5))
                    max_time = float(light_stats.get('max_time', 30))
                    switch_reason = light_stats.get('switch_reason', None)
                except (ValueError, TypeError, AttributeError):
                    # Nếu có lỗi chuyển đổi kiểu, dùng giá trị mặc định
                    current_green = 'north_south'
                    is_yellow = False
                    remaining = 0
                    elapsed = 0
                    progress = 0
                    min_time = 5
                    max_time = 30
                    switch_reason = None
            
            direction_text = pair_names.get(current_green, current_green)
            state_text = "VANG" if is_yellow else "XANH"
            
            # Hiển thị cặp hướng và trạng thái với màu sắc tương ứng
            state_color = (255, 255, 100) if is_yellow else (100, 255, 100)  # Vàng hoặc Xanh lá
            
            cv2.putText(frame, f"{direction_text}: {state_text}", (15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, state_color, 2)
            y += 22
            
            # Hiển thị thời gian đã chạy / tối đa
            elapsed_safe = elapsed if elapsed is not None else 0
            max_time_safe = max_time if max_time is not None else 30
            time_text = f"{elapsed_safe:.0f}s / {max_time_safe:.0f}s"
            cv2.putText(frame, time_text, (15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (100, 200, 255), 1)
            y += 18
            
            # Progress bar
            bar_width = self.dashboard_width - 30
            bar_height = 8
            bar_x = 15
            bar_y = y
            
            # Background bar
            cv2.rectangle(frame, (bar_x, bar_y), 
                         (bar_x + bar_width, bar_y + bar_height),
                         (60, 60, 60), -1)
            
            # Progress bar (màu thay đổi theo thời gian)
            progress_safe = progress if progress is not None else 0
            progress_width = int((progress_safe / 100) * bar_width) if progress_safe else 0
            if progress_safe < 50:
                bar_color = (50, 255, 50)  # Xanh lá - còn nhiều thời gian
            elif progress_safe < 80:
                bar_color = (50, 200, 255)  # Cam - gần hết thời gian
            else:
                bar_color = (50, 100, 255)  # Đỏ - sắp hết thời gian
            
            cv2.rectangle(frame, (bar_x, bar_y),
                         (bar_x + progress_width, bar_y + bar_height),
                         bar_color, -1)
            
            # Border
            cv2.rectangle(frame, (bar_x, bar_y),
                         (bar_x + bar_width, bar_y + bar_height),
                         (150, 150, 150), 1)
            
            y += bar_height + 12
            
            # Hiển thị phần trăm và thời gian còn lại
            remaining_safe = remaining if remaining is not None else 0
            percent_text = f"{progress_safe:.0f}% - Con lai: {remaining_safe:.0f}s"
            cv2.putText(frame, percent_text, (15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
            y += 16
            
            # Hiển thị lý do sắp chuyển đèn (nếu có)
            if switch_reason and elapsed_safe >= min_time:
                # Giới hạn độ dài text để tránh lỗi
                reason_text = str(switch_reason)[:40]  # Giới hạn 40 ký tự
                cv2.putText(frame, f"! {reason_text}", (15, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 150, 255), 1)
            
        except Exception as e:
            # Nếu có lỗi, vẽ thông báo lỗi đơn giản
            cv2.putText(frame, "Dashboard Error", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            print(f"Dashboard error: {e}")
        
        return frame

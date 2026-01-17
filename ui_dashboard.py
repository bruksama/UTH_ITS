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
        
        # Vẽ border đơn giản
        cv2.line(frame, (self.dashboard_width, 0), (self.dashboard_width, self.height), 
                (100, 100, 100), 1)
        
        y = 20
        
        # FPS đơn giản
        if UI_CONFIG['show_fps']:
            fps_text = f"FPS: {fps:.0f}"
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
        
        current_green = light_stats.get('current_green', 'north')
        is_yellow = light_stats.get('is_yellow', False)
        remaining = light_stats.get('remaining_time', 0)
        elapsed = light_stats.get('elapsed_time', 0)
        progress = light_stats.get('progress_percent', 0)
        min_time = light_stats.get('min_time', 0)
        max_time = light_stats.get('max_time', 0)
        switch_reason = light_stats.get('switch_reason', None)
        
        direction_text = direction_names.get(current_green, current_green)
        state_text = "YELLOW" if is_yellow else "GREEN"
        
        # Hiển thị hướng và trạng thái
        cv2.putText(frame, f"{direction_text}: {state_text}", (15, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        y += 18
        
        # Hiển thị thời gian đã chạy / tối đa
        time_text = f"{elapsed:.0f}s / {max_time:.0f}s"
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
        progress_width = int((progress / 100) * bar_width)
        if progress < 50:
            bar_color = (50, 255, 50)  # Xanh lá - còn nhiều thời gian
        elif progress < 80:
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
        percent_text = f"{progress:.0f}% - Con lai: {remaining:.0f}s"
        cv2.putText(frame, percent_text, (15, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        y += 16
        
        # Hiển thị lý do sắp chuyển đèn (nếu có)
        if switch_reason and elapsed >= min_time:
            cv2.putText(frame, f"! {switch_reason}", (15, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, (100, 150, 255), 1)
        
        return frame

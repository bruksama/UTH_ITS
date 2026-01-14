"""
Module tạo dashboard hiển thị thống kê và thông tin
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
        Vẽ dashboard lên frame
        
        Args:
            frame: Frame video
            vehicle_stats: Thống kê từ VehicleDetector
            traffic_stats: Thống kê từ TrafficCounter
            light_stats: Thống kê từ TrafficLightController
            fps: FPS hiện tại
            
        Returns:
            Frame đã được vẽ dashboard
        """
        # Tạo overlay cho dashboard
        overlay = frame.copy()
        
        # Vẽ background panel bên trái
        cv2.rectangle(
            overlay,
            (0, 0),
            (self.dashboard_width, self.height),
            COLORS['background'],
            -1
        )
        
        # Blend overlay
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        
        # Vẽ border
        cv2.rectangle(
            frame,
            (0, 0),
            (self.dashboard_width, self.height),
            COLORS['primary'],
            3
        )
        
        y_offset = 30
        
        # Title
        title = "DASHBOARD"
        cv2.putText(
            frame, title,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8,
            COLORS['primary'], 2
        )
        y_offset += 40
        
        # FPS
        if UI_CONFIG['show_fps']:
            fps_text = f"FPS: {fps:.1f}"
            cv2.putText(
                frame, fps_text,
                (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                COLORS['text'], 2
            )
            y_offset += 30
        
        # Vehicle Detection Stats
        y_offset = self._draw_section(
            frame, "NHAN DIEN XE",
            [
                f"Tong: {vehicle_stats.get('total', 0)}",
                f"Trung binh: {vehicle_stats.get('average_per_frame', 0):.1f}/frame",
                f"Hien tai: {vehicle_stats.get('current', 0)}"
            ],
            y_offset + 20
        )
        
        # Traffic Count Stats
        y_offset = self._draw_section(
            frame, "DEM XE THEO HUONG",
            [
                f"Bac: {traffic_stats['current'].get('north', 0)}",
                f"Nam: {traffic_stats['current'].get('south', 0)}",
                f"Dong: {traffic_stats['current'].get('east', 0)}",
                f"Tay: {traffic_stats['current'].get('west', 0)}",
                f"---",
                f"Tong: {traffic_stats.get('total_all', 0)}"
            ],
            y_offset + 20
        )
        
        # Traffic Light Stats
        current_green = light_stats.get('current_green', 'north')
        direction_name = {
            'north': 'Bac',
            'south': 'Nam',
            'east': 'Dong',
            'west': 'Tay'
        }.get(current_green, current_green)
        
        state_text = "VANG" if light_stats.get('is_yellow', False) else "XANH"
        
        y_offset = self._draw_section(
            frame, "DEN GIAO THONG",
            [
                f"Huong: {direction_name}",
                f"Trang thai: {state_text}",
                f"Thoi gian: {light_stats.get('remaining_time', 0):.1f}s",
                f"---",
                f"So lan chuyen: {light_stats.get('switch_count', 0)}"
            ],
            y_offset + 20
        )
        
        return frame
    
    def _draw_section(self, frame, title, items, y_start):
        """
        Vẽ một section trong dashboard
        
        Args:
            frame: Frame video
            title: Tiêu đề section
            items: List các item cần hiển thị
            y_start: Vị trí Y bắt đầu
            
        Returns:
            Vị trí Y sau khi vẽ xong
        """
        # Vẽ tiêu đề
        cv2.putText(
            frame, title,
            (10, y_start),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
            COLORS['primary'], 2
        )
        
        y_offset = y_start + 25
        
        # Vẽ đường kẻ ngang
        cv2.line(
            frame,
            (10, y_offset),
            (self.dashboard_width - 10, y_offset),
            COLORS['text_secondary'],
            1
        )
        y_offset += 15
        
        # Vẽ các items
        for item in items:
            if item == "---":
                cv2.line(
                    frame,
                    (10, y_offset - 5),
                    (self.dashboard_width - 10, y_offset - 5),
                    COLORS['text_secondary'],
                    1
                )
                y_offset += 10
            else:
                cv2.putText(
                    frame, item,
                    (15, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    COLORS['text'], 1
                )
                y_offset += 22
        
        return y_offset

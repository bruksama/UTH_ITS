"""
Module tạo dashboard hiển thị thống kê và thông tin - Phiên bản cải tiến
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
        Vẽ dashboard lên frame với giao diện đẹp và dễ hiểu
        
        Args:
            frame: Frame video
            vehicle_stats: Thống kê từ VehicleDetector
            traffic_stats: Thống kê từ TrafficCounter
            light_stats: Thống kê từ TrafficLightController
            fps: FPS hiện tại
            
        Returns:
            Frame đã được vẽ dashboard
        """
        # Vẽ background panel với gradient
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (0, 0),
            (self.dashboard_width, self.height),
            (30, 30, 30),  # Màu tối hơn
            -1
        )
        cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
        
        # Vẽ border đẹp hơn
        cv2.line(frame, (self.dashboard_width, 0), (self.dashboard_width, self.height), 
                COLORS['primary'], 4)
        
        y = 25
        
        # Header với background
        header_height = 50
        cv2.rectangle(frame, (0, 0), (self.dashboard_width, header_height), 
                     COLORS['primary'], -1)
        cv2.putText(frame, "THONG KE", (15, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        
        y = header_height + 25
        
        # FPS với icon
        if UI_CONFIG['show_fps']:
            fps_color = COLORS['success'] if fps >= 15 else COLORS['warning'] if fps >= 10 else COLORS['danger']
            self._draw_info_box(frame, "FPS", f"{fps:.1f}", fps_color, y, self.dashboard_width - 20)
            y += 45
        
        # Nhận diện xe - Section lớn hơn
        y = self._draw_section_improved(
            frame, "NHAN DIEN XE", y + 10,
            [
                ("Tong so xe", f"{vehicle_stats.get('total', 0):,}", COLORS['info']),
                ("Trung binh/frame", f"{vehicle_stats.get('average_per_frame', 0):.1f}", COLORS['text']),
                ("Hien tai", f"{vehicle_stats.get('current', 0)}", COLORS['primary'])
            ]
        )
        
        # Đếm xe theo hướng - Visual hơn
        y = self._draw_traffic_section(
            frame, "DEM XE THEO HUONG", y + 15,
            traffic_stats['current']
        )
        
        # Đèn giao thông - Nổi bật hơn
        y = self._draw_light_section(
            frame, "DEN GIAO THONG", y + 15,
            light_stats
        )
        
        return frame
    
    def _draw_info_box(self, frame, label, value, color, y, width):
        """Vẽ một box thông tin"""
        box_height = 35
        cv2.rectangle(frame, (10, y - 25), (width, y + 5), (40, 40, 40), -1)
        cv2.rectangle(frame, (10, y - 25), (width, y + 5), color, 2)
        
        # Label
        cv2.putText(frame, label, (15, y - 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['text_secondary'], 1)
        # Value
        (text_w, text_h), _ = cv2.getTextSize(value, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.putText(frame, value, (width - text_w - 10, y - 8),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    def _draw_section_improved(self, frame, title, y_start, items):
        """Vẽ section với style đẹp hơn"""
        # Title với background
        title_bg_height = 30
        cv2.rectangle(frame, (5, y_start - 20), (self.dashboard_width - 5, y_start + 5),
                     (50, 50, 50), -1)
        cv2.putText(frame, title, (10, y_start - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLORS['primary'], 2)
        
        y = y_start + 15
        
        # Items
        for label, value, color in items:
            # Background cho mỗi item
            item_height = 30
            cv2.rectangle(frame, (10, y - 20), (self.dashboard_width - 10, y + 5),
                         (35, 35, 35), -1)
            
            # Label
            cv2.putText(frame, label + ":", (15, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['text_secondary'], 1)
            
            # Value
            (text_w, _), _ = cv2.getTextSize(value, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.putText(frame, value, (self.dashboard_width - text_w - 15, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            y += item_height + 5
        
        return y
    
    def _draw_traffic_section(self, frame, title, y_start, counts):
        """Vẽ section đếm xe với visual tốt hơn"""
        # Title
        title_bg_height = 30
        cv2.rectangle(frame, (5, y_start - 20), (self.dashboard_width - 5, y_start + 5),
                     (50, 50, 50), -1)
        cv2.putText(frame, title, (10, y_start - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLORS['primary'], 2)
        
        y = y_start + 15
        
        # Màu sắc cho mỗi hướng
        direction_colors = {
            'north': COLORS['primary'],
            'south': COLORS['success'],
            'east': COLORS['danger'],
            'west': COLORS['warning']
        }
        
        direction_names = {
            'north': 'BAC',
            'south': 'NAM',
            'east': 'DONG',
            'west': 'TAY'
        }
        
        # Vẽ từng hướng với bar chart
        for direction in ['north', 'south', 'east', 'west']:
            count = counts.get(direction, 0)
            color = direction_colors.get(direction, COLORS['text'])
            name = direction_names.get(direction, direction.upper())
            
            # Background
            item_height = 35
            cv2.rectangle(frame, (10, y - 22), (self.dashboard_width - 10, y + 8),
                         (35, 35, 35), -1)
            
            # Label
            cv2.putText(frame, name, (15, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLORS['text'], 1)
            
            # Số lượng
            count_text = str(count)
            (text_w, _), _ = cv2.getTextSize(count_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.putText(frame, count_text, (self.dashboard_width - text_w - 15, y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Bar indicator
            max_bar_width = self.dashboard_width - 120
            bar_width = int((count / max(1, max(counts.values()))) * max_bar_width) if max(counts.values()) > 0 else 0
            bar_width = min(bar_width, max_bar_width)
            cv2.rectangle(frame, (15, y + 2), (15 + bar_width, y + 6), color, -1)
            
            y += item_height + 5
        
        return y
    
    def _draw_light_section(self, frame, title, y_start, light_stats):
        """Vẽ section đèn giao thông với visual tốt hơn"""
        # Title
        cv2.rectangle(frame, (5, y_start - 20), (self.dashboard_width - 5, y_start + 5),
                     (50, 50, 50), -1)
        cv2.putText(frame, title, (10, y_start - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLORS['primary'], 2)
        
        y = y_start + 15
        
        # Trạng thái đèn hiện tại
        current_green = light_stats.get('current_green', 'north')
        is_yellow = light_stats.get('is_yellow', False)
        remaining = light_stats.get('remaining_time', 0)
        
        direction_names = {
            'north': 'BAC',
            'south': 'NAM',
            'east': 'DONG',
            'west': 'TAY'
        }
        
        # Hiển thị đèn hiện tại
        state_color = COLORS['warning'] if is_yellow else COLORS['success']
        state_text = "VANG" if is_yellow else "XANH"
        direction_text = direction_names.get(current_green, current_green.upper())
        
        # Box lớn cho trạng thái
        box_height = 50
        cv2.rectangle(frame, (10, y - 25), (self.dashboard_width - 10, y + 20),
                     (40, 40, 40), -1)
        cv2.rectangle(frame, (10, y - 25), (self.dashboard_width - 10, y + 20),
                     state_color, 3)
        
        # Vẽ đèn tròn
        light_x = 30
        light_y = y
        light_radius = 12
        cv2.circle(frame, (light_x, light_y), light_radius, state_color, -1)
        cv2.circle(frame, (light_x, light_y), light_radius, (255, 255, 255), 2)
        
        # Text
        status_text = f"{direction_text}: {state_text}"
        cv2.putText(frame, status_text, (light_x + 25, y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, state_color, 2)
        
        time_text = f"Con lai: {remaining:.1f}s"
        cv2.putText(frame, time_text, (light_x + 25, y + 12),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['text_secondary'], 1)
        
        y += box_height + 10
        
        # Số lần chuyển đèn
        switch_count = light_stats.get('switch_count', 0)
        self._draw_info_box(frame, "So lan chuyen den", str(switch_count), 
                           COLORS['info'], y, self.dashboard_width - 20)
        
        return y + 40

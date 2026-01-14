"""
Module đếm xe theo các hướng/làn tại ngã tư
"""
import cv2
import numpy as np
from config import COLORS, UI_CONFIG


class TrafficCounter:
    def __init__(self, frame_shape, zones_config=None):
        """
        Khởi tạo counter với các vùng đếm xe
        
        Args:
            frame_shape: Kích thước frame (height, width)
            zones_config: Dict chứa config các vùng đếm
                          Format: {'direction': {'points': [(x1,y1), ...], 'color': (B,G,R)}}
        """
        self.frame_shape = frame_shape
        self.height, self.width = frame_shape[:2]
        
        # Mặc định 4 hướng nếu không có config
        if zones_config is None:
            zones_config = self._create_default_zones()
        
        self.zones = zones_config
        self.counts = {direction: 0 for direction in zones_config.keys()}
        self.total_counted = {direction: 0 for direction in zones_config.keys()}
        self.direction_names = {
            'north': 'Bắc',
            'south': 'Nam',
            'east': 'Đông',
            'west': 'Tây'
        }
        
    def _create_default_zones(self):
        """
        Tạo các vùng đếm mặc định cho 4 hướng
        """
        h, w = self.height, self.width
        
        return {
            'north': {
                'points': [(w//4, 0), (3*w//4, 0), (3*w//4, h//4), (w//4, h//4)],
                'color': COLORS['primary']  # Blue
            },
            'south': {
                'points': [(w//4, 3*h//4), (3*w//4, 3*h//4), (3*w//4, h), (w//4, h)],
                'color': COLORS['success']  # Green
            },
            'east': {
                'points': [(3*w//4, h//4), (w, h//4), (w, 3*h//4), (3*w//4, 3*h//4)],
                'color': COLORS['danger']  # Red
            },
            'west': {
                'points': [(0, h//4), (w//4, h//4), (w//4, 3*h//4), (0, 3*h//4)],
                'color': COLORS['warning']  # Yellow
            }
        }
    
    def point_in_zone(self, point, zone_points):
        """
        Kiểm tra điểm có nằm trong zone không (sử dụng ray casting algorithm)
        
        Args:
            point: Điểm cần kiểm tra (x, y)
            zone_points: List các điểm tạo thành polygon
            
        Returns:
            True nếu điểm nằm trong zone
        """
        x, y = point
        n = len(zone_points)
        inside = False
        
        p1x, p1y = zone_points[0]
        for i in range(1, n + 1):
            p2x, p2y = zone_points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def count_vehicles(self, detections):
        """
        Đếm số xe trong mỗi zone
        
        Args:
            detections: List các detection từ VehicleDetector
            
        Returns:
            Dict với số lượng xe mỗi hướng
        """
        # Reset counts
        self.counts = {direction: 0 for direction in self.zones.keys()}
        
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = bbox
            
            # Lấy điểm trung tâm của bounding box
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            center_point = (center_x, center_y)
            
            # Kiểm tra điểm trung tâm nằm trong zone nào
            for direction, zone_info in self.zones.items():
                if self.point_in_zone(center_point, zone_info['points']):
                    self.counts[direction] += 1
                    self.total_counted[direction] += 1
                    break
        
        return self.counts.copy()
    
    def draw_zones(self, frame):
        """
        Vẽ các zone lên frame với style đẹp hơn
        
        Args:
            frame: Frame video
            
        Returns:
            Frame đã được vẽ zones
        """
        for direction, zone_info in self.zones.items():
            points = np.array(zone_info['points'], np.int32)
            color = zone_info['color']
            count = self.counts[direction]
            
            # Vẽ polygon với độ trong suốt
            overlay = frame.copy()
            cv2.fillPoly(overlay, [points], color)
            cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
            
            # Vẽ border
            cv2.polylines(frame, [points], True, color, UI_CONFIG['line_thickness'])
            
            # Vẽ label và số lượng với background
            direction_name = self.direction_names.get(direction, direction.capitalize())
            label = f"{direction_name}: {count}"
            
            # Lấy điểm trung tâm của zone để đặt label
            center_x = int(sum(p[0] for p in points) / len(points))
            center_y = int(sum(p[1] for p in points) / len(points))
            
            # Tính kích thước text
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            
            # Vẽ background cho text
            padding = 5
            cv2.rectangle(
                frame,
                (center_x - text_width//2 - padding, center_y - text_height - padding),
                (center_x + text_width//2 + padding, center_y + baseline + padding),
                color,
                -1
            )
            
            # Vẽ text
            cv2.putText(
                frame, label,
                (center_x - text_width//2, center_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                COLORS['text'], 2
            )
        
        return frame
    
    def get_statistics(self):
        """Lấy thống kê đếm xe"""
        return {
            'current': self.counts.copy(),
            'total': self.total_counted.copy(),
            'total_all': sum(self.total_counted.values())
        }
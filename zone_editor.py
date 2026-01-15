"""
Module cho phép vẽ và chỉnh sửa zones trực tiếp trên video
"""
import cv2
import numpy as np
from config import COLORS


class ZoneEditor:
    def __init__(self, zones_config, frame_shape):
        """
        Khởi tạo zone editor
        
        Args:
            zones_config: Dict chứa config các zones hiện tại
            frame_shape: Kích thước frame (height, width)
        """
        self.zones = zones_config.copy() if zones_config else {}
        self.height, self.width = frame_shape[:2]
        self.editing_zone = None
        self.dragging = False
        self.drag_point_idx = None
        self.drag_zone = None
        self.current_point = None
        
        # Màu sắc cho mỗi hướng
        self.zone_colors = {
            'north': COLORS['primary'],
            'south': COLORS['success'],
            'east': COLORS['danger'],
            'west': COLORS['warning']
        }
        
        # Tên hướng
        self.direction_names = {
            'north': 'Bắc',
            'south': 'Nam',
            'east': 'Đông',
            'west': 'Tây'
        }
    
    def draw_zones_editable(self, frame):
        """
        Vẽ zones với khả năng chỉnh sửa
        
        Args:
            frame: Frame video
            
        Returns:
            Frame đã được vẽ zones
        """
        for direction, zone_info in self.zones.items():
            points = np.array(zone_info['points'], np.int32)
            color = self.zone_colors.get(direction, COLORS['primary'])
            
            # Vẽ polygon với độ trong suốt
            overlay = frame.copy()
            cv2.fillPoly(overlay, [points], color)
            cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
            
            # Vẽ border
            cv2.polylines(frame, [points], True, color, 2)
            
            # Vẽ các điểm để có thể kéo
            for i, point in enumerate(points):
                point_x, point_y = int(point[0]), int(point[1])
                # Vẽ điểm lớn hơn để dễ click
                cv2.circle(frame, (point_x, point_y), 6, color, -1)
                cv2.circle(frame, (point_x, point_y), 6, (255, 255, 255), 2)
            
            # Vẽ label
            center_x = int(sum(p[0] for p in points) / len(points))
            center_y = int(sum(p[1] for p in points) / len(points))
            direction_name = self.direction_names.get(direction, direction.capitalize())
            
            (text_w, text_h), _ = cv2.getTextSize(
                direction_name, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            cv2.rectangle(
                frame,
                (center_x - text_w//2 - 5, center_y - text_h - 5),
                (center_x + text_w//2 + 5, center_y + 5),
                (0, 0, 0),
                -1
            )
            cv2.putText(
                frame, direction_name,
                (center_x - text_w//2, center_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                color, 2
            )
        
        return frame
    
    def handle_mouse_event(self, event, x, y, flags, param):
        """
        Xử lý sự kiện chuột
        
        Args:
            event: Loại sự kiện (cv2.EVENT_*)
            x, y: Tọa độ chuột
            flags: Flags
            param: Tham số bổ sung
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            # Kiểm tra xem có click vào điểm nào không
            clicked_zone, point_idx = self._find_point_at(x, y)
            if clicked_zone and point_idx is not None:
                self.dragging = True
                self.drag_zone = clicked_zone
                self.drag_point_idx = point_idx
                self.last_mouse_pos = (x, y)
            else:
                # Kiểm tra xem có click vào zone nào để di chuyển không
                clicked_zone = self._find_zone_at(x, y)
                if clicked_zone:
                    self.editing_zone = clicked_zone
                    # Lưu vị trí ban đầu của zone
                    self.zone_start_points = [p[:] for p in self.zones[clicked_zone]['points']]
                    self.drag_start_pos = (x, y)
                    self.dragging = True
                    self.drag_zone = clicked_zone
                    self.drag_point_idx = None  # Di chuyển toàn bộ zone
        
        elif event == cv2.EVENT_MOUSEMOVE:
            self.current_point = (x, y)
            if self.dragging and self.drag_zone:
                if self.drag_point_idx is not None:
                    # Di chuyển một điểm
                    self.zones[self.drag_zone]['points'][self.drag_point_idx] = (x, y)
                else:
                    # Di chuyển toàn bộ zone
                    if hasattr(self, 'zone_start_points') and hasattr(self, 'drag_start_pos'):
                        dx = x - self.drag_start_pos[0]
                        dy = y - self.drag_start_pos[1]
                        new_points = []
                        for px, py in self.zone_start_points:
                            new_points.append((px + dx, py + dy))
                        self.zones[self.drag_zone]['points'] = new_points
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False
            if self.drag_zone and self.drag_point_idx is None:
                # Cập nhật zone_start_points sau khi di chuyển xong
                if hasattr(self, 'zone_start_points'):
                    self.zone_start_points = [p[:] for p in self.zones[self.drag_zone]['points']]
            self.drag_zone = None
            self.drag_point_idx = None
            if hasattr(self, 'last_mouse_pos'):
                delattr(self, 'last_mouse_pos')
    
    def _find_point_at(self, x, y, threshold=10):
        """
        Tìm điểm gần vị trí click
        
        Args:
            x, y: Tọa độ click
            threshold: Khoảng cách tối đa
            
        Returns:
            (zone_name, point_index) hoặc (None, None)
        """
        for zone_name, zone_info in self.zones.items():
            points = zone_info['points']
            for i, (px, py) in enumerate(points):
                distance = ((x - px) ** 2 + (y - py) ** 2) ** 0.5
                if distance < threshold:
                    return zone_name, i
        return None, None
    
    def _find_zone_at(self, x, y):
        """
        Tìm zone chứa điểm (x, y)
        
        Args:
            x, y: Tọa độ
            
        Returns:
            Tên zone hoặc None
        """
        for zone_name, zone_info in self.zones.items():
            if self._point_in_polygon((x, y), zone_info['points']):
                return zone_name
        return None
    
    def _point_in_polygon(self, point, polygon_points):
        """Kiểm tra điểm có trong polygon không"""
        x, y = point
        n = len(polygon_points)
        inside = False
        
        p1x, p1y = polygon_points[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon_points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_zones(self):
        """Lấy zones hiện tại"""
        return self.zones.copy()
    
    def save_zones(self, filepath='zones_config.json'):
        """Lưu zones vào file"""
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.zones, f, indent=2, ensure_ascii=False)
        print(f"Đã lưu zones vào: {filepath}")
    
    def load_zones(self, filepath='zones_config.json'):
        """Tải zones từ file"""
        import json
        import os
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.zones = json.load(f)
            print(f"Đã tải zones từ: {filepath}")
            return True
        return False

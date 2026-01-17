"""
Module điều khiển đèn giao thông dựa trên số lượng xe
"""
import time
import cv2
from config import TRAFFIC_LIGHT_CONFIG, COLORS, UI_CONFIG


class TrafficLightController:
    def __init__(self, min_green_time=None, max_green_time=None, threshold=None):
        """
        Khởi tạo controller
        
        Args:
            min_green_time: Thời gian xanh tối thiểu (giây)
            max_green_time: Thời gian xanh tối đa (giây)
            threshold: Ngưỡng số xe để chuyển đèn (xe)
        """
        self.min_green_time = min_green_time or TRAFFIC_LIGHT_CONFIG['min_green_time']
        self.max_green_time = max_green_time or TRAFFIC_LIGHT_CONFIG['max_green_time']
        self.threshold = threshold or TRAFFIC_LIGHT_CONFIG['threshold']
        self.yellow_time = TRAFFIC_LIGHT_CONFIG['yellow_time']
        
        # Trạng thái đèn: 'north', 'south', 'east', 'west'
        self.current_green = 'north'
        
        # Thời gian bắt đầu đèn xanh hiện tại
        self.green_start_time = time.time()
        self.is_yellow = False
        self.yellow_start_time = None
        
        # Thống kê
        self.switch_count = 0
        self.direction_names = {
            'north': 'North',
            'south': 'South',
            'east': 'East',
            'west': 'West'
        }
        
    def get_light_state(self, vehicle_counts):
        """
        Tính toán trạng thái đèn dựa trên số lượng xe
        
        Args:
            vehicle_counts: Dict số lượng xe mỗi hướng
            
        Returns:
            Dict trạng thái đèn mỗi hướng: {'direction': 'green'|'yellow'|'red'}
        """
        current_time = time.time()
        elapsed_green_time = current_time - self.green_start_time
        
        # Kiểm tra nếu đang ở trạng thái vàng
        if self.is_yellow:
            if current_time - self.yellow_start_time >= self.yellow_time:
                # Chuyển sang đèn xanh mới
                self._switch_to_next_light(vehicle_counts)
                self.is_yellow = False
        else:
            # Kiểm tra điều kiện chuyển đèn
            current_count = vehicle_counts.get(self.current_green, 0)
            
            # Tìm hướng có nhiều xe nhất
            max_direction = max(vehicle_counts.items(), key=lambda x: x[1])
            max_count = max_direction[1]
            max_dir = max_direction[0]
            
            # Điều kiện chuyển đèn:
            # 1. Đã hết thời gian xanh tối thiểu VÀ
            # 2. (Hướng hiện tại ít xe hơn threshold HOẶC có hướng khác nhiều xe hơn đáng kể)
            should_switch = (
                elapsed_green_time >= self.min_green_time and
                (
                    current_count < self.threshold or
                    (max_dir != self.current_green and max_count > current_count + self.threshold)
                )
            )
            
            # Hoặc đã hết thời gian xanh tối đa
            if elapsed_green_time >= self.max_green_time:
                should_switch = True
            
            if should_switch:
                self.is_yellow = True
                self.yellow_start_time = current_time
        
        # Tạo dict trạng thái đèn
        light_states = {}
        for direction in vehicle_counts.keys():
            if direction == self.current_green:
                if self.is_yellow:
                    light_states[direction] = 'yellow'
                else:
                    light_states[direction] = 'green'
            else:
                light_states[direction] = 'red'
        
        return light_states
    
    def _switch_to_next_light(self, vehicle_counts):
        """
        Chuyển sang đèn xanh tiếp theo dựa trên số lượng xe
        """
        # Tìm hướng có nhiều xe nhất (ngoại trừ hướng hiện tại)
        other_directions = {k: v for k, v in vehicle_counts.items() 
                           if k != self.current_green}
        
        if other_directions:
            # Chọn hướng có nhiều xe nhất
            next_green = max(other_directions.items(), key=lambda x: x[1])[0]
        else:
            # Nếu không có xe, chuyển theo thứ tự vòng tròn
            directions = list(vehicle_counts.keys())
            current_idx = directions.index(self.current_green)
            next_green = directions[(current_idx + 1) % len(directions)]
        
        self.current_green = next_green
        self.green_start_time = time.time()
        self.switch_count += 1
    
    def draw_lights(self, frame, light_states, frame_shape):
        """
        Vẽ trạng thái đèn lên frame với style đẹp hơn
        
        Args:
            frame: Frame video
            light_states: Dict trạng thái đèn
            frame_shape: Kích thước frame (height, width)
            
        Returns:
            Frame đã được vẽ đèn
        """
        h, w = frame_shape[:2]
        
        # Vị trí hiển thị đèn cho mỗi hướng (góc trên phải)
        light_size = 28
        spacing = 38
        start_x = w - 140
        start_y = 35
        
        positions = {
            'north': (start_x, start_y),
            'south': (start_x, start_y + spacing),
            'east': (start_x, start_y + spacing * 2),
            'west': (start_x, start_y + spacing * 3)
        }
        
        # Màu sắc cho mỗi trạng thái
        colors = {
            'green': COLORS['success'],
            'yellow': COLORS['warning'],
            'red': COLORS['danger']
        }
        
        # Vẽ background panel đẹp hơn
        panel_height = spacing * 4 + 30
        panel_width = 130
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (start_x - 15, start_y - 15),
            (start_x + panel_width, start_y + panel_height),
            (30, 30, 30),
            -1
        )
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
        cv2.rectangle(
            frame,
            (start_x - 15, start_y - 15),
            (start_x + panel_width, start_y + panel_height),
            COLORS['primary'],
            3
        )
        
        # Vẽ title với background
        title_bg_height = 25
        cv2.rectangle(
            frame,
            (start_x - 15, start_y - 15),
            (start_x + panel_width, start_y - 15 + title_bg_height),
            COLORS['primary'],
            -1
        )
        cv2.putText(
            frame, "DEN GIAO THONG",
            (start_x - 10, start_y - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55,
            (255, 255, 255), 2
        )
        
        for direction, state in light_states.items():
            if direction in positions:
                x, y = positions[direction]
                color = colors[state]
                direction_name = self.direction_names.get(direction, direction[0].upper())
                
                # Vẽ vòng tròn đèn với hiệu ứng đẹp hơn
                # Shadow effect
                cv2.circle(frame, (x + 2, y + 2), light_size, (0, 0, 0), -1)
                # Main circle
                cv2.circle(frame, (x, y), light_size, color, -1)
                cv2.circle(frame, (x, y), light_size, (255, 255, 255), 2)
                
                # Vẽ viền sáng cho đèn đang bật
                if state != 'red':
                    cv2.circle(frame, (x, y), light_size + 4, color, 2)
                    # Glow effect
                    for r in range(light_size + 6, light_size + 10, 2):
                        overlay_circle = frame.copy()
                        cv2.circle(overlay_circle, (x, y), r, color, 1)
                        cv2.addWeighted(overlay_circle, 0.3, frame, 0.7, 0, frame)
                
                # Vẽ label với background
                state_symbol = "G" if state == 'green' else "Y" if state == 'yellow' else "R"
                label = f"{direction_name} [{state_symbol}]"
                
                (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
                cv2.rectangle(frame, 
                            (x + light_size + 8, y - text_h // 2 - 2),
                            (x + light_size + 8 + text_w + 4, y + text_h // 2 + 2),
                            (40, 40, 40), -1)
                cv2.putText(
                    frame, label,
                    (x + light_size + 10, y + 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    color, 2
                )
        
        # Hiển thị thời gian đèn xanh còn lại
        if not self.is_yellow:
            elapsed = time.time() - self.green_start_time
            remaining = max(0, self.max_green_time - elapsed)
            time_text = f"Time: {remaining:.1f}s"
            cv2.putText(
                frame, time_text,
                (start_x - 5, start_y + panel_height - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                COLORS['text_secondary'], 1
            )
        
        return frame
    
    def get_statistics(self, vehicle_counts=None):
        """Lấy thống kê điều khiển đèn"""
        elapsed = time.time() - self.green_start_time
        remaining = max(0, self.max_green_time - elapsed) if not self.is_yellow else 0
        
        # Tính phần trăm thời gian đã qua
        progress_percent = (elapsed / self.max_green_time) * 100 if not self.is_yellow else 100
        
        # Xác định lý do sắp chuyển đèn
        switch_reason = None
        if vehicle_counts and not self.is_yellow:
            current_count = vehicle_counts.get(self.current_green, 0)
            max_other = max([v for k, v in vehicle_counts.items() if k != self.current_green], default=0)
            
            if elapsed >= self.max_green_time * 0.9:
                switch_reason = f"Gần hết thời gian tối đa ({self.max_green_time}s)"
            elif current_count < self.threshold:
                switch_reason = f"Ít xe (<{self.threshold} xe)"
            elif max_other > current_count + self.threshold:
                switch_reason = f"Hướng khác đông hơn (+{max_other - current_count} xe)"
        
        return {
            'current_green': self.current_green,
            'is_yellow': self.is_yellow,
            'elapsed_time': elapsed,
            'remaining_time': remaining,
            'progress_percent': progress_percent,
            'switch_count': self.switch_count,
            'switch_reason': switch_reason,
            'min_time': self.min_green_time,
            'max_time': self.max_green_time
        }
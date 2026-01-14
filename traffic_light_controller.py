"""
Module điều khiển đèn giao thông dựa trên số lượng xe
"""
import time
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
            'north': 'Bắc',
            'south': 'Nam',
            'east': 'Đông',
            'west': 'Tây'
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
        light_size = 25
        spacing = 35
        start_x = w - 120
        start_y = 20
        
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
        
        # Vẽ background panel
        panel_height = spacing * 4 + 20
        panel_width = 100
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (start_x - 10, start_y - 10),
            (start_x + panel_width, start_y + panel_height),
            COLORS['background'],
            -1
        )
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        cv2.rectangle(
            frame,
            (start_x - 10, start_y - 10),
            (start_x + panel_width, start_y + panel_height),
            COLORS['text'],
            2
        )
        
        # Vẽ title
        cv2.putText(
            frame, "DEN GIAO THONG",
            (start_x - 5, start_y - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            COLORS['text'], 1
        )
        
        for direction, state in light_states.items():
            if direction in positions:
                x, y = positions[direction]
                color = colors[state]
                direction_name = self.direction_names.get(direction, direction[0].upper())
                
                # Vẽ vòng tròn đèn với hiệu ứng
                cv2.circle(frame, (x, y), light_size, color, -1)
                cv2.circle(frame, (x, y), light_size, COLORS['text'], 2)
                
                # Vẽ viền sáng cho đèn đang bật
                if state != 'red':
                    cv2.circle(frame, (x, y), light_size + 3, color, 1)
                
                # Vẽ label
                label = f"{direction_name}: {state[0].upper()}"
                cv2.putText(
                    frame, label,
                    (x + light_size + 5, y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    COLORS['text'], 1
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
    
    def get_statistics(self):
        """Lấy thống kê điều khiển đèn"""
        elapsed = time.time() - self.green_start_time
        return {
            'current_green': self.current_green,
            'is_yellow': self.is_yellow,
            'elapsed_time': elapsed,
            'remaining_time': max(0, self.max_green_time - elapsed) if not self.is_yellow else 0,
            'switch_count': self.switch_count
        }
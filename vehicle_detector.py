"""
Module nhận diện xe từ video sử dụng YOLOv8n
"""
import cv2
from ultralytics import YOLO
import numpy as np
from config import DETECTION_CONFIG, COLORS


class VehicleDetector:
    def __init__(self, model_path=None, confidence_threshold=None):
        """
        Khởi tạo detector với YOLOv8n
        
        Args:
            model_path: Đường dẫn đến model YOLOv8n
            confidence_threshold: Ngưỡng confidence tối thiểu
        """
        self.model_path = model_path or DETECTION_CONFIG['model_path']
        self.model = YOLO(self.model_path)
        self.vehicle_classes = DETECTION_CONFIG['vehicle_classes']
        self.confidence_threshold = confidence_threshold or DETECTION_CONFIG['confidence_threshold']
        
        # Class names mapping
        self.class_names = {
            2: 'Car',
            3: 'Motorcycle',
            5: 'Bus',
            7: 'Truck'
        }
        
        # Thống kê
        self.total_detections = 0
        self.detection_history = []
        
        # Traffic counter reference (sẽ được set từ main)
        self.traffic_counter = None
        
    def detect(self, frame):
        """
        Nhận diện xe trong frame
        
        Args:
            frame: Frame video (numpy array)
            
        Returns:
            List các detection với format [x1, y1, x2, y2, confidence, class]
        """
        results = self.model(frame, verbose=False, conf=self.confidence_threshold)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Chỉ lấy các class là xe
                if int(box.cls) in self.vehicle_classes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    if confidence >= self.confidence_threshold:
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': confidence,
                            'class': class_id,
                            'class_name': self.class_names.get(class_id, 'Vehicle')
                        })
        
        self.total_detections += len(detections)
        self.detection_history.append(len(detections))
        if len(self.detection_history) > 100:
            self.detection_history.pop(0)
        
        return detections
    
    def set_traffic_counter(self, traffic_counter):
        """Set reference to traffic counter to check zones"""
        self.traffic_counter = traffic_counter
    
    def is_vehicle_in_zones(self, bbox):
        """
        Kiểm tra xe có nằm trong bất kỳ zone nào không
        
        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            True nếu xe nằm trong ít nhất một zone
        """
        if not self.traffic_counter:
            return True  # Nếu không có counter, hiển thị tất cả
        
        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        center_point = (center_x, center_y)
        
        # Kiểm tra điểm trung tâm có nằm trong zone nào không
        for direction, zone_info in self.traffic_counter.zones.items():
            if self.traffic_counter.point_in_zone(center_point, zone_info['points']):
                return True
        
        return False
    
    def draw_detections(self, frame, detections):
        """
        Vẽ bounding box lên frame - chỉ cho xe trong zones
        
        Args:
            frame: Frame video
            detections: List các detection
            
        Returns:
            Frame đã được vẽ bounding box
        """
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            class_name = det.get('class_name', 'Vehicle')
            
            # Chỉ vẽ nếu xe nằm trong zones
            if not self.is_vehicle_in_zones([x1, y1, x2, y2]):
                continue
            
            # Màu sắc theo loại xe
            colors_map = {
                'Car': COLORS['primary'],
                'Motorcycle': COLORS['warning'],
                'Bus': COLORS['info'],
                'Truck': COLORS['danger']
            }
            color = colors_map.get(class_name, COLORS['success'])
            
            # Vẽ bounding box với độ dày và màu đẹp hơn
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Vẽ background cho label
            label = f"{class_name} {conf:.1%}"
            (label_width, label_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            # Vẽ background rectangle cho text
            cv2.rectangle(
                frame,
                (x1, y1 - label_height - 10),
                (x1 + label_width, y1),
                color,
                -1
            )
            
            # Vẽ text
            cv2.putText(
                frame, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                COLORS['text'], 2
            )
        
        return frame
    
    def get_statistics(self):
        """Lấy thống kê detection"""
        avg_detections = sum(self.detection_history) / len(self.detection_history) if self.detection_history else 0
        return {
            'total': self.total_detections,
            'average_per_frame': avg_detections,
            'current': self.detection_history[-1] if self.detection_history else 0
        }
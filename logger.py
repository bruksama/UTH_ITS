"""
Module logging và export statistics
"""
import csv
import os
from datetime import datetime
from config import LOGGING_CONFIG


class TrafficLogger:
    def __init__(self, log_file=None):
        """
        Khởi tạo logger
        
        Args:
            log_file: Đường dẫn file log
        """
        self.log_file = log_file or LOGGING_CONFIG['log_file']
        self.enabled = LOGGING_CONFIG['enabled']
        self.log_interval = LOGGING_CONFIG['log_interval']
        self.last_log_time = 0
        
        # Tạo file log với header nếu chưa tồn tại
        if self.enabled and not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 'North', 'South', 'East', 'West',
                    'Total_Vehicles', 'Current_Green', 'Light_State',
                    'Elapsed_Time', 'FPS'
                ])
    
    def log(self, vehicle_counts, light_stats, fps=0):
        """
        Ghi log
        
        Args:
            vehicle_counts: Dict số lượng xe mỗi hướng
            light_stats: Dict thống kê đèn
            fps: FPS hiện tại
        """
        if not self.enabled:
            return
        
        current_time = datetime.now().timestamp()
        
        # Chỉ log theo interval
        if current_time - self.last_log_time < self.log_interval:
            return
        
        self.last_log_time = current_time
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                vehicle_counts.get('north', 0),
                vehicle_counts.get('south', 0),
                vehicle_counts.get('east', 0),
                vehicle_counts.get('west', 0),
                sum(vehicle_counts.values()),
                light_stats.get('current_green', 'unknown'),
                'yellow' if light_stats.get('is_yellow', False) else 'green',
                light_stats.get('elapsed_time', 0),
                fps
            ])
    
    def export_summary(self, output_file='traffic_summary.txt'):
        """
        Export summary statistics
        
        Args:
            output_file: Đường dẫn file output
        """
        if not os.path.exists(self.log_file):
            return
        
        # Đọc và tính toán thống kê
        with open(self.log_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if not rows:
            return
        
        # Tính toán thống kê
        total_north = sum(int(row['North']) for row in rows)
        total_south = sum(int(row['South']) for row in rows)
        total_east = sum(int(row['East']) for row in rows)
        total_west = sum(int(row['West']) for row in rows)
        
        total_vehicles = sum(int(row['Total_Vehicles']) for row in rows)
        avg_vehicles = total_vehicles / len(rows) if rows else 0
        
        # Ghi summary
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== TRAFFIC STATISTICS SUMMARY ===\n\n")
            f.write(f"Total Records: {len(rows)}\n")
            f.write(f"Time Range: {rows[0]['Timestamp']} - {rows[-1]['Timestamp']}\n\n")
            f.write("Vehicle Count by Direction:\n")
            f.write(f"  North: {total_north}\n")
            f.write(f"  South: {total_south}\n")
            f.write(f"  East: {total_east}\n")
            f.write(f"  West: {total_west}\n")
            f.write(f"\nTotal Vehicles: {total_vehicles}\n")
            f.write(f"Average per Record: {avg_vehicles:.2f}\n")

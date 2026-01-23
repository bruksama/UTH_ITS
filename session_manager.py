"""
Script helper để quản lý sessions
Cung cấp các chức năng: list, view, compare, clean sessions
"""
import os
import json
import argparse
from datetime import datetime
from pathlib import Path


class SessionManager:
    def __init__(self, base_folder='output', sessions_folder='sessions'):
        self.base_folder = base_folder
        self.sessions_folder = os.path.join(base_folder, sessions_folder)
    
    def list_sessions(self, limit=None, sort_by='date'):
        """
        Liệt kê tất cả sessions
        
        Args:
            limit: Giới hạn số lượng sessions hiển thị
            sort_by: Sắp xếp theo 'date' hoặc 'frames'
        """
        if not os.path.exists(self.sessions_folder):
            print(f"Không tìm thấy folder sessions: {self.sessions_folder}")
            return []
        
        sessions = []
        for session_name in os.listdir(self.sessions_folder):
            session_path = os.path.join(self.sessions_folder, session_name)
            if not os.path.isdir(session_path):
                continue
            
            metadata_file = os.path.join(session_path, 'metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                sessions.append({
                    'name': session_name,
                    'path': session_path,
                    'metadata': metadata
                })
            else:
                # Session không có metadata (có thể là session cũ)
                sessions.append({
                    'name': session_name,
                    'path': session_path,
                    'metadata': None
                })
        
        # Sắp xếp
        if sort_by == 'date':
            sessions.sort(key=lambda x: x['name'], reverse=True)
        elif sort_by == 'frames':
            sessions.sort(
                key=lambda x: x['metadata']['video_info']['processed_frames'] 
                if x['metadata'] else 0, 
                reverse=True
            )
        
        # Giới hạn
        if limit:
            sessions = sessions[:limit]
        
        return sessions
    
    def print_sessions_table(self, sessions):
        """In bảng sessions"""
        if not sessions:
            print("Không có session nào!")
            return
        
        print("\n" + "=" * 120)
        print(f"{'Session ID':<20} {'Timestamp':<20} {'Video':<30} {'Frames':<10} {'Vehicles':<10}")
        print("=" * 120)
        
        for session in sessions:
            name = session['name']
            metadata = session['metadata']
            
            if metadata:
                timestamp = metadata['session_info']['timestamp']
                video = metadata['video_info']['source'][:28]
                frames = metadata['video_info']['processed_frames']
                vehicles = metadata['statistics']['total_vehicles_detected']
                print(f"{name:<20} {timestamp:<20} {video:<30} {frames:<10} {vehicles:<10}")
            else:
                print(f"{name:<20} {'N/A':<20} {'N/A':<30} {'N/A':<10} {'N/A':<10}")
        
        print("=" * 120)
        print(f"Tổng số sessions: {len(sessions)}\n")
    
    def view_session(self, session_name):
        """Xem chi tiết một session"""
        session_path = os.path.join(self.sessions_folder, session_name)
        
        if not os.path.exists(session_path):
            print(f"Không tìm thấy session: {session_name}")
            return
        
        metadata_file = os.path.join(session_path, 'metadata.json')
        
        if not os.path.exists(metadata_file):
            print(f"Session {session_name} không có metadata")
            return
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # In thông tin chi tiết
        print("\n" + "=" * 60)
        print(f"SESSION: {session_name}")
        print("=" * 60)
        
        print("\n[SESSION INFO]")
        print(f"  Timestamp: {metadata['session_info']['timestamp']}")
        print(f"  Session ID: {metadata['session_info']['session_id']}")
        
        print("\n[VIDEO INFO]")
        print(f"  Source: {metadata['video_info']['source']}")
        print(f"  Resolution: {metadata['video_info']['width']}x{metadata['video_info']['height']}")
        print(f"  FPS: {metadata['video_info']['fps']}")
        print(f"  Total frames: {metadata['video_info']['total_frames']}")
        print(f"  Processed frames: {metadata['video_info']['processed_frames']}")
        
        print("\n[DETECTION CONFIG]")
        print(f"  Model: {metadata['detection_config']['model']}")
        print(f"  Confidence threshold: {metadata['detection_config']['confidence_threshold']}")
        
        print("\n[STATISTICS]")
        print(f"  Total vehicles detected: {metadata['statistics']['total_vehicles_detected']}")
        print(f"  Average vehicles/frame: {metadata['statistics']['average_vehicles_per_frame']:.2f}")
        print(f"  Vehicles by direction:")
        for direction, count in metadata['statistics']['vehicles_by_direction'].items():
            print(f"    {direction.capitalize()}: {count}")
        print(f"  Traffic light switches: {metadata['statistics']['traffic_light_switches']}")
        
        print("\n[OUTPUT FILES]")
        for file_type, filename in metadata['output_files'].items():
            if filename:
                file_path = os.path.join(session_path, filename)
                exists = "✓" if os.path.exists(file_path) else "✗"
                print(f"  {file_type.capitalize()}: {filename} {exists}")
        
        # Kiểm tra screenshots
        screenshots_folder = os.path.join(session_path, 'screenshots')
        if os.path.exists(screenshots_folder):
            screenshot_count = len([f for f in os.listdir(screenshots_folder) if f.endswith('.jpg')])
            print(f"  Screenshots: {screenshot_count} files")
        
        print("\n[SESSION PATH]")
        print(f"  {session_path}")
        print("=" * 60 + "\n")
    
    def compare_sessions(self, session_names):
        """So sánh nhiều sessions"""
        print("\n" + "=" * 120)
        print(f"SO SÁNH {len(session_names)} SESSIONS")
        print("=" * 120)
        
        sessions_data = []
        for name in session_names:
            metadata_file = os.path.join(self.sessions_folder, name, 'metadata.json')
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                sessions_data.append({'name': name, 'metadata': metadata})
        
        if not sessions_data:
            print("Không tìm thấy session nào có metadata!")
            return
        
        # In bảng so sánh
        print(f"\n{'Metric':<30}", end='')
        for s in sessions_data:
            print(f"{s['name']:<25}", end='')
        print()
        print("-" * 120)
        
        # Timestamp
        print(f"{'Timestamp':<30}", end='')
        for s in sessions_data:
            print(f"{s['metadata']['session_info']['timestamp']:<25}", end='')
        print()
        
        # Video source
        print(f"{'Video source':<30}", end='')
        for s in sessions_data:
            video = s['metadata']['video_info']['source'][:23]
            print(f"{video:<25}", end='')
        print()
        
        # Frames
        print(f"{'Processed frames':<30}", end='')
        for s in sessions_data:
            frames = s['metadata']['video_info']['processed_frames']
            print(f"{frames:<25}", end='')
        print()
        
        # Total vehicles
        print(f"{'Total vehicles':<30}", end='')
        for s in sessions_data:
            vehicles = s['metadata']['statistics']['total_vehicles_detected']
            print(f"{vehicles:<25}", end='')
        print()
        
        # Average vehicles/frame
        print(f"{'Avg vehicles/frame':<30}", end='')
        for s in sessions_data:
            avg = s['metadata']['statistics']['average_vehicles_per_frame']
            print(f"{avg:<25.2f}", end='')
        print()
        
        # Traffic light switches
        print(f"{'Light switches':<30}", end='')
        for s in sessions_data:
            switches = s['metadata']['statistics']['traffic_light_switches']
            print(f"{switches:<25}", end='')
        print()
        
        print("=" * 120 + "\n")
    
    def clean_old_sessions(self, keep_latest=5, dry_run=True):
        """
        Xóa các sessions cũ, chỉ giữ lại N sessions mới nhất
        
        Args:
            keep_latest: Số lượng sessions mới nhất cần giữ
            dry_run: True = chỉ hiển thị, không xóa thật
        """
        sessions = self.list_sessions(sort_by='date')
        
        if len(sessions) <= keep_latest:
            print(f"Chỉ có {len(sessions)} sessions, không cần xóa!")
            return
        
        sessions_to_delete = sessions[keep_latest:]
        
        print(f"\n{'DRY RUN - ' if dry_run else ''}Sẽ xóa {len(sessions_to_delete)} sessions:")
        for session in sessions_to_delete:
            print(f"  - {session['name']}")
        
        if not dry_run:
            import shutil
            for session in sessions_to_delete:
                shutil.rmtree(session['path'])
                print(f"  ✓ Đã xóa: {session['name']}")
            print(f"\nĐã xóa {len(sessions_to_delete)} sessions!")
        else:
            print("\nChạy với --execute để xóa thật")
    
    def get_latest_session(self):
        """Lấy session mới nhất"""
        sessions = self.list_sessions(limit=1, sort_by='date')
        return sessions[0] if sessions else None


def main():
    parser = argparse.ArgumentParser(
        description='Session Manager - Quản lý các sessions của Traffic Control System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:
  # Liệt kê tất cả sessions
  python session_manager.py list
  
  # Liệt kê 10 sessions mới nhất
  python session_manager.py list --limit 10
  
  # Xem chi tiết một session
  python session_manager.py view 20260123_143052
  
  # So sánh 2 sessions
  python session_manager.py compare 20260123_143052 20260123_150234
  
  # Xóa sessions cũ (dry run)
  python session_manager.py clean --keep 5
  
  # Xóa sessions cũ (thực thi)
  python session_manager.py clean --keep 5 --execute
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='Liệt kê sessions')
    list_parser.add_argument('--limit', type=int, help='Giới hạn số lượng sessions')
    list_parser.add_argument('--sort', choices=['date', 'frames'], default='date',
                            help='Sắp xếp theo date hoặc frames')
    
    # View command
    view_parser = subparsers.add_parser('view', help='Xem chi tiết session')
    view_parser.add_argument('session_name', help='Tên session (ví dụ: 20260123_143052)')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='So sánh sessions')
    compare_parser.add_argument('session_names', nargs='+', help='Danh sách tên sessions')
    
    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Xóa sessions cũ')
    clean_parser.add_argument('--keep', type=int, default=5,
                             help='Số lượng sessions mới nhất cần giữ (mặc định: 5)')
    clean_parser.add_argument('--execute', action='store_true',
                             help='Thực thi xóa (mặc định là dry run)')
    
    # Latest command
    latest_parser = subparsers.add_parser('latest', help='Xem session mới nhất')
    
    args = parser.parse_args()
    
    manager = SessionManager()
    
    if args.command == 'list':
        sessions = manager.list_sessions(limit=args.limit, sort_by=args.sort)
        manager.print_sessions_table(sessions)
    
    elif args.command == 'view':
        manager.view_session(args.session_name)
    
    elif args.command == 'compare':
        manager.compare_sessions(args.session_names)
    
    elif args.command == 'clean':
        manager.clean_old_sessions(keep_latest=args.keep, dry_run=not args.execute)
    
    elif args.command == 'latest':
        latest = manager.get_latest_session()
        if latest:
            manager.view_session(latest['name'])
        else:
            print("Không có session nào!")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

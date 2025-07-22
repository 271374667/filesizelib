# Real-World Use Cases

Production-ready examples demonstrating Bytesize in real applications and scenarios.

## 🌐 Web Development

### File Upload Handler

A robust file upload system with size validation and progress tracking:

```python
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from bytesize import Storage, StorageUnit

class FileUploadHandler:
    """Production-ready file upload handler with size management."""
    
    def __init__(self, upload_dir: str, max_file_size: str = "100 MB", 
                 max_total_size: str = "1 GB"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.max_file_size = Storage.parse(max_file_size)
        self.max_total_size = Storage.parse(max_total_size)
    
    def validate_upload(self, file_path: str, filename: str) -> Dict[str, any]:
        """Validate file upload against size constraints."""
        try:
            file_size = Storage.get_size_from_path(file_path)
            current_total = self._calculate_current_usage()
            
            # Check individual file size
            if file_size > self.max_file_size:
                return {
                    'valid': False,
                    'error': 'FILE_TOO_LARGE',
                    'message': f'File size {file_size.auto_scale()} exceeds limit of {self.max_file_size.auto_scale()}',
                    'file_size': file_size,
                    'limit': self.max_file_size
                }
            
            # Check total storage limit
            projected_total = current_total + file_size
            if projected_total > self.max_total_size:
                remaining = self.max_total_size - current_total
                return {
                    'valid': False,
                    'error': 'STORAGE_LIMIT_EXCEEDED',
                    'message': f'Upload would exceed storage limit. Available: {remaining.auto_scale()}',
                    'file_size': file_size,
                    'available': remaining,
                    'current_usage': current_total
                }
            
            return {
                'valid': True,
                'file_size': file_size,
                'current_usage': current_total,
                'projected_usage': projected_total,
                'remaining_space': self.max_total_size - projected_total
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': 'VALIDATION_ERROR',
                'message': f'Could not validate file: {str(e)}'
            }
    
    def process_upload(self, source_path: str, filename: str) -> Dict[str, any]:
        """Process file upload with validation and metadata."""
        validation = self.validate_upload(source_path, filename)
        
        if not validation['valid']:
            return validation
        
        try:
            destination = self.upload_dir / filename
            
            # Handle filename conflicts
            counter = 1
            original_name = destination.stem
            extension = destination.suffix
            
            while destination.exists():
                new_name = f"{original_name}_{counter}{extension}"
                destination = self.upload_dir / new_name
                counter += 1
            
            # Copy file
            shutil.copy2(source_path, destination)
            
            # Verify successful upload
            uploaded_size = Storage.get_size_from_path(destination)
            
            return {
                'success': True,
                'filename': destination.name,
                'file_size': uploaded_size,
                'file_path': str(destination),
                'current_usage': validation['projected_usage'],
                'remaining_space': validation['remaining_space']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': 'UPLOAD_FAILED',
                'message': f'Upload failed: {str(e)}'
            }
    
    def _calculate_current_usage(self) -> Storage:
        """Calculate current storage usage."""
        return Storage.get_size_from_path(self.upload_dir)
    
    def get_storage_stats(self) -> Dict[str, any]:
        """Get comprehensive storage statistics."""
        current_usage = self._calculate_current_usage()
        remaining = self.max_total_size - current_usage
        usage_percent = (current_usage / self.max_total_size) * 100
        
        files = list(self.upload_dir.glob('*'))
        file_count = len([f for f in files if f.is_file()])
        
        return {
            'total_capacity': self.max_total_size,
            'current_usage': current_usage,
            'remaining_space': remaining,
            'usage_percentage': usage_percent,
            'file_count': file_count,
            'max_file_size': self.max_file_size,
            'status': 'warning' if usage_percent > 80 else 'normal'
        }

# Usage in a web framework (Flask example)
from flask import Flask, request, jsonify

app = Flask(__name__)
upload_handler = FileUploadHandler('/uploads', '50 MB', '10 GB')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save temporary file
    temp_path = f'/tmp/{file.filename}'
    file.save(temp_path)
    
    try:
        result = upload_handler.process_upload(temp_path, file.filename)
        
        if result.get('success'):
            return jsonify({
                'message': 'Upload successful',
                'filename': result['filename'],
                'size': str(result['file_size'].auto_scale()),
                'storage_usage': str(result['current_usage'].auto_scale())
            })
        else:
            return jsonify({
                'error': result.get('error', 'Unknown error'),
                'message': result.get('message', 'Upload failed')
            }), 400
            
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@app.route('/storage/stats')
def storage_stats():
    stats = upload_handler.get_storage_stats()
    return jsonify({
        'capacity': str(stats['total_capacity'].auto_scale()),
        'used': str(stats['current_usage'].auto_scale()),
        'remaining': str(stats['remaining_space'].auto_scale()),
        'usage_percentage': f"{stats['usage_percentage']:.1f}%",
        'file_count': stats['file_count'],
        'status': stats['status']
    })
```

### Content Delivery Network (CDN) Analytics

Track and analyze content delivery performance:

```python
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class CDNAnalyzer:
    """Analyze CDN usage and performance metrics."""
    
    def __init__(self, db_path: str = 'cdn_analytics.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for analytics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                file_path TEXT,
                file_size_bytes INTEGER,
                transfer_time_seconds REAL,
                client_ip TEXT,
                user_agent TEXT,
                success BOOLEAN
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_transfer(self, file_path: str, transfer_time: float, 
                    client_ip: str, user_agent: str, success: bool = True):
        """Log a file transfer event."""
        try:
            file_size = Storage.get_size_from_path(file_path)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transfers 
                (timestamp, file_path, file_size_bytes, transfer_time_seconds, 
                 client_ip, user_agent, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow().isoformat(),
                file_path,
                file_size.convert_to_bytes(),
                transfer_time,
                client_ip,
                user_agent,
                success
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Failed to log transfer: {e}")
    
    def analyze_bandwidth_usage(self, days: int = 7) -> Dict[str, any]:
        """Analyze bandwidth usage over specified period."""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total bandwidth
        cursor.execute('''
            SELECT SUM(file_size_bytes), COUNT(*), AVG(transfer_time_seconds)
            FROM transfers 
            WHERE timestamp > ? AND success = 1
        ''', (start_date.isoformat(),))
        
        total_bytes, transfer_count, avg_time = cursor.fetchone()
        
        if total_bytes is None:
            total_bytes = 0
            transfer_count = 0
            avg_time = 0
        
        total_bandwidth = Storage.parse_from_bytes(total_bytes)
        
        # Daily breakdown
        cursor.execute('''
            SELECT DATE(timestamp) as date, 
                   SUM(file_size_bytes) as daily_bytes,
                   COUNT(*) as daily_transfers
            FROM transfers 
            WHERE timestamp > ? AND success = 1
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (start_date.isoformat(),))
        
        daily_stats = []
        for date, bytes_transferred, transfers in cursor.fetchall():
            daily_stats.append({
                'date': date,
                'bandwidth': Storage.parse_from_bytes(bytes_transferred),
                'transfers': transfers,
                'avg_file_size': Storage.parse_from_bytes(bytes_transferred / transfers) if transfers > 0 else Storage(0, StorageUnit.BYTES)
            })
        
        # Top files by bandwidth
        cursor.execute('''
            SELECT file_path, 
                   SUM(file_size_bytes) as total_bytes,
                   COUNT(*) as request_count,
                   file_size_bytes as file_size
            FROM transfers 
            WHERE timestamp > ? AND success = 1
            GROUP BY file_path, file_size_bytes
            ORDER BY total_bytes DESC
            LIMIT 10
        ''', (start_date.isoformat(),))
        
        top_files = []
        for file_path, total_bytes, requests, file_size in cursor.fetchall():
            top_files.append({
                'file_path': file_path,
                'total_bandwidth': Storage.parse_from_bytes(total_bytes),
                'requests': requests,
                'file_size': Storage.parse_from_bytes(file_size)
            })
        
        conn.close()
        
        # Calculate average throughput
        avg_throughput = Storage(0, StorageUnit.BYTES)
        if avg_time > 0:
            avg_file_size = total_bandwidth / transfer_count if transfer_count > 0 else Storage(0, StorageUnit.BYTES)
            throughput_bytes_per_second = avg_file_size.convert_to_bytes() / avg_time
            avg_throughput = Storage.parse_from_bytes(throughput_bytes_per_second)
        
        return {
            'period_days': days,
            'total_bandwidth': total_bandwidth,
            'total_transfers': transfer_count,
            'average_throughput': avg_throughput,
            'daily_stats': daily_stats,
            'top_files': top_files,
            'avg_transfer_time': avg_time
        }
    
    def generate_report(self, days: int = 7) -> str:
        """Generate human-readable bandwidth report."""
        analysis = self.analyze_bandwidth_usage(days)
        
        report = f"CDN Bandwidth Report ({days} days)\n"
        report += "=" * 50 + "\n\n"
        
        report += f"📊 Summary:\n"
        report += f"  Total Bandwidth: {analysis['total_bandwidth'].auto_scale()}\n"
        report += f"  Total Transfers: {analysis['total_transfers']:,}\n"
        report += f"  Average Throughput: {analysis['average_throughput'].auto_scale()}/s\n"
        report += f"  Average Transfer Time: {analysis['avg_transfer_time']:.2f}s\n\n"
        
        # Daily breakdown
        if analysis['daily_stats']:
            report += f"📅 Daily Breakdown:\n"
            for day in analysis['daily_stats']:
                report += f"  {day['date']}: {day['bandwidth'].auto_scale()} ({day['transfers']} transfers)\n"
            report += "\n"
        
        # Top files
        if analysis['top_files']:
            report += f"🔥 Top Files by Bandwidth:\n"
            for i, file_info in enumerate(analysis['top_files'][:5], 1):
                report += f"  {i}. {file_info['file_path']}\n"
                report += f"     Total: {file_info['total_bandwidth'].auto_scale()} ({file_info['requests']} requests)\n"
                report += f"     Size: {file_info['file_size'].auto_scale()}\n"
        
        return report

# Usage example
analyzer = CDNAnalyzer()

# Log some transfers (this would typically be called from your CDN/web server)
analyzer.log_transfer('/static/video.mp4', 2.5, '192.168.1.100', 'Mozilla/5.0...')
analyzer.log_transfer('/static/image.jpg', 0.1, '192.168.1.101', 'Chrome/100.0...')

# Generate weekly report
print(analyzer.generate_report(7))
```

## 🖥️ System Administration

### Disk Space Monitor

Comprehensive disk space monitoring and alerting:

```python
import psutil
import smtplib
from email.mime.text import MimeText
from datetime import datetime
from typing import List, Dict, Tuple

class DiskSpaceMonitor:
    """Production disk space monitoring system."""
    
    def __init__(self, alert_threshold: str = "90%", 
                 warning_threshold: str = "80%",
                 email_config: Optional[Dict] = None):
        self.alert_threshold = float(alert_threshold.rstrip('%'))
        self.warning_threshold = float(warning_threshold.rstrip('%'))
        self.email_config = email_config
        self.last_alerts = {}
    
    def scan_disk_usage(self) -> List[Dict[str, any]]:
        """Scan all mounted disks and return usage information."""
        disk_info = []
        
        # Get all disk partitions
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                # Get disk usage statistics
                usage = psutil.disk_usage(partition.mountpoint)
                
                total = Storage.parse_from_bytes(usage.total)
                used = Storage.parse_from_bytes(usage.used)
                free = Storage.parse_from_bytes(usage.free)
                
                usage_percent = (used.convert_to_bytes() / total.convert_to_bytes()) * 100
                
                # Determine status
                if usage_percent >= self.alert_threshold:
                    status = 'CRITICAL'
                elif usage_percent >= self.warning_threshold:
                    status = 'WARNING'
                else:
                    status = 'OK'
                
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'filesystem': partition.fstype,
                    'total': total,
                    'used': used,
                    'free': free,
                    'usage_percent': usage_percent,
                    'status': status
                })
                
            except PermissionError:
                # Skip inaccessible partitions
                continue
            except Exception as e:
                print(f"Error scanning {partition.mountpoint}: {e}")
                continue
        
        return disk_info
    
    def check_large_directories(self, paths: List[str], 
                               threshold: str = "1 GB") -> List[Dict[str, any]]:
        """Check specified directories for large size."""
        threshold_size = Storage.parse(threshold)
        large_dirs = []
        
        for path in paths:
            try:
                dir_size = Storage.get_size_from_path(path)
                
                if dir_size > threshold_size:
                    large_dirs.append({
                        'path': path,
                        'size': dir_size,
                        'threshold': threshold_size,
                        'over_threshold': dir_size - threshold_size
                    })
                    
            except (FileNotFoundError, PermissionError) as e:
                large_dirs.append({
                    'path': path,
                    'error': str(e),
                    'size': None
                })
        
        return large_dirs
    
    def find_largest_files(self, directory: str, 
                          count: int = 10) -> List[Tuple[str, Storage]]:
        """Find the largest files in a directory."""
        file_sizes = []
        
        try:
            for file_path in Path(directory).rglob('*'):
                if file_path.is_file():
                    try:
                        size = Storage.get_size_from_path(file_path)
                        file_sizes.append((str(file_path), size))
                    except (PermissionError, FileNotFoundError):
                        continue
            
            # Sort by size and return top N
            file_sizes.sort(key=lambda x: x[1].convert_to_bytes(), reverse=True)
            return file_sizes[:count]
            
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
            return []
    
    def generate_alert_report(self, disk_info: List[Dict], 
                            large_dirs: List[Dict] = None,
                            largest_files: List[Tuple] = None) -> str:
        """Generate comprehensive alert report."""
        report = f"🚨 Disk Space Alert Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 70 + "\n\n"
        
        # Critical and warning disks
        critical_disks = [disk for disk in disk_info if disk['status'] == 'CRITICAL']
        warning_disks = [disk for disk in disk_info if disk['status'] == 'WARNING']
        
        if critical_disks:
            report += "🔴 CRITICAL DISK USAGE:\n"
            for disk in critical_disks:
                report += f"  {disk['device']} ({disk['mountpoint']})\n"
                report += f"    Usage: {disk['usage_percent']:.1f}% ({disk['used'].auto_scale()} / {disk['total'].auto_scale()})\n"
                report += f"    Free: {disk['free'].auto_scale()}\n"
                report += f"    Filesystem: {disk['filesystem']}\n\n"
        
        if warning_disks:
            report += "🟡 WARNING DISK USAGE:\n"
            for disk in warning_disks:
                report += f"  {disk['device']} ({disk['mountpoint']})\n"
                report += f"    Usage: {disk['usage_percent']:.1f}% ({disk['used'].auto_scale()} / {disk['total'].auto_scale()})\n"
                report += f"    Free: {disk['free'].auto_scale()}\n\n"
        
        # Large directories
        if large_dirs:
            report += "📁 LARGE DIRECTORIES:\n"
            for dir_info in large_dirs:
                if 'error' not in dir_info:
                    report += f"  {dir_info['path']}: {dir_info['size'].auto_scale()}\n"
                    report += f"    Over threshold by: {dir_info['over_threshold'].auto_scale()}\n"
                else:
                    report += f"  {dir_info['path']}: Error - {dir_info['error']}\n"
            report += "\n"
        
        # Largest files
        if largest_files:
            report += "📄 LARGEST FILES:\n"
            for i, (file_path, size) in enumerate(largest_files[:10], 1):
                report += f"  {i:2d}. {size.auto_scale():>8} - {file_path}\n"
            report += "\n"
        
        # Summary
        total_disks = len(disk_info)
        ok_disks = len([d for d in disk_info if d['status'] == 'OK'])
        
        report += f"📊 SUMMARY:\n"
        report += f"  Total Partitions: {total_disks}\n"
        report += f"  OK: {ok_disks}, Warning: {len(warning_disks)}, Critical: {len(critical_disks)}\n"
        
        return report
    
    def send_email_alert(self, subject: str, body: str):
        """Send email alert if configured."""
        if not self.email_config:
            return False
        
        try:
            msg = MimeText(body)
            msg['Subject'] = subject
            msg['From'] = self.email_config['from']
            msg['To'] = ', '.join(self.email_config['to'])
            
            with smtplib.SMTP(self.email_config['smtp_host'], 
                            self.email_config['smtp_port']) as server:
                if self.email_config.get('use_tls'):
                    server.starttls()
                if self.email_config.get('username'):
                    server.login(self.email_config['username'], 
                               self.email_config['password'])
                
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False
    
    def run_monitoring_cycle(self, check_dirs: List[str] = None):
        """Run complete monitoring cycle."""
        print(f"🔍 Starting disk monitoring cycle at {datetime.now()}")
        
        # Scan disk usage
        disk_info = self.scan_disk_usage()
        
        # Check for alerts
        alerts_needed = any(disk['status'] in ['CRITICAL', 'WARNING'] 
                          for disk in disk_info)
        
        # Check large directories if specified
        large_dirs = None
        if check_dirs:
            large_dirs = self.check_large_directories(check_dirs)
        
        # Find largest files in problematic partitions
        largest_files = []
        for disk in disk_info:
            if disk['status'] == 'CRITICAL':
                files = self.find_largest_files(disk['mountpoint'], 5)
                largest_files.extend(files)
        
        # Generate report
        report = self.generate_alert_report(disk_info, large_dirs, largest_files)
        
        # Print report
        print(report)
        
        # Send email alerts if needed
        if alerts_needed and self.email_config:
            critical_count = len([d for d in disk_info if d['status'] == 'CRITICAL'])
            warning_count = len([d for d in disk_info if d['status'] == 'WARNING'])
            
            subject = f"🚨 Disk Space Alert: {critical_count} Critical, {warning_count} Warning"
            self.send_email_alert(subject, report)
        
        return {
            'disk_info': disk_info,
            'large_dirs': large_dirs,
            'largest_files': largest_files,
            'alerts_sent': alerts_needed
        }

# Usage example
email_config = {
    'smtp_host': 'smtp.gmail.com',
    'smtp_port': 587,
    'use_tls': True,
    'username': 'alerts@company.com',
    'password': 'app_password',
    'from': 'alerts@company.com',
    'to': ['admin@company.com', 'ops@company.com']
}

monitor = DiskSpaceMonitor(
    alert_threshold="90%",
    warning_threshold="80%",
    email_config=email_config
)

# Run monitoring
result = monitor.run_monitoring_cycle([
    '/var/log',
    '/tmp',
    '/home/users',
    '/opt/applications'
])
```

## 📊 Data Analysis and ETL

### Log File Analyzer

Analyze log files and track storage patterns:

```python
import re
import gzip
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Iterator, Dict, List, Tuple

class LogFileAnalyzer:
    """Analyze log files for storage and performance patterns."""
    
    def __init__(self, log_pattern: str = None):
        # Default Apache/Nginx log pattern
        self.log_pattern = log_pattern or (
            r'(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
            r'"(?P<method>\S+) (?P<url>\S+) \S+" (?P<status>\d+) '
            r'(?P<size>\d+|-) "(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
        )
        self.log_regex = re.compile(self.log_pattern)
    
    def parse_log_file(self, file_path: str) -> Iterator[Dict[str, any]]:
        """Parse log file and yield structured records."""
        open_func = gzip.open if file_path.endswith('.gz') else open
        
        with open_func(file_path, 'rt', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    match = self.log_regex.match(line.strip())
                    if match:
                        data = match.groupdict()
                        
                        # Parse size
                        size_str = data.get('size', '0')
                        if size_str == '-' or size_str == '':
                            size = Storage(0, StorageUnit.BYTES)
                        else:
                            size = Storage(int(size_str), StorageUnit.BYTES)
                        
                        # Parse timestamp
                        timestamp_str = data.get('timestamp', '')
                        try:
                            # Common log format: 10/Oct/2000:13:55:36 -0700
                            timestamp = datetime.strptime(
                                timestamp_str.split()[0], 
                                '%d/%b/%Y:%H:%M:%S'
                            )
                        except ValueError:
                            timestamp = datetime.now()
                        
                        yield {
                            'line_number': line_num,
                            'ip': data.get('ip', ''),
                            'timestamp': timestamp,
                            'method': data.get('method', ''),
                            'url': data.get('url', ''),
                            'status': int(data.get('status', 0)),
                            'size': size,
                            'referer': data.get('referer', ''),
                            'user_agent': data.get('user_agent', ''),
                            'raw_line': line.strip()
                        }
                        
                except Exception as e:
                    # Skip malformed lines but track them
                    yield {
                        'line_number': line_num,
                        'error': str(e),
                        'raw_line': line.strip()
                    }
    
    def analyze_bandwidth_usage(self, file_paths: List[str], 
                               time_window: int = 24) -> Dict[str, any]:
        """Analyze bandwidth usage patterns."""
        hourly_bandwidth = defaultdict(lambda: Storage(0, StorageUnit.BYTES))
        status_bandwidth = defaultdict(lambda: Storage(0, StorageUnit.BYTES))
        url_bandwidth = defaultdict(lambda: Storage(0, StorageUnit.BYTES))
        ip_bandwidth = defaultdict(lambda: Storage(0, StorageUnit.BYTES))
        
        total_bandwidth = Storage(0, StorageUnit.BYTES)
        total_requests = 0
        error_count = 0
        
        # Cutoff time for analysis window
        cutoff_time = datetime.now() - timedelta(hours=time_window)
        
        for file_path in file_paths:
            print(f"Analyzing {file_path}...")
            
            for record in self.parse_log_file(file_path):
                if 'error' in record:
                    error_count += 1
                    continue
                
                # Skip records outside time window
                if record['timestamp'] < cutoff_time:
                    continue
                
                size = record['size']
                total_bandwidth += size
                total_requests += 1
                
                # Hourly breakdown
                hour_key = record['timestamp'].strftime('%Y-%m-%d %H:00')
                hourly_bandwidth[hour_key] += size
                
                # Status code breakdown
                status_code = record['status']
                status_bandwidth[f"{status_code}"] += size
                
                # Top URLs by bandwidth
                url_bandwidth[record['url']] += size
                
                # Top IPs by bandwidth
                ip_bandwidth[record['ip']] += size
        
        # Calculate averages and top items
        avg_request_size = (total_bandwidth / total_requests 
                           if total_requests > 0 
                           else Storage(0, StorageUnit.BYTES))
        
        # Sort top consumers
        top_urls = sorted(url_bandwidth.items(), 
                         key=lambda x: x[1].convert_to_bytes(), 
                         reverse=True)[:20]
        
        top_ips = sorted(ip_bandwidth.items(),
                        key=lambda x: x[1].convert_to_bytes(),
                        reverse=True)[:20]
        
        return {
            'analysis_period_hours': time_window,
            'total_bandwidth': total_bandwidth,
            'total_requests': total_requests,
            'average_request_size': avg_request_size,
            'parsing_errors': error_count,
            'hourly_bandwidth': dict(hourly_bandwidth),
            'status_bandwidth': dict(status_bandwidth),
            'top_urls': top_urls,
            'top_ips': top_ips
        }
    
    def generate_bandwidth_report(self, analysis: Dict[str, any]) -> str:
        """Generate human-readable bandwidth report."""
        report = f"📈 Bandwidth Analysis Report\n"
        report += f"Analysis Period: {analysis['analysis_period_hours']} hours\n"
        report += "=" * 60 + "\n\n"
        
        # Summary statistics
        report += f"📊 Summary:\n"
        report += f"  Total Bandwidth: {analysis['total_bandwidth'].auto_scale()}\n"
        report += f"  Total Requests: {analysis['total_requests']:,}\n"
        report += f"  Average Request Size: {analysis['average_request_size'].auto_scale()}\n"
        report += f"  Parsing Errors: {analysis['parsing_errors']:,}\n\n"
        
        # Status code breakdown
        if analysis['status_bandwidth']:
            report += f"📋 Bandwidth by Status Code:\n"
            for status, bandwidth in sorted(analysis['status_bandwidth'].items()):
                percentage = (bandwidth / analysis['total_bandwidth']) * 100
                report += f"  {status}: {bandwidth.auto_scale()} ({percentage:.1f}%)\n"
            report += "\n"
        
        # Top URLs
        if analysis['top_urls']:
            report += f"🔥 Top URLs by Bandwidth:\n"
            for i, (url, bandwidth) in enumerate(analysis['top_urls'][:10], 1):
                percentage = (bandwidth / analysis['total_bandwidth']) * 100
                report += f"  {i:2d}. {bandwidth.auto_scale():>8} ({percentage:4.1f}%) - {url}\n"
            report += "\n"
        
        # Top IPs
        if analysis['top_ips']:
            report += f"🌐 Top IPs by Bandwidth:\n"
            for i, (ip, bandwidth) in enumerate(analysis['top_ips'][:10], 1):
                percentage = (bandwidth / analysis['total_bandwidth']) * 100
                report += f"  {i:2d}. {bandwidth.auto_scale():>8} ({percentage:4.1f}%) - {ip}\n"
            report += "\n"
        
        # Hourly breakdown (last 24 hours)
        if analysis['hourly_bandwidth']:
            report += f"⏰ Hourly Bandwidth (Last 24 Hours):\n"
            sorted_hours = sorted(analysis['hourly_bandwidth'].items())
            for hour, bandwidth in sorted_hours[-24:]:
                report += f"  {hour}: {bandwidth.auto_scale()}\n"
        
        return report
    
    def detect_anomalies(self, analysis: Dict[str, any]) -> List[Dict[str, any]]:
        """Detect bandwidth usage anomalies."""
        anomalies = []
        
        # Check for unusually large requests
        avg_size = analysis['average_request_size']
        large_request_threshold = avg_size * 10  # 10x average
        
        for url, bandwidth in analysis['top_urls']:
            # Estimate request count (rough)
            estimated_requests = bandwidth / avg_size if avg_size.convert_to_bytes() > 0 else 1
            avg_per_request = bandwidth / estimated_requests
            
            if avg_per_request > large_request_threshold:
                anomalies.append({
                    'type': 'large_requests',
                    'url': url,
                    'bandwidth': bandwidth,
                    'estimated_avg_size': avg_per_request,
                    'threshold': large_request_threshold
                })
        
        # Check for high-bandwidth IPs
        total_bandwidth = analysis['total_bandwidth']
        high_usage_threshold = total_bandwidth * 0.1  # 10% of total
        
        for ip, bandwidth in analysis['top_ips']:
            if bandwidth > high_usage_threshold:
                percentage = (bandwidth / total_bandwidth) * 100
                anomalies.append({
                    'type': 'high_bandwidth_ip',
                    'ip': ip,
                    'bandwidth': bandwidth,
                    'percentage': percentage
                })
        
        return anomalies

# Usage example
analyzer = LogFileAnalyzer()

# Analyze recent logs
log_files = [
    '/var/log/nginx/access.log',
    '/var/log/nginx/access.log.1',
    '/var/log/apache2/access.log'
]

try:
    analysis = analyzer.analyze_bandwidth_usage(log_files, time_window=24)
    report = analyzer.generate_bandwidth_report(analysis)
    print(report)
    
    # Check for anomalies
    anomalies = analyzer.detect_anomalies(analysis)
    if anomalies:
        print("\n🚨 Detected Anomalies:")
        for anomaly in anomalies:
            if anomaly['type'] == 'large_requests':
                print(f"  Large requests to {anomaly['url']}: {anomaly['bandwidth'].auto_scale()}")
            elif anomaly['type'] == 'high_bandwidth_ip':
                print(f"  High bandwidth IP {anomaly['ip']}: {anomaly['bandwidth'].auto_scale()} ({anomaly['percentage']:.1f}%)")
                
except Exception as e:
    print(f"Analysis failed: {e}")
```

## 🎮 Gaming and Media

### Game Asset Manager

Manage game assets and optimize storage:

```python
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple

class GameAssetManager:
    """Manage game assets with storage optimization."""
    
    def __init__(self, assets_dir: str, cache_dir: str = None):
        self.assets_dir = Path(assets_dir)
        self.cache_dir = Path(cache_dir) if cache_dir else self.assets_dir / '.cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        # Asset categories with typical sizes
        self.asset_categories = {
            'textures': ['.png', '.jpg', '.jpeg', '.tga', '.dds', '.exr'],
            'models': ['.fbx', '.obj', '.dae', '.gltf', '.glb'],
            'audio': ['.wav', '.mp3', '.ogg', '.flac', '.aiff'],
            'video': ['.mp4', '.mov', '.avi', '.webm'],
            'scripts': ['.cs', '.js', '.lua', '.py'],
            'shaders': ['.hlsl', '.glsl', '.cg', '.shader'],
            'data': ['.json', '.xml', '.yaml', '.csv']
        }
    
    def scan_assets(self) -> Dict[str, any]:
        """Scan all assets and categorize by type."""
        asset_info = {
            'categories': {},
            'total_size': Storage(0, StorageUnit.BYTES),
            'total_files': 0,
            'duplicates': [],
            'large_files': [],
            'optimization_suggestions': []
        }
        
        # Initialize category tracking
        for category in self.asset_categories:
            asset_info['categories'][category] = {
                'files': [],
                'total_size': Storage(0, StorageUnit.BYTES),
                'file_count': 0
            }
        
        asset_info['categories']['other'] = {
            'files': [],
            'total_size': Storage(0, StorageUnit.BYTES),
            'file_count': 0
        }
        
        # File hash tracking for duplicate detection
        file_hashes = {}
        
        # Scan all files
        for file_path in self.assets_dir.rglob('*'):
            if file_path.is_file():
                try:
                    file_size = Storage.get_size_from_path(file_path)
                    asset_info['total_size'] += file_size
                    asset_info['total_files'] += 1
                    
                    # Categorize file
                    category = self._categorize_file(file_path)
                    
                    file_info = {
                        'path': str(file_path.relative_to(self.assets_dir)),
                        'size': file_size,
                        'extension': file_path.suffix.lower()
                    }
                    
                    asset_info['categories'][category]['files'].append(file_info)
                    asset_info['categories'][category]['total_size'] += file_size
                    asset_info['categories'][category]['file_count'] += 1
                    
                    # Check for large files (>50MB)
                    if file_size > Storage(50, StorageUnit.MB):
                        asset_info['large_files'].append(file_info)
                    
                    # Calculate hash for duplicate detection
                    file_hash = self._calculate_file_hash(file_path)
                    if file_hash in file_hashes:
                        # Found duplicate
                        original_file = file_hashes[file_hash]
                        asset_info['duplicates'].append({
                            'original': original_file,
                            'duplicate': file_info,
                            'wasted_space': file_size
                        })
                    else:
                        file_hashes[file_hash] = file_info
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
        
        # Generate optimization suggestions
        asset_info['optimization_suggestions'] = self._generate_optimization_suggestions(asset_info)
        
        return asset_info
    
    def _categorize_file(self, file_path: Path) -> str:
        """Categorize file based on extension."""
        extension = file_path.suffix.lower()
        
        for category, extensions in self.asset_categories.items():
            if extension in extensions:
                return category
        
        return 'other'
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for duplicate detection."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return f"error_{file_path.name}"
    
    def _generate_optimization_suggestions(self, asset_info: Dict) -> List[Dict[str, any]]:
        """Generate optimization suggestions based on asset analysis."""
        suggestions = []
        
        # Check for excessive texture sizes
        texture_category = asset_info['categories']['textures']
        if texture_category['total_size'] > Storage(1, StorageUnit.GB):
            large_textures = [f for f in texture_category['files'] 
                            if f['size'] > Storage(10, StorageUnit.MB)]
            if large_textures:
                suggestions.append({
                    'type': 'texture_optimization',
                    'severity': 'medium',
                    'description': f"Found {len(large_textures)} large textures (>10MB)",
                    'potential_savings': sum(f['size'] for f in large_textures) * 0.3,  # Estimate 30% compression
                    'action': 'Consider compressing textures or using lower resolution versions'
                })
        
        # Check for duplicate files
        if asset_info['duplicates']:
            total_wasted = sum(dup['wasted_space'] for dup in asset_info['duplicates'])
            suggestions.append({
                'type': 'duplicate_removal',
                'severity': 'high',
                'description': f"Found {len(asset_info['duplicates'])} duplicate files",
                'potential_savings': total_wasted,
                'action': 'Remove duplicate files to save space'
            })
        
        # Check for uncompressed audio
        audio_category = asset_info['categories']['audio']
        wav_files = [f for f in audio_category['files'] if f['extension'] == '.wav']
        if wav_files and len(wav_files) > 10:
            wav_size = sum(f['size'] for f in wav_files)
            suggestions.append({
                'type': 'audio_compression',
                'severity': 'medium',
                'description': f"Found {len(wav_files)} uncompressed WAV files",
                'potential_savings': wav_size * 0.7,  # Estimate 70% compression
                'action': 'Convert WAV files to OGG or MP3 for better compression'
            })
        
        return suggestions
    
    def generate_asset_report(self, asset_info: Dict) -> str:
        """Generate comprehensive asset report."""
        report = "🎮 Game Asset Analysis Report\n"
        report += "=" * 50 + "\n\n"
        
        # Summary
        report += f"📊 Summary:\n"
        report += f"  Total Assets: {asset_info['total_files']:,} files\n"
        report += f"  Total Size: {asset_info['total_size'].auto_scale()}\n"
        report += f"  Duplicates: {len(asset_info['duplicates'])}\n"
        report += f"  Large Files (>50MB): {len(asset_info['large_files'])}\n\n"
        
        # Category breakdown
        report += f"📁 Asset Categories:\n"
        for category, info in asset_info['categories'].items():
            if info['file_count'] > 0:
                percentage = (info['total_size'] / asset_info['total_size']) * 100
                avg_size = info['total_size'] / info['file_count']
                report += f"  {category.title()}:\n"
                report += f"    Files: {info['file_count']:,}\n"
                report += f"    Size: {info['total_size'].auto_scale()} ({percentage:.1f}%)\n"
                report += f"    Avg Size: {avg_size.auto_scale()}\n"
        report += "\n"
        
        # Large files
        if asset_info['large_files']:
            report += f"🔍 Large Files (>50MB):\n"
            sorted_large = sorted(asset_info['large_files'], 
                                key=lambda x: x['size'].convert_to_bytes(), 
                                reverse=True)
            for file_info in sorted_large[:10]:
                report += f"  {file_info['size'].auto_scale():>8} - {file_info['path']}\n"
            report += "\n"
        
        # Duplicates
        if asset_info['duplicates']:
            total_wasted = sum(dup['wasted_space'] for dup in asset_info['duplicates'])
            report += f"🔄 Duplicate Files ({len(asset_info['duplicates'])} pairs):\n"
            report += f"  Wasted Space: {total_wasted.auto_scale()}\n"
            for dup in asset_info['duplicates'][:5]:
                report += f"    {dup['duplicate']['size'].auto_scale()} - {dup['original']['path']} = {dup['duplicate']['path']}\n"
            if len(asset_info['duplicates']) > 5:
                report += f"    ... and {len(asset_info['duplicates']) - 5} more\n"
            report += "\n"
        
        # Optimization suggestions
        if asset_info['optimization_suggestions']:
            report += f"💡 Optimization Suggestions:\n"
            total_potential_savings = Storage(0, StorageUnit.BYTES)
            
            for suggestion in asset_info['optimization_suggestions']:
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(suggestion['severity'], '🔵')
                potential_savings = suggestion['potential_savings']
                total_potential_savings += potential_savings
                
                report += f"  {severity_icon} {suggestion['description']}\n"
                report += f"    Potential Savings: {potential_savings.auto_scale()}\n"
                report += f"    Action: {suggestion['action']}\n"
            
            report += f"\n  💰 Total Potential Savings: {total_potential_savings.auto_scale()}\n"
        
        return report
    
    def optimize_duplicates(self, dry_run: bool = True) -> Dict[str, any]:
        """Remove or hardlink duplicate files."""
        asset_info = self.scan_assets()
        duplicates = asset_info['duplicates']
        
        if not duplicates:
            return {'removed': 0, 'space_saved': Storage(0, StorageUnit.BYTES)}
        
        removed_count = 0
        space_saved = Storage(0, StorageUnit.BYTES)
        
        for duplicate in duplicates:
            duplicate_path = self.assets_dir / duplicate['duplicate']['path']
            
            if dry_run:
                print(f"Would remove: {duplicate_path}")
                removed_count += 1
                space_saved += duplicate['wasted_space']
            else:
                try:
                    duplicate_path.unlink()
                    print(f"Removed: {duplicate_path}")
                    removed_count += 1
                    space_saved += duplicate['wasted_space']
                except Exception as e:
                    print(f"Failed to remove {duplicate_path}: {e}")
        
        return {
            'removed': removed_count,
            'space_saved': space_saved,
            'dry_run': dry_run
        }

# Usage example
asset_manager = GameAssetManager('./game_assets')

# Scan and analyze assets
print("🔍 Scanning game assets...")
asset_info = asset_manager.scan_assets()

# Generate report
report = asset_manager.generate_asset_report(asset_info)
print(report)

# Optimize duplicates (dry run first)
print("\n🔧 Checking for duplicate optimization...")
optimization_result = asset_manager.optimize_duplicates(dry_run=True)
print(f"Could save {optimization_result['space_saved'].auto_scale()} by removing {optimization_result['removed']} duplicates")
```

## 🔐 Security and Compliance

### Data Retention Monitor

Monitor and enforce data retention policies:

```python
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class DataRetentionMonitor:
    """Monitor and enforce data retention policies."""
    
    def __init__(self, config_file: str = 'retention_policies.json'):
        self.config_file = config_file
        self.policies = self._load_policies()
        
    def _load_policies(self) -> Dict[str, any]:
        """Load retention policies from configuration file."""
        default_policies = {
            'log_files': {
                'paths': ['/var/log/**/*.log', '/opt/app/logs/**/*.log'],
                'retention_days': 90,
                'size_threshold': '10 GB',
                'compress_after_days': 7,
                'archive_location': '/archive/logs'
            },
            'user_uploads': {
                'paths': ['/uploads/**/*'],
                'retention_days': 365,
                'size_threshold': '100 GB',
                'compress_after_days': 30,
                'archive_location': '/archive/uploads'
            },
            'temp_files': {
                'paths': ['/tmp/**/*', '/var/tmp/**/*'],
                'retention_days': 7,
                'size_threshold': '1 GB',
                'compress_after_days': 1,
                'archive_location': None  # Delete, don't archive
            },
            'database_backups': {
                'paths': ['/backups/db/**/*.sql', '/backups/db/**/*.dump'],
                'retention_days': 30,
                'size_threshold': '50 GB',
                'compress_after_days': 1,
                'archive_location': '/archive/backups'
            }
        }
        
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                # Create default config file
                with open(self.config_file, 'w') as f:
                    json.dump(default_policies, f, indent=2)
                return default_policies
        except Exception as e:
            print(f"Error loading policies: {e}, using defaults")
            return default_policies
    
    def scan_policy_violations(self) -> Dict[str, any]:
        """Scan for files violating retention policies."""
        violations = {
            'expired_files': [],
            'oversized_directories': [],
            'compression_candidates': [],
            'total_violations': 0,
            'total_recoverable_space': Storage(0, StorageUnit.BYTES)
        }
        
        for policy_name, policy in self.policies.items():
            print(f"Checking policy: {policy_name}")
            
            retention_cutoff = datetime.now() - timedelta(days=policy['retention_days'])
            compression_cutoff = datetime.now() - timedelta(days=policy['compress_after_days'])
            size_threshold = Storage.parse(policy['size_threshold'])
            
            # Check each path pattern
            for path_pattern in policy['paths']:
                try:
                    # Use glob to find matching files
                    from glob import glob
                    matching_paths = glob(path_pattern, recursive=True)
                    
                    for file_path in matching_paths:
                        file_path = Path(file_path)
                        
                        if not file_path.exists() or not file_path.is_file():
                            continue
                        
                        try:
                            file_size = Storage.get_size_from_path(file_path)
                            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                            
                            # Check for expired files
                            if file_mtime < retention_cutoff:
                                violations['expired_files'].append({
                                    'policy': policy_name,
                                    'path': str(file_path),
                                    'size': file_size,
                                    'age_days': (datetime.now() - file_mtime).days,
                                    'action': 'archive' if policy['archive_location'] else 'delete'
                                })
                                violations['total_recoverable_space'] += file_size
                            
                            # Check for compression candidates
                            elif (file_mtime < compression_cutoff and 
                                  not str(file_path).endswith(('.gz', '.zip', '.bz2')) and
                                  file_size > Storage(1, StorageUnit.MB)):
                                
                                violations['compression_candidates'].append({
                                    'policy': policy_name,
                                    'path': str(file_path),
                                    'size': file_size,
                                    'age_days': (datetime.now() - file_mtime).days,
                                    'estimated_compressed_size': file_size * 0.3  # Estimate 70% compression
                                })
                        
                        except Exception as e:
                            print(f"Error processing {file_path}: {e}")
                            continue
                
                except Exception as e:
                    print(f"Error processing pattern {path_pattern}: {e}")
                    continue
            
            # Check directory sizes
            for path_pattern in policy['paths']:
                try:
                    # Get parent directories to check
                    parent_dirs = set()
                    for path in glob(path_pattern, recursive=True):
                        parent_dirs.add(str(Path(path).parent))
                    
                    for dir_path in parent_dirs:
                        try:
                            dir_size = Storage.get_size_from_path(dir_path)
                            
                            if dir_size > size_threshold:
                                violations['oversized_directories'].append({
                                    'policy': policy_name,
                                    'path': dir_path,
                                    'size': dir_size,
                                    'threshold': size_threshold,
                                    'overage': dir_size - size_threshold
                                })
                        
                        except Exception as e:
                            print(f"Error checking directory {dir_path}: {e}")
                            continue
                
                except Exception as e:
                    print(f"Error checking directories for {path_pattern}: {e}")
                    continue
        
        violations['total_violations'] = (
            len(violations['expired_files']) + 
            len(violations['oversized_directories']) + 
            len(violations['compression_candidates'])
        )
        
        return violations
    
    def generate_compliance_report(self, violations: Dict[str, any]) -> str:
        """Generate data retention compliance report."""
        report = "🔐 Data Retention Compliance Report\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "=" * 60 + "\n\n"
        
        # Summary
        report += f"📊 Summary:\n"
        report += f"  Total Violations: {violations['total_violations']}\n"
        report += f"  Expired Files: {len(violations['expired_files'])}\n"
        report += f"  Oversized Directories: {len(violations['oversized_directories'])}\n"
        report += f"  Compression Candidates: {len(violations['compression_candidates'])}\n"
        report += f"  Recoverable Space: {violations['total_recoverable_space'].auto_scale()}\n\n"
        
        # Expired files
        if violations['expired_files']:
            report += f"🗑️  Expired Files (Retention Policy Violated):\n"
            
            # Group by policy
            by_policy = {}
            for violation in violations['expired_files']:
                policy = violation['policy']
                if policy not in by_policy:
                    by_policy[policy] = []
                by_policy[policy].append(violation)
            
            for policy_name, policy_violations in by_policy.items():
                total_size = sum(v['size'] for v in policy_violations)
                report += f"  {policy_name} ({len(policy_violations)} files, {total_size.auto_scale()}):\n"
                
                # Show top 5 largest files
                sorted_violations = sorted(policy_violations, 
                                         key=lambda x: x['size'].convert_to_bytes(), 
                                         reverse=True)
                for violation in sorted_violations[:5]:
                    report += f"    {violation['size'].auto_scale():>8} ({violation['age_days']} days) - {violation['path']}\n"
                
                if len(policy_violations) > 5:
                    report += f"    ... and {len(policy_violations) - 5} more files\n"
                report += "\n"
        
        # Oversized directories
        if violations['oversized_directories']:
            report += f"📁 Oversized Directories:\n"
            for violation in violations['oversized_directories']:
                report += f"  {violation['path']}\n"
                report += f"    Size: {violation['size'].auto_scale()} (threshold: {violation['threshold'].auto_scale()})\n"
                report += f"    Overage: {violation['overage'].auto_scale()}\n"
                report += f"    Policy: {violation['policy']}\n"
            report += "\n"
        
        # Compression candidates
        if violations['compression_candidates']:
            total_compressible = sum(v['size'] for v in violations['compression_candidates'])
            estimated_savings = sum(v['size'] - v['estimated_compressed_size'] 
                                  for v in violations['compression_candidates'])
            
            report += f"🗜️  Compression Candidates:\n"
            report += f"  Total Size: {total_compressible.auto_scale()}\n"
            report += f"  Estimated Savings: {estimated_savings.auto_scale()}\n"
            
            # Group by policy
            by_policy = {}
            for violation in violations['compression_candidates']:
                policy = violation['policy']
                if policy not in by_policy:
                    by_policy[policy] = []
                by_policy[policy].append(violation)
            
            for policy_name, policy_violations in by_policy.items():
                policy_size = sum(v['size'] for v in policy_violations)
                report += f"  {policy_name} ({len(policy_violations)} files, {policy_size.auto_scale()})\n"
        
        # Recommendations
        report += "\n💡 Recommendations:\n"
        
        if violations['expired_files']:
            expired_size = sum(v['size'] for v in violations['expired_files'])
            report += f"  1. Archive or delete {len(violations['expired_files'])} expired files to free {expired_size.auto_scale()}\n"
        
        if violations['compression_candidates']:
            comp_savings = sum(v['size'] - v['estimated_compressed_size'] 
                             for v in violations['compression_candidates'])
            report += f"  2. Compress {len(violations['compression_candidates'])} files to save ~{comp_savings.auto_scale()}\n"
        
        if violations['oversized_directories']:
            report += f"  3. Review {len(violations['oversized_directories'])} oversized directories for cleanup opportunities\n"
        
        if violations['total_violations'] == 0:
            report += "  ✅ All policies are currently in compliance!\n"
        
        return report
    
    def enforce_policies(self, dry_run: bool = True) -> Dict[str, any]:
        """Enforce retention policies by archiving/deleting files."""
        violations = self.scan_policy_violations()
        
        results = {
            'files_processed': 0,
            'files_deleted': 0,
            'files_archived': 0,
            'files_compressed': 0,
            'space_freed': Storage(0, StorageUnit.BYTES),
            'space_saved': Storage(0, StorageUnit.BYTES),
            'errors': [],
            'dry_run': dry_run
        }
        
        # Process expired files
        for violation in violations['expired_files']:
            results['files_processed'] += 1
            file_path = Path(violation['path'])
            
            if not dry_run:
                try:
                    if violation['action'] == 'archive':
                        # Archive file
                        policy = self.policies[violation['policy']]
                        archive_dir = Path(policy['archive_location'])
                        archive_dir.mkdir(parents=True, exist_ok=True)
                        
                        archive_path = archive_dir / file_path.name
                        file_path.rename(archive_path)
                        
                        results['files_archived'] += 1
                        print(f"Archived: {file_path} -> {archive_path}")
                    else:
                        # Delete file
                        file_path.unlink()
                        results['files_deleted'] += 1
                        results['space_freed'] += violation['size']
                        print(f"Deleted: {file_path}")
                        
                except Exception as e:
                    error_msg = f"Failed to process {file_path}: {e}"
                    results['errors'].append(error_msg)
                    print(error_msg)
            else:
                action = "Archive" if violation['action'] == 'archive' else "Delete"
                print(f"Would {action.lower()}: {file_path} ({violation['size'].auto_scale()})")
                if violation['action'] == 'delete':
                    results['space_freed'] += violation['size']
        
        return results

# Usage example
monitor = DataRetentionMonitor()

# Scan for violations
print("🔍 Scanning for retention policy violations...")
violations = monitor.scan_policy_violations()

# Generate compliance report
report = monitor.generate_compliance_report(violations)
print(report)

# Enforce policies (dry run first)
if violations['total_violations'] > 0:
    print("\n🔧 Enforcing policies (dry run)...")
    enforcement_result = monitor.enforce_policies(dry_run=True)
    
    print(f"Would process {enforcement_result['files_processed']} files")
    print(f"Would free {enforcement_result['space_freed'].auto_scale()} of space")
    
    # Uncomment to actually enforce policies
    # enforcement_result = monitor.enforce_policies(dry_run=False)
```

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Update existing documentation to English", "status": "completed", "priority": "high", "id": "1"}, {"content": "Complete API reference documentation", "status": "completed", "priority": "high", "id": "2"}, {"content": "Create user guide sections", "status": "completed", "priority": "medium", "id": "3"}, {"content": "Add examples and real-world scenarios", "status": "completed", "priority": "medium", "id": "4"}, {"content": "Update banner URL in documentation", "status": "completed", "priority": "low", "id": "5"}]
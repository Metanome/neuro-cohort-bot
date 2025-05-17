"""
Status monitoring module for the Neuro Cohort Bot.

This module tracks operational metrics, errors, and source statuses.
It provides functionality to generate status reports and maintain
a persistent record of the bot's operation over time.
"""
import os
import json
import time
import logging
from datetime import datetime, timedelta

STATUS_FILE = os.path.join(os.path.dirname(__file__), '../status.json')

class StatusMonitor:
    def __init__(self):
        self.status = {
            'last_run': None,
            'last_run_timestamp': None,
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'errors': [],
            'posts_count': 0,
            'sources_status': {}
        }
        self.load_status()
        
    def load_status(self):
        """Load status from file"""
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, 'r') as f:
                    self.status = json.load(f)
            except Exception as e:
                logging.error(f"Error loading status file: {e}")
    
    def save_status(self):
        """Save status to file"""
        try:
            with open(STATUS_FILE, 'w') as f:
                json.dump(self.status, f, indent=2, default=str)
        except Exception as e:
            logging.error(f"Error saving status file: {e}")
            
    def record_run_start(self):
        """Record the start of a data collection run"""
        current_time = datetime.now()
        self.status['last_run'] = current_time.isoformat()
        self.status['last_run_formatted'] = current_time.strftime("%B %d, %Y at %I:%M %p")
        self.status['last_run_timestamp'] = time.time()
        self.status['total_runs'] += 1
        self.temp_errors = []  # Store temporary errors for this run
        self.save_status()
        return self.status['total_runs']  # Return run ID
    
    def record_run_complete(self, success=True, posts=0, source_statuses=None):
        """Record the completion of a data collection run"""
        if success:
            self.status['successful_runs'] += 1
        else:
            self.status['failed_runs'] += 1
            
        # Add any new posts to the count
        self.status['posts_count'] += posts
        
        # Update source statuses
        if source_statuses:
            self.status['sources_status'] = source_statuses
        
        # Add any errors from this run
        if self.temp_errors:
            # Keep only the last 50 errors
            self.status['errors'] = self.temp_errors + self.status['errors']
            self.status['errors'] = self.status['errors'][:50]
            
        self.save_status()
    
    def record_error(self, source_name, error_msg):
        """Record an error that occurred during data collection"""
        current_time = datetime.now()
        formatted_time = current_time.strftime("%B %d, %Y at %I:%M %p")
        error_entry = {
            'timestamp': current_time.isoformat(),
            'formatted_time': formatted_time,
            'source': source_name,
            'error': error_msg
        }
        self.temp_errors.append(error_entry)
    
    def get_health_status(self):
        """Get the overall health status of the bot"""
        if not self.status['last_run_timestamp']:
            return "Unknown"
            
        # Check if the bot has run recently (within 2x the expected interval)
        # Default expectation is 30 minutes
        expected_interval = 30 * 60  # seconds
        
        last_run = float(self.status['last_run_timestamp'])
        now = time.time()
        
        if now - last_run > expected_interval * 2:
            return "Unhealthy - Last run too long ago"
            
        # Check if errors are too frequent
        error_rate = 0
        if self.status['total_runs'] > 0:
            error_rate = self.status['failed_runs'] / self.status['total_runs']
            
        if error_rate > 0.3:  # If more than 30% of runs have errors
            return "Unhealthy - High error rate"
            
        return "Healthy"

# Global status monitor instance
monitor = StatusMonitor()

def get_monitor():
    """Get the global status monitor instance"""
    return monitor

def send_status_report(telegram_bot=None):
    """Generate and send a status report"""
    status = monitor.status
    health = monitor.get_health_status()
    
    report = "🤖 *Neuro Cohort Bot Status Report*\n\n"
    report += f"*Health:* {health}\n"
    
    # Format last run date to human-readable format
    if 'last_run_formatted' in status:
        report += f"*Last run:* {status['last_run_formatted']}\n"
    else:
        last_run_str = status.get('last_run')
        if last_run_str:
            try:
                last_run_dt = datetime.fromisoformat(last_run_str)
                formatted_date = last_run_dt.strftime("%B %d, %Y at %I:%M %p")
                report += f"*Last run:* {formatted_date}\n"
            except ValueError:
                report += f"*Last run:* {last_run_str}\n"
        else:
            report += "*Last run:* Never\n"
        
    report += f"*Total runs:* {status['total_runs']}\n"
    report += f"*Successful:* {status['successful_runs']}\n"
    report += f"*Failed:* {status['failed_runs']}\n"
    report += f"*Posts made:* {status['posts_count']}\n\n"
    
    # Add source status
    report += "*Sources:*\n"
    for source, source_status in status.get('sources_status', {}).items():
        report += f"- {source}: {source_status}\n"
    
    # Add recent errors (up to 5)
    if status['errors']:
        report += "\n*Recent errors:*\n"
        for i, error in enumerate(status['errors'][:5]):
            # Use formatted time if available, otherwise try to format the timestamp
            if 'formatted_time' in error:
                error_time = error['formatted_time']
            else:
                try:
                    error_dt = datetime.fromisoformat(error['timestamp'])
                    error_time = error_dt.strftime("%B %d, %Y at %I:%M %p")
                except (ValueError, KeyError):
                    error_time = "Unknown time"
            
            report += f"{i+1}. *{error_time}* [{error['source']}] {error['error']}\n"
    
    logging.info("Generated status report")
    
    if telegram_bot:
        try:
            return report  # Return the report for sending
        except Exception as e:
            logging.error(f"Error sending status report: {e}")
            
    return report


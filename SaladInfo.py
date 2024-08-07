import os, re, glob, yaml
from time import sleep, localtime, strftime
from datetime import datetime
from psutil import virtual_memory
from plyer import notification

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

try:
    logs_directory = config['logs_directory']
    polling_interval = config['polling_interval']
except KeyError as e:
    raise ReferenceError(f"Missing config.yml key: {e}")

# Define regular expressions for extracting information
timestamp_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
patterns = {
    # 'Wallet Balance': re.compile(r'Wallet: Current\(([\d.]+)\)'),
    'Wallet': re.compile(r'Wallet: (.*)'),
    'Predicted Earnings': re.compile(r'Predicted Earnings Report: (([\d.]+) from \(([^\)]+)\))'),
    'Workloads': re.compile(r'Workloads Received: (.*)'),
    # 'Workload IDs': re.compile(r'Workload Ids: (.*)'),
    'Workload IDs': re.compile(r'Workload Received: (.*)'),
    # 'Failed Workloads': re.compile(r'({ "id": ".*", "status": "WORKLOAD_STATUS_FAILED", "detail": ".*" })')
}

def find_newest_log_file(logs_directory):
    logs_directory = os.path.expandvars(logs_directory)
    log_files = glob.glob(os.path.join(logs_directory, 'log-*.txt'))
    
    if not log_files:
        raise FileNotFoundError("No log files found.")
    
    # Get the newest log file based on modification time
    newest_log_file = max(log_files, key=os.path.getmtime)
    return newest_log_file

def extract_salad_info(log_file_path):
    # Read the latest log file
    with open(log_file_path, 'r') as file:
        # Read all lines and search for lines with data
        lines = file.readlines()
    
    # Initialize dicctionaries to store matches and their corresponding timestamps
    matches = {pattern: None for pattern in patterns}
    timestamps = {pattern: None for pattern in patterns}

    # Iterate through lines in reverse order
    for line in reversed(lines):
        for pattern_name, pattern in patterns.items():
            # Skip patterns that have already been found
            if matches[pattern_name]:
                continue
            # Search for the pattern in the line
            match = pattern.search(line)
            if match:
                # Store the match
                matches[pattern_name] = match
                # Extract and store timestamp that corresponds with match
                timestamp_match = timestamp_pattern.match(line)
                timestamps[pattern_name] = timestamp_match
        
        if all(matches.values()):
            # Exit the loop to stop searching once all patterns have been found
            break
    # Return all matches and their corresponding timestamps when found
    return matches, timestamps

def timestamp_difference(timestamp):
    timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    seconds_diff = int((datetime.now() - timestamp_dt).total_seconds())
    if seconds_diff > 59:
        minutes_diff = seconds_diff // 60
        seconds_diff = seconds_diff % 60
        if minutes_diff > 59:
            hours_diff = minutes_diff // 60
            minutes_diff = minutes_diff % 60
            diff_string = "(" + str(hours_diff) + "h " + str(minutes_diff) + "m ago)"
        else:
            diff_string = "(" + str(minutes_diff) + "m " + str(seconds_diff) + "s ago)"
    else:
        diff_string = "(" + str(seconds_diff) + "s ago)"
    return diff_string

#def notify_failed_workload(timestamp, failed_workload):
    if failed_workload:
        if not last_failed_state:
            notification.notify(
                title = "Salad Info",
                message = f"Workload {failed_workload.group(1)} failed at {timestamp.group(1)}.",
                app_icon = "image.ico",
                timeout = 5
            )
        elif failed_workload.group(1) != last_failed_state.group(1):
            notification.notify(
                title = "Salad Info",
                message = f"Workload {failed_workload.group(1)} failed at {timestamp.group(1)}.",
                app_icon = "image.ico",
                timeout = 5
            )
    return failed_workload

last_failed_state = None

while True:
    # Find the newest log file in the specified directory
    newest_log_file_path = find_newest_log_file(logs_directory)
    if newest_log_file_path:
        # Extract and display information from the newest log file
        matches, timestamps = extract_salad_info(newest_log_file_path)
        # last_failed_state = notify_failed_workload(timestamps['Failed Workloads'], matches['Failed Workloads'])
        # Print extracted information
        for _ in range(polling_interval):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Reading log file: {newest_log_file_path}")
            print("Memory Usage: %.2f GB (%.1f%%)" % (virtual_memory()[3]/(pow(10,9)), virtual_memory()[2]))
            print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
            for pattern_name, pattern in patterns.items():
                match = matches[pattern_name]
                if match:
                    timestamp = timestamps[pattern_name].group(1)
                    print(f"{timestamp} {timestamp_difference(timestamp) : <13} | {pattern_name}: {match.group(1)}")
            sleep(1)
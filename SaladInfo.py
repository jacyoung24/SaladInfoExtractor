import os, re, glob, yaml
from time import sleep, localtime, strftime
from datetime import datetime
from psutil import virtual_memory

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
    'Predicted Earnings': re.compile(r'Predicted Earnings Report: (([\d.]+) from \(([^\)]+)\))'),
    'Wallet Balance': re.compile(r'Wallet: Current\(([\d.]+)\)'),
    'Workloads': re.compile(r'Workloads Received: (.*)'),
    'Workload IDs': re.compile(r'Workload Ids: (.*)'),
    'Failed Workloads': re.compile(r'({ "id": ".*", "status": "WORKLOAD_STATUS_FAILED", "detail": ".*" })')
}

# Initialize variables for timestamp and predicted earnings
matches = {pattern: None for pattern in patterns}
timestamps = {pattern: None for pattern in patterns}

def find_newest_log_file(logs_directory):
    logs_directory = os.path.expandvars(logs_directory)
    log_files = glob.glob(os.path.join(logs_directory, 'log-*.txt'))
    
    if not log_files:
        # print("Error: No log files found.")
        # return None
        raise FileNotFoundError("No log files found.")
    
    # Get the newest log file based on modification time
    newest_log_file = max(log_files, key=os.path.getmtime)
    return newest_log_file

def extract_salad_info(log_file_path):
    # Read the latest log file
    with open(log_file_path, 'r') as file:
        # Read all lines and search for lines with data
        lines = file.readlines()

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

def timestamp_difference(timestamp):
    timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    seconds_diff = int((datetime.now() - timestamp_dt).total_seconds())
    diff_string = "(" + str(seconds_diff) + "s ago)"
    return diff_string

while True:
    # Find the newest log file in the specified directory
    newest_log_file_path = find_newest_log_file(logs_directory)

    if newest_log_file_path:
        # Extract and display information from the newest log file
        extract_salad_info(newest_log_file_path)
        # Print extracted information
        for _ in range(polling_interval):
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Reading log file: {newest_log_file_path}")
            print(f"Memory Usage: {virtual_memory()[2]}%")
            print(strftime("%Y-%m-%d %H:%M:%S", localtime()))
            for pattern_name, pattern in patterns.items():
                match = matches[pattern_name]
                if match:
                    timestamp = timestamps[pattern_name].group(1)
                    print(f"{timestamp} {timestamp_difference(timestamp) : <10} | {pattern_name}: {match.group(1)}")
            sleep(1)
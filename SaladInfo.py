import os
import re
import glob
from time import sleep, localtime, strftime
from datetime import datetime
from psutil import virtual_memory

def find_newest_log_file(logs_directory):
    log_files = glob.glob(os.path.join(logs_directory, 'log-*.txt'))
    
    if not log_files:
        print("Error: No log files found.")
        return None
    
    # Get the newest log file based on modification time
    newest_log_file = max(log_files, key=os.path.getmtime)
    print(f"Selected newest log file: {newest_log_file}")
    return newest_log_file

def extract_salad_info(log_file_path):
    # Check if the file exists
    if not os.path.exists(log_file_path):
        print(f"Error: Log file '{log_file_path}' not found.")
        return

    print(f"Reading log file: {log_file_path}")
    print(f"Memory Usage: {virtual_memory()[2]}%")
    print(strftime("%Y-%m-%d %H:%M:%S", localtime()))

    # Read the latest log file
    with open(log_file_path, 'r') as file:
        # Read all lines and search for lines with data
        lines = file.readlines()

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

    # Iterate through lines in reverse order
    for line in reversed(lines):
        for pattern_name, pattern in patterns.items():
            if matches[pattern_name]:
                continue
            # Search for the pattern in the line
            match = pattern.search(line)
            if match:
                # Store the match
                matches[pattern_name] = match
                # Extract timestamp
                timestamp_match = timestamp_pattern.match(line)
                timestamp_str = timestamp_match.group(1)
                timestamp_dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()
                seconds_diff = int((current_time - timestamp_dt).total_seconds())
                diff_string = "(" + str(seconds_diff) + "s ago)"
                # Print extracted information
                print(f"{timestamp_str} {diff_string : <10} | {pattern_name}: {match.group(1)}")
        
        if all(matches.values()):
            # Exit the loop to stop searching once all patterns have been found
            break

# Specify the directory where Salad log files are located
logs_directory = 'C:\\ProgramData\\Salad\\logs'

# logs_directory = ".\\SaladInfoExtractor"

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    # Find the newest log file in the specified directory
    newest_log_file_path = find_newest_log_file(logs_directory)

    if newest_log_file_path:
        # Extract and display information from the newest log file
        extract_salad_info(newest_log_file_path)
        sleep(1)
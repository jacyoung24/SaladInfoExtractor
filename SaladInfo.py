import os
import re
import glob
from time import sleep, localtime, strftime, strptime
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
    earnings_pattern = re.compile(r'Predicted Earnings Report: ([\d.]+) from \(([^\)]+)\)')
    wallet_balance_pattern = re.compile(r'Wallet: Current\(([\d.]+)\)')
    workloads_pattern = re.compile(r'Workloads Received: (.*)')
    ids_pattern = re.compile(r'Workload Ids: (.*)')

    # Initialize variables for timestamp and predicted earnings
    earnings_match = None
    wallet_balance_match = None
    workloads_match = None
    ids_match = None

    # Iterate through lines in reverse order
    for line in reversed(lines):
        # Extract timestamp
        timestamp_match = timestamp_pattern.match(line)

        # Extract predicted earnings information
        if earnings_match != 0:
            earnings_match = earnings_pattern.search(line)
        if wallet_balance_match != 0:
            wallet_balance_match = wallet_balance_pattern.search(line)
        if workloads_match != 0:
            workloads_match = workloads_pattern.search(line)
        if ids_match != 0:
            ids_match = ids_pattern.search(line)

        if earnings_match or wallet_balance_match or workloads_match or ids_match:
            # Print the extracted information
            if earnings_match:
                print(f"{timestamp_match.group(1)} | Predicted Earnings: {earnings_match.group(1)} from {earnings_match.group(2)}")
                earnings_match = 0
            if wallet_balance_match:
                print(f"{timestamp_match.group(1)} | Wallet Balance: {wallet_balance_match.group(1)}")
                wallet_balance_match = 0
            if workloads_match:
                print(f"{timestamp_match.group(1)} | Workloads: {workloads_match.group(1)}")
                workloads_match = 0
            if ids_match:
                print(f"{timestamp_match.group(1)} | Workload IDs: {ids_match.group(1)}")
                ids_match = 0
            
            if earnings_match == 0 and wallet_balance_match == 0 and workloads_match == 0 and ids_match == 0:
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
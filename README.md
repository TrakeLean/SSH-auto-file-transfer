# File Transfer Automation with Paramiko

This project automates secure file transfers from a local machine to a remote server over SSH using the Paramiko library. It enables recursive directory uploads, checks for existing files on the server, monitors transfer speeds, and calculates remaining disk space to avoid interruptions.

## Features

- **Recursive Directory Transfer**: Automatically transfers all files and folders within a specified directory to the remote server.
- **Transfer Progress and Speed Calculation**: Displays real-time progress and speed during file transfer.
- **Space Availability Check**: Ensures the server has enough disk space before each file transfer.
- **Resume and Replace Logic**: Checks for files already present on the server, resuming or replacing as necessary.

## Prerequisites

- **Python 3.x**
- **Paramiko**: Install using `pip install paramiko`

## Usage

1. **Set up the SSH Configuration**:
   Update the SSH credentials and server details in the script, specifically:

   ```python
   ssh_host = 'your_host'
   ssh_username = 'your_username'
   ssh_password = 'your_password'
   ```

2. **Running the Script**:
   Run the script from the command line, passing in the path to the directory you want to transfer:

   ```bash
   python transfer_script.py /path/to/local_directory
   ```

   This will connect to the specified SSH server and start transferring files to the corresponding directory.

## Functions Overview

### `calculate_rest(transferred, total, start_time)`

Calculates and displays the transfer progress, percentage completed, and speed in MB/s.

- **Arguments**:
  - `transferred`: Bytes transferred so far.
  - `total`: Total bytes of the file.
  - `start_time`: Timestamp for calculating speed.
  
### `transfer_files(sftp, local_path, remote_path, dir_list)`

Recursively transfers files from the specified local directory to the remote server, handling files and directories differently.

- **Arguments**:
  - `sftp`: Open SFTP client for transferring files.
  - `local_path`: Source directory path on the local machine.
  - `remote_path`: Target directory path on the server.
  - `dir_list`: List of files and directories on the remote server.

### SSH Configuration and Connection

The script establishes an SSH connection and sets up the necessary file transfer session using Paramiko's SSH and SFTP clients.

## Sample Output

The script provides real-time feedback on the transfer process, including:

- **Connection Status**: Notifies when the connection to the server is established and closed.
- **File Transfer Progress**: Shows progress for each file, speed, and size.
- **Space Alerts**: Warns if there's insufficient space on the server for the transfer.

## Error Handling

- **Space Check**: If a file cannot be transferred due to limited space, the transfer stops with a warning.
- **Existing File Check**: If a file already exists, it verifies the size. Files that are incomplete or smaller are overwritten, while matching files are skipped.

## License

This project is open source, licensed under the MIT License.

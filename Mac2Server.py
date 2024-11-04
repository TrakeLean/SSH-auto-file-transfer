import paramiko

import sys
import os
import traceback
import time



def calculate_rest(transferred, total, start_time):
    percentage = (transferred / total) * 100
    speed = transferred / (1024 * 1024 * (time.time() - start_time))
    print_msg = f' ~ {(((transferred/1024)/1024)/1024):.03f}/{(((total/1024)/1024)/1024):.03f}GB ({percentage:.2f}%) @ {speed:.2f} MB/s'
    print_msg_length = len(print_msg)
    print(f'{print_msg}\033[{print_msg_length}D', end='')
    if (percentage == 100):
        print("")
    

def transfer_files(sftp, local_path, remote_path, dir_list):
    """
    Recursively transfer files from local_path to remote_path.
    """
    new = True
    for name in os.listdir(local_path):
        local_file = os.path.join(local_path, name)
        remote_file = os.path.join(remote_path, name)
        size = (((os.path.getsize(local_file)/1024)/1024)/1024)

        if os.path.isdir(local_file):
            try:
                client.exec_command(f'mkdir -p \'{remote_file}\'')
                print("="*70)
                print(f'|| ~~ Folder: {name}')
                dir_list = sftp.listdir(remote_file)
            except:
                pass
            transfer_files(sftp, local_file, remote_file, dir_list)
        else:
            if not name.startswith('.'):
                if (new):
                    print("-"*70)
                    print(f'|| {local_file.split("/")[-3]} - {local_file.split("/")[-2]}')
                # Check if episode is already there
                if name in dir_list:
                    # Get file size
                    remote_size = (sftp.stat(remote_file).st_size)
                    remote_size_in_gb = ((((remote_size)/1024)/1024)/1024)
                    if (size > remote_size_in_gb):
                        print(f'||WARNING|| ~~~ Part of file here: {name}')
                        print(f' ~~~~~~~ || R ~ E ~ M ~ O ~ V ~ I ~ N ~ G || ~~~~~~~~~~~~')
                        # Delete file then rewrite (faster)
                        sftp.remove(remote_file)
                        print(f'||{size:.03f}gb|| ~~ Transerfering File: {name}', end='')
                        start_time = time.time()
                        sftp.put(local_file, remote_file, callback=lambda transferred, total: calculate_rest(transferred, total, start_time=start_time))
                    elif (size == remote_size_in_gb):
                        print(f'||{size:.03f}gb|| ~~~ File already here: {name}')
                        pass
                    else:
                        print(" || No space for file, ending script...")
                        return
                else:
                    # Execute df command to get available space
                    _, stdout, _ = client.exec_command('df -h /')

                    # Parse the output to get the available space value
                    output_lines = stdout.readlines()
                    if len(output_lines) > 1:
                        available_space = output_lines[1].split()[3]
                        if "G" in available_space:
                            available_space = float(available_space.replace("G", ""))
                        elif "M" in available_space:
                            available_space = ((float(available_space.replace("M", ""))/1024))
                        elif "K" in available_space:
                            available_space = (float(available_space.replace("K", ""))/1024/1024)
                            
                        if (available_space > size):
                            print(f'||{size:.03f}gb|| ~~ Transerfering File: {name}', end='')

                            start_time = time.time()
                            # We need to send in start_time to be able to calculate download speed
                            sftp.put(local_file, remote_file, callback=lambda transferred, total: calculate_rest(transferred, total, start_time=start_time))
                            # client.exec_command(f'rsync -avz --progress {local_file} {ssh_username}@{ssh_host}:{remote_file}')
                        else:
                            print(f'|| ~~~~~~~~~~~~ NO MORE SPACE ON SERVER! Space left {available_space}')
                            return

                new = False


if len(sys.argv) > 0:
    client = paramiko.SSHClient()

    #LOAD HOST KEYS
    client.load_host_keys('/Users/tareklein/.ssh/known_hosts')
    client.load_system_host_keys()

    #Known_host policy
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_host = ''
    ssh_username = ''
    ssh_password = ''
    
    client.connect(ssh_host, username=ssh_username, password=ssh_password)

    _, stdout, _ = client.exec_command('pwd')
    ssh_directory = stdout.read().decode("utf8").split("\n")[0]

    # Start padding
    print("")
    print("="*70)
    print(f'Starting SSH connection: {ssh_username}@{ssh_host}')
    print("="*70)
    print("")
    
    # Open SSH file transfer protocol
    sftp = client.open_sftp()

    # Setup base for recursion transfer
    local_path = f'{os.path.realpath(sys.argv[1])}'
    # Find start directory for server
    start_directory = local_path.split("/")[-1]
    
    remote_path = f'{ssh_directory}/{start_directory}'
    
    transfer_files(sftp, local_path, remote_path, _)

    sftp.close()
    client.close()
    
    
    # End padding
    print("")
    print("="*70)
    print("Closing SSH connection...")
    print("="*70)
    print("")
    
else:
    print("No file dropped.")

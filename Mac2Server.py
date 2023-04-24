from paramiko import SSHClient, AutoAddPolicy

import sys
import os



if len(sys.argv) > 0:
    client = SSHClient()

    #LOAD HOST KEYS
    client.load_host_keys('/Users/tareklein/.ssh/known_hosts')
    client.load_system_host_keys()

    #Known_host policy
    client.set_missing_host_key_policy(AutoAddPolicy())

    client.connect('trk.td.org.uit.no', username='tarek', password='tarek.123')

    _, stdout, _ = client.exec_command('pwd')
    ssh_directory = stdout.read().decode("utf8").split("\n")[0]

    _, stdout, _ = client.exec_command('ls')
    output = stdout.read().decode("utf8").split("\n")

    if 'plex' in output:
        print('Plex folder found')
        stdin, stdout, stderr = client.exec_command('ls')
        plex_directory = stdout.read().decode("utf8").split("\n")
        if 'movies' in plex_directory:
            print('Movies folder found')
        else:
            client.exec_command('mkdir -p plex/movies')
        if 'series' in plex_directory:
            print('Series folder found')
        else:
            client.exec_command('mkdir -p plex/series')
            
    else:
        print('Plex folder not found, creating')
        client.exec_command('mkdir -p plex/movies plex/series')

    print("")
    
    # Find directory of local movies
    local_dir = (f'{os.path.dirname(sys.argv[1])}/plex')
    local_dir = os.listdir(local_dir)





    # Open SSH file transfer protocol
    sftp = client.open_sftp()
    
    # # Change the remote working directory to ssh_directory/plex
    # sftp.chdir(ssh_directory+'/plex')
    
    if 'movies' in local_dir:
        # Find directory of local movies
        local_movies_dir = (f'{os.path.dirname(sys.argv[1])}/plex/movies')
        
        # Switch to local movies directory
        os.chdir(local_movies_dir)
        
        # List up local movies
        local_movies = [file for file in os.listdir(local_movies_dir) if not file.startswith('.')]

        
        # Change the remote working directory to ssh_directory/plex/movies
        sftp.chdir(ssh_directory+'/plex/movies')
        
        _, stdout, _ = client.exec_command('ls plex/movies/')
        remote_movies = stdout.read().decode("utf8").split("\n")
        for local_movie in local_movies:
            local_movie_path = os.path.realpath(local_movie)
            
            # Get the size of the file in bytes
            size = (int(os.path.getsize((local_movie_path))/1024)/1024)/1024
            print("="*70)
            if local_movie in remote_movies:
                print(f'||{size:.03f}gb|| ~~~ Movie already here: {local_movie}')
            else:
                remote_path = f'{ssh_directory}/plex/movies/{local_movie}'
                print(f'||{size:.03f}gb|| ~~~ Transfering movie: {local_movie}')
                # sftp.put(local_movie_path, remote_path)
            
    if 'series' in local_dir:
        # Find directory of local movies
        local_series_dir = (f'{os.path.dirname(sys.argv[1])}/plex/series')
        
        # Switch to local movies directory
        os.chdir(local_series_dir)
        
        # List up local movies
        local_series = ([file for file in os.listdir(local_series_dir) if not file.startswith('.')])
        
        
        # Change the remote working directory to ssh_directory/plex/series
        sftp.chdir(ssh_directory+'/plex/series')
        
        _, stdout, _ = client.exec_command('ls plex/series/')
        remote_series = stdout.read().decode("utf8").split("\n")
        for local_serie in local_series:

            # Save remote path
            remote_path = f'\'{ssh_directory}/plex/series/{local_serie}\''
            
            # Change the remote working directory to ssh_directory/plex/series/(series folder name)
            sftp.chdir(f'{ssh_directory}/plex/series/')
            
            # Create series folder
            client.exec_command(f'mkdir {remote_path}')
            
            # Go into file_name directory on local computer
            series_folder = f'{os.path.dirname(sys.argv[1])}/plex/series/{local_serie}'
            os.chdir(series_folder)
            
            # Get a list of all the files in the directory
            episode_list = os.listdir(series_folder)
            
            local_serie_path = os.path.join(local_series_dir, local_serie)
            
            # Get size of series folder in GB
            size = (((os.path.getsize(f'{local_serie_path}')/1024)/1024)/1024)
            
            print("="*70)
            print(f'||{size:.03f}gb|| ~~~ Transerfering Series: {local_serie}')
            
            for episode in episode_list:
                local_path = f'{os.path.dirname(sys.argv[1])}/{local_serie}/{local_serie}'
                remote_path = f'{ssh_directory}/plex/series/{local_serie}/{local_serie}'
                
                # Change the remote working directory to ssh_directory/plex/series/(series name)
                sftp.chdir(f'{ssh_directory}/plex/series/{local_serie}') 
                # Calcualte size of file
                size = (((os.path.getsize(episode)/1024)/1024)/1024)
                print(f'||{size:.03f}gb|| ~~ Transerfering Episode: {episode}') 
                # sftp.put(local_path, remote_path)
        else:
            print("="*70)
            print(f'||{size:.03f}gb|| ~~~ Series already here: {local_serie}')

    print("")
    sftp.close()
    client.close()
    
else:
    print("No file dropped.")


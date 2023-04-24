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
    print("")
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
        local_movies = os.listdir(local_movies_dir)[1:]
        
        # Change the remote working directory to ssh_directory/plex/movies
        sftp.chdir(ssh_directory+'/plex/movies')
        
        _, stdout, _ = client.exec_command('ls plex/movies/')
        remote_movies = stdout.read().decode("utf8").split("\n")
        print(local_movies)
        for local_movie in local_movies:
            local_movie_path = os.path.realpath(local_movie)
            
            # Get the size of the file in bytes
            size = (int(os.path.getsize((local_movie_path))/1024)/1024)/1024
            
            if local_movie in remote_movies:
                print(f'Movie already here: {local_movie} ~~~ ({size:.03f}gb)')
            else:
                remote_path = f'{ssh_directory}/plex/movies/{local_movie}'
                print(f'Transfering movie: {local_movie} ~~~ ({size:.03f}gb)')
                sftp.put(local_movie_path, remote_path)
            
        
    if 'series' in loc:
        file_name = os.path.basename(sys.argv[1]).replace(" ", "_").replace("[", "\[").replace("]", "›")
        
        # Change the remote working directory to ssh_directory/plex/series
        sftp.chdir(ssh_directory+'/plex/series')
        
        _, stdout, _ = client.exec_command('ls plex/series/') 
        series = stdout.read().decode("utf8").split("\n")
        
        if file_name not in series:
            remote_path = f'{ssh_directory}/plex/series/{file_name}'
            
            # Create series folder
            client.exec_command(f'mkdir plex/series/{file_name}')
            
            # Change the remote working directory to ssh_directory/plex/series/(series folder name)
            sftp.chdir(f'{ssh_directory}/plex/series')
            
            # Go into file_name directory on local computer and sftp all the files there
            os.chdir(f'{os.path.dirname(sys.argv[1])}/{file_name}')
            
            # Get a list of all the files in the directory
            files = os.listdir()
            
            for file in files:
                local_path = f'{os.path.dirname(sys.argv[1])}/{file_name.replace("_", " ")}/{file}'
                remote_path = f'{ssh_directory}/plex/series/{file_name}/{file}'
                
                # Change the remote working directory to ssh_directory/plex/series/(series name)
                sftp.chdir(f'{ssh_directory}/plex/series/{file_name}') 
                 
                size = ((os.path.getsize(local_path)/1024)/1024)/1024
                print(f'Transerfering Episode: {file} ~~~ ({size:.03f}gb)') 
                # sftp.put(local_path, remote_path)
        else:
            print(f'Series already here: {file_name} ~~~ ({size:.03f}gb)')


    sftp.close()

    client.close()
    
else:
    print("No file dropped.")


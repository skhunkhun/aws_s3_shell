Sunveer Khunkhun
January 27 2023

<!-- LIMITATIONS -->

    - The S5-S3.conf file uses [default]

    - The absolute path and relative path is determined by a '/' in the front of the path
        For example:
            If you want to use create_folder and absolute path - 'create_folder /<bucket name>/<full path>' 
            If you want to use create_folder and relative path where the chlocn is set to /<bucket name> - 'create_folder <relative path>' without a '/' in the front

        This is the case with every method that uses absolute or relative pathing

    - For s3delete and s3copy, to differentiate between a folder and a file, there must be a '/' at the end to signify a folder.
        For example:
            Folder - 's3delete /<bucket name>/<folder>/'
            File - 's3delete /<bucket name>/<path to file>

<!-- HOW TO RUN SHELL: -->

    Use 'tar -xvf Assignment1.tar' to unzip the tar file
    Install all the requirements in the requirements.txt file (used only the packages that were given in the sample code)
    Make sure your 'S3-S5.conf file' is in the directory
    It should look like this:

    [default]
    aws_access_key_id = xxxxxxxxxxxxxxxx
    aws_secret_access_key = xxxxxxxxxxxxxxxxx
    
    Run 'python3 s3Main.py' and the shell should start immediately if the right packages are installed

<!-- NORMAL BEHAVIOUR: -->

    Local Shell Commands:
        -Commands like 'ls' and 'cd' should work as intended 

    LOCS3CP:
        - copies a local file to a Cloud (S3) location given 'locs3cp <full or relative pathname of local file> /<bucket name>/<full pathname of S3object>'
        - will give success message if successful or give the correct error message depeding on the error

    S3LOCCP:
        - copies a Cloud object to a local file system location given 's3loccp /<bucket name>/<full pathname of S3 file> <full/relative pathname of the local file>'
        - will give success message if successful or give the correct error message depeding on the error

    CREATE_BUCKET:
        - creates a bucket in the user's S3 space following naming conventions for S3 buckets given 'create_bucket /<bucket name>'
        - will give success message if successful or give the correct error message depeding on the error

    CREATE_FOLDER:
        - creates a directory or folder in an existing S3 bucket given 'create_folder /<bucket name>/<full pathname for the folder>'
        - will give success message if successful or give the correct error message depeding on the error

    CHLOCN:
        -changes the current working directory in your S3 space given 'chlocn /<bucket name>/<full pathname of directory>'

        -If bucket or folder does not exists, it will print an error message
        
        * CHLOCN follows linux file system behaviour

    CWLOCN:
        - displays the current working location/directory, i.e. your location in S3 space. If you
        are not yet located in a bucket, then the response will be "/". This would be the
        response if you execute this command after starting the shell.
        - displays the path on Success

    LIST:
        - like the Linix ls command, list will show either a short or long form of the contents of
        your current working directory or a specified S3 location (including "/"). The argument
        to get the long version is "-l" - same as the Unix ls command. The long form will
        mimic the Linix long form (type, size, permissions) as much as possible.

        * when displaying '/' or '~', all of the users buckets will be dsiplayed

        - will display the locations of the path given on success or and error message on failure

    S3COPY:
        - delete an object (directories included but only if they are empty). This command will
        not delete buckets given 's3delete <full or indirect pathname of object>'.
    
        - will give success message if successful or error message if not

    S3DELETE:
        - delete an object (directories included but only if they are empty). This command will
        not delete buckets.

        - will give success message if successful or give the correct error message depending on the error

    DELETE_BUCKET:
        - delete a bucket if it is empty. You cannot delete the bucket that you are currently in.

        - will give success message if successful or give the correct error message depending on the error

import configparser
import os 
import sys 
import pathlib
import boto3

#function to check if a folder exists in the S3 space (Mostly for chlocn)
def folder_exists(location, s3):
    
    #parse location data to get bucket name and object path
    aws_name = location.split('/')
    bucket_name = aws_name[1]
    object_name = ""

    for i in range(2, len(aws_name)):
        object_name += aws_name[i]  + '/'
    object_name = object_name[:-1]

    #check if the bucket or object exists before user can change to it
    try:
        resp = s3.list_objects(Bucket=bucket_name, Prefix=object_name, Delimiter='/', MaxKeys=2)
    except:
        return False

    #Make sure the object name matches by case and not prefix only
    if 'CommonPrefixes' in resp:
        if len(object_name) == 0 and resp['Name'] == bucket_name:
            return True

        object_name = object_name + '/'
        s3_object_name = resp['CommonPrefixes'][0]['Prefix']
        if object_name != s3_object_name:
            return False

    if len(object_name) == 0 and resp['Name'] == bucket_name:
        return True

    return 'CommonPrefixes' in resp

# function to allow a user to change their current directory in their S3 space
def chlocn(location, data_parse, s3):

    original_location = location
    #check the correct number of arguments
    if len(data_parse) != 2:
        print("Invalid arguments: chlocn /<bucket name>/<full pathname of directory>")
        return original_location
    
    try:
        # allows user to go to parent directory
        if '..' in data_parse[1]:

            if len(location) == 1:
                print("Cannot go into parent directory")
                return original_location

            dots = data_parse[1].split('/')
            path = location.split('/')

            location = ""
            for i in range(1, len(path) - len(dots)):
                location += "/" + path[i]

        elif data_parse[1] == '/' or data_parse[1] == '~':
            location = data_parse[1]
            return location

        else:
            if data_parse[1][0] != '/':
                location = location + "/" + data_parse[1]
            else:
                location = data_parse[1]

        if location == '/' or location == '~':
            return 

        if len(location) == 0:
            location = '/'
            return location

        if folder_exists(location, s3) == False:
            print("Bucket or Directory does not exist")
            return original_location

    except Exception as e:
        print(e)
        return original_location

    return location

# function to copy a local file to the cloud location
def copy_local_file(location, data_parse, s3):

    if len(data_parse) != 3:
        return "Invalid Arguments: locs3cp <full or relative pathname of local file> /<bucket name>/<full pathname of S3 object>"

    try:
        #check if user is using a relative path or absolute path
        if len(location) == 1 or data_parse[2][0] == '/':
            location = data_parse[2]
        
        else:
            location = location + "/" + data_parse[2]

        aws_name = location.split("/")
        bucket_name = aws_name[1]
        object_name = ""
        isAbsolute = os.path.isabs(data_parse[1])
        full_path = ""

        #get the local file path
        if isAbsolute == True:
            full_path = data_parse[1]
        
        else:
            a_path = os.path.dirname(__file__)
            full_path = os.path.join(a_path, data_parse[1])

        for i in range(2, len(aws_name)):
            object_name += aws_name[i]  + '/'

        object_name = object_name[:-1]
    
        s3.upload_file(full_path, bucket_name, object_name)
    except Exception as e:
        return e
    
    return f"Successfully copied {full_path} to {location}"

# function to copy a cloud file to local
def copy_cloud_file(location, data_parse, s3):

    if len(data_parse) != 3:
        return "Invalid Arguments: s3loccp /<bucket name>/<full pathname of S3 file> <full/relative pathname of the local file>"

    try:
        if len(location) == 1 or data_parse[1][0] == '/':
            location = data_parse[1]
        
        else:
            location = location + "/" + data_parse[1]

        filename = data_parse[2]
        aws_name = location.split('/')
        bucket_name = aws_name[1]
        object_name = ""

        for i in range(2, len(aws_name)):
            object_name += aws_name[i]  + '/'

        object_name = object_name[:-1]

    
        s3.download_file(bucket_name, object_name, filename)
    except Exception as e:
        return e

    return f"Successfully copied {location} to {filename}"

# function to create a bucket in the S3 space
def create_bucket(data_parse, s3):

    if len(data_parse) != 2:
        return "Invalid Arguments: create_bucket /<bucket name>"
    try:
        bname = data_parse[1][1:]

        s3.create_bucket(Bucket=bname, CreateBucketConfiguration={'LocationConstraint': 'ca-central-1'})
    except Exception as e:
        return e

    return f"Successfully created bucket {bname}"

# function to create a folder in the S3 space
def create_folder(location, data_parse, s3):

    if len(data_parse) != 2:
        return "Invalid Arguments: create_folder /<bucket name>/<full pathname for the folder>"

    try:
        if len(location) == 1 or data_parse[1][0] == '/':
            location = data_parse[1]
        else:
            location = location + "/" + data_parse[1]

        aws_name = location.split('/')
        bucket_name = aws_name[1]
        object_name = ""

        for i in range(2, len(aws_name)):
            object_name += aws_name[i]  + '/'

        s3.put_object(Bucket=bucket_name, Body="", Key=object_name)
    except Exception as e:
        return e

    return f"Successfully created {location}"

#function to list objects and buckets in S3 space
def list_object(location, data_parse, s3, s3_res):

    if len(data_parse) > 3 or len(data_parse) < 1:
        return "Invalid Arguments: list or list /<bucket name> or list /<bucket name>/<full pathname for directory or file>"
        
    try:
        if len(data_parse) == 1: #check if user types only 'list' and either lists the root or the path user is in
            if len(location) == 1:
                print(f"All buckets in {location}")
                buckets = s3.list_buckets()
                for bucket in buckets['Buckets']:
                    print(bucket["Name"])

            else:
                aws_name = location.split('/')
                bucket_name = aws_name[1]
                object_name = ""

                for i in range(2, len(aws_name)):
                    object_name += aws_name[i]  + '/'

                bucket = s3_res.Bucket(bucket_name)
                for object in bucket.objects.filter(Prefix=object_name):
                    print(object.key)

        elif len(data_parse) == 2 and data_parse[1] == '-l': # checks if user types 'list -l' and either lists the root or path user is in with extra information
            if len(location) == 1:
                print("All buckets in /")
                buckets = s3.list_buckets()
                for bucket in buckets['Buckets']:
                    print(f"Creation Date: {(bucket['CreationDate'])}\tName: {(bucket['Name'])} ")
            else:
                aws_name = location.split('/')
                bucket_name = aws_name[1]
                object_name = ""

                for i in range(2, len(aws_name)):
                    object_name += aws_name[i]  + '/'

                bucket = s3_res.Bucket(bucket_name)
                for object in bucket.objects.filter(Prefix=object_name):
                    print(f"LAST MODIFIED: {object.last_modified}\tSIZE: {object.size}\tSTORAGE CLASS: {object.storage_class}\tKEY: {object.key}")
        
        elif len(data_parse) == 2 and data_parse[1] != '-l': #checks if user types 'list <path>' and prints out the correct items in directory
            if data_parse[1] == '/':
                print("All buckets in /")
                buckets = s3.list_buckets()
                for bucket in buckets['Buckets']:
                    print(bucket["Name"])
            else:
                if data_parse[1][0] == '/':
                    location = data_parse[1]
                else:
                    location = location + "/" + data_parse[1]

                aws_name = location.split('/')
                bucket_name = aws_name[1]
                object_name = ""

                for i in range(2, len(aws_name)):
                    object_name += aws_name[i]  + '/'

                if folder_exists(location, s3) == False:
                    print("Cannot list contents of this S3 location")
                    return 1

                bucket = s3_res.Bucket(bucket_name)
                for object in bucket.objects.filter(Prefix=object_name):
                    print(object.key)

        elif len(data_parse) == 3: #checks if user types 'list -l <path>' and prints out directory information with extra information

            if data_parse[2][0] == '/':
                location = data_parse[2]
            else:
                location = location + "/" + data_parse[2]

            aws_name = location.split('/')
            bucket_name = aws_name[1]
            object_name = ""

            for i in range(2, len(aws_name)):
                object_name += aws_name[i]  + '/'

            if folder_exists(location, s3) == False:
                print("Cannot list contents of this S3 location")
                return 1

            bucket = s3_res.Bucket(bucket_name)
            for object in bucket.objects.filter(Prefix=object_name):
                print(f"LAST MODIFIED: {object.last_modified}\tSIZE: {object.size}\tSTORAGE CLASS: {object.storage_class}\tKEY: {object.key}")
        else:
            return "Cannot list contents of this S3 location"

    except Exception as e:
        return e

#function to copy an object from one S3 space to another
def copy_object(location, data_parse, s3_res):

    if len(data_parse) != 3:
        return "Invalid Arguments: S3copy <from S3 location of object> <to S3 location>"

    try:
        #parse both S3 paths
        from_s3 = ""
        to_s3 = ""

        if data_parse[1][0] == '/':
            from_s3 = data_parse[1]
        else:
            from_s3 = location + "/" + data_parse[1]

        if data_parse[2][0] == '/':
            to_s3 = data_parse[2]
        else:
            to_s3 = location + "/" + data_parse[2]

        from_name = from_s3.split('/')
        from_bucket_name = from_name[1]
        from_object_name = ""
        for i in range(2, len(from_name)):
            from_object_name += from_name[i]  + '/'
        from_object_name = from_object_name[:-1]

        to_name = to_s3.split('/')
        to_bucket_name = to_name[1]
        to_object_name = ""
        for i in range(2, len(to_name)):
            to_object_name += to_name[i]  + '/'
        to_object_name = to_object_name[:-1]

        copy_source = {
            'Bucket' : from_bucket_name,
            'Key' : from_object_name
        }

        to_bucket = s3_res.Bucket(to_bucket_name)
        to_bucket.copy(copy_source, to_object_name)

    except Exception as e:
        return e

    return f"Successfully copied {from_s3} to {to_s3}"

# function to delete an object from an S3 location
def delete_object(location, data_parse, s3, s3_res):
    
    if len(data_parse) != 2:
        return "Invalid Arguments: s3delete <full or indirect pathname of object>"

    try:
        if len(location) == 1 or data_parse[1][0] == '/':
            location = data_parse[1]
        else:
            location = location + "/" + data_parse[1]

        aws_name = location.split('/')
        bucket_name = aws_name[1]
        object_name = ""

        for i in range(2, len(aws_name)):
            object_name += '/' + aws_name[i] 
        object_name = object_name[1:]

        bucket = s3_res.Bucket(bucket_name)
        count = bucket.objects.filter(Prefix=object_name)
        count1 = len(list(count))

        if count1 == 0:
            return "No object found with the name {" + object_name + "} in bucket {" + bucket_name + "}"
        elif count1 == 1:
            obj_name = ""
            for obj in count:
                obj_name = obj.key

            if obj_name != object_name:
                return "No object found with the name {" + object_name + "} in bucket {" + bucket_name + "}"
        elif count1 > 1:
            return "Cannot delete {" + object_name + "} in bucket {" + bucket_name + "} as it is not empty"

        s3.delete_object(Bucket=bucket_name, Key=object_name)
    except Exception as e:
        return e

    return "Successfully deleted object {" + object_name + "} from {" + bucket_name + "}"

# function to delete a bucket from the S3 location
def delete_bucket(location, data_parse, s3):

    if len(data_parse) != 2:
        return "Invalid Arguments: delete_bucket <bucket name>"

    try:
        aws_name = location.split('/')
        bucket_name = aws_name[1]

        if bucket_name == data_parse[1][1:]:
            return "Error: Cannot delete bucket that you are currently in"

        bucket_name = data_parse[1][1:]

        s3.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        return e

    return f"Successfully deleted bucket {bucket_name}"
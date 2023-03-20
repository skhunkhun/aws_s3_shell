from s3Functions import *

print( "Welcome to the AWS S3 Storage Shell (S5)" )

try:

    #  Find AWS access key id and secret access key information from configuration file

    config = configparser.ConfigParser()
    config.read("S5-S3.conf")
    aws_access_key_id = config['default']['aws_access_key_id']
    aws_secret_access_key = config['default']['aws_secret_access_key']

#  Establish an AWS session

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

#  Set up client and resources

    s3 = session.client('s3')
    s3_res = session.resource('s3')

    # make sure key is valid
    s3.list_buckets()
    print("You are now connected to your S3 storage\n")


except Exception as e:
    print ( "You could not be connected to your S3 storage" )
    print ( "Please review procedures for authenticating your account on AWS S3 and make sure your S5-S3.conf file is correct" )
    exit()

location = "/"

while True:
    data = input("S5> ")
    data_parse = data.split()

    if(len(data_parse) > 0):

        if data_parse[0].lower() == 'exit' or data_parse[0].lower() == 'quit':
            break

        elif data_parse[0] == 'chlocn':
            location = chlocn(location, data_parse, s3)

        elif data_parse[0] == 'locs3cp':
            ret = copy_local_file(location, data_parse, s3)
            print(ret)

        elif data_parse[0] == 's3loccp':
            ret = copy_cloud_file(location, data_parse, s3)
            print(ret)

        elif data_parse[0] == 'create_bucket':
            ret = create_bucket(data_parse, s3)
            print(ret)

        elif data_parse[0] == 'create_folder':
            ret = create_folder(location, data_parse, s3)
            print(ret)

        elif data_parse[0] == 'cwlocn':
            if len(data_parse) != 1:
                print("Invalid Arguments: cwlocn")
            else:
                print(location)

        elif data_parse[0] == 'list':
            list_object(location, data_parse, s3, s3_res)

        elif data_parse[0] == 's3copy':
            ret = copy_object(location, data_parse, s3_res)
            print(ret)

        elif data_parse[0] == 's3delete':
            ret = delete_object(location, data_parse, s3, s3_res)
            print(ret)

        elif data_parse[0] == 'delete_bucket':
            ret = delete_bucket(location, data_parse, s3)
            print(ret)

        else:
            if data_parse[0] == 'cd':
                os.chdir(data_parse[1])
            else:
                os.system(data)
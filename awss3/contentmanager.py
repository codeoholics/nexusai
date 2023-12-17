from awss3.awsconfig import getBotoS3Client
from projects.document_reader import log
from shared import config, logger

log = logger.get_logger(__name__)
client = None

def uploadFile(file, object_name):
    s3client = getBotoS3Client()
    bucket = config.get('S3_BUCKET')
    # If S3 object_name was not specified, use file_name

    log.info("Uploading file: %s", object_name)
    log.info("bucket : %s", bucket)
    log.info(file)
    # Upload the file
    try:
        response = s3client.upload_file(file, bucket, object_name)

        url = f"https://{bucket}.s3.amazonaws.com/{object_name}"
        log.info("Upload successful url : %s",url)
        return url
    except Exception as e:
        log.error("Upload failed: %s", e)
        return None

def delete_all_objects_in_bucket():
    s3_client = getBotoS3Client()
    bucket = config.get('S3_BUCKET')

    log.info("Deleting all objects in bucket: %s", bucket)

    try:
        # List all objects in the bucket
        object_list = s3_client.list_objects_v2(Bucket=bucket)

        # Check if the bucket is empty
        if 'Contents' not in object_list:
            log.info("The bucket is already empty.")
            return True

        # Delete each object in the bucket
        for obj in object_list['Contents']:
            s3_client.delete_object(Bucket=bucket, Key=obj['Key'])
            log.info("Deleted object: %s", obj['Key'])

        log.info("All objects deleted successfully.")
        return True


    except Exception as e:
        log.error("Error deleting objects: %s", e)
        return False

def downloadfile(object_name):
    s3client = getBotoS3Client()
    bucket = config.get('S3_BUCKET')
    # If S3 object_name was not specified, use file_name

    log.info("Downloading file: %s", object_name)
    log.info("bucket : %s", bucket)
    # Download the file
    try:
        response = s3client.download_file(bucket, object_name, object_name)
        print("Download successful:", response)
        return True
    except Exception as e:
        log.error("Download failed: %s", e)
        return None



import boto3

from shared import config
from shared import logger
log = logger.get_logger(__name__)
client = None


def getBotoS3Client():
    global client
    if client is not None:
        return client
    else:
        try:
            log.info("Creating boto3 client")
            log.info("AWS_ACCESS_KEY_ID: %s", config.get('AWS_ACCESS_KEY_ID'))
            log.info("region_name: %s", config.get('AWS_DEFAULT_REGION'))
            client = boto3.client('s3',
                              aws_access_key_id=config.get('AWS_ACCESS_KEY_ID'),
                              aws_secret_access_key=config.get('AWS_SECRET_ACCESS_KEY'),
                                region_name=config.get('AWS_DEFAULT_REGION')

                                  )
        except Exception as e:
            print("Error in getBotoS3Client:", e)
        return client





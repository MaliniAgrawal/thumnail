import boto3
from botocore.exceptions import ClientError
import os
from PIL import Image
import urllib.parse

s3 = boto3.client('s3')

SOURCE_BUCKET = "1234-image"
DESTINATION_BUCKET = "1234-thumnailimage"

def create_thumbnail(image_path, thumb_path, size=(128, 128)):
    with Image.open(image_path) as image:
        image.thumbnail(size)
        image.save(thumb_path)

def lambda_handler(event, context):
    print("Received event:", event)  # Log the entire event
    try:
        # Extracting bucket name and object key from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    except KeyError as e:
        print(f"KeyError: {e}")
        return {
            'statusCode': 400,
            'body': f"KeyError: {e}. Event: {event}"
        }

    # Download the image from S3
    download_path = f'/tmp/{os.path.basename(object_key)}'
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        with open(download_path, 'wb') as f:
            f.write(response['Body'].read())
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print(f"Access denied. Check IAM permissions for bucket: {bucket_name}")
        elif error_code == 'InvalidRequest':
            print(f"Invalid request. This might be due to the object key being too long: {object_key}")
        else:
            print(f"Unexpected error: {e}")
        raise

    # Create a thumbnail
    thumb_path = f'/tmp/thumb-{os.path.basename(object_key)}'
    create_thumbnail(download_path, thumb_path)

    # Upload the thumbnail back to S3
    thumb_key = f'thumb-{os.path.basename(object_key)}'
    s3.upload_file(thumb_path, DESTINATION_BUCKET, thumb_key)

    return {
        'statusCode': 200,
        'body': f"Thumbnail created and uploaded to {DESTINATION_BUCKET}/{thumb_key}"
    }
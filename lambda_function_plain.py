import boto3
import os
from PIL import Image
import urllib.parse


"""This lambda function is pure logic it does not check permission or access denied issues. if you wish to use this file
as it is than under runtime setting go edit and instead of using "lambda_function.lambda_handler" this use 
"lambda_function_plain.lambda_handler just to make sure under this section lambda_function is your lambda .py file name and
lambda_handler is you def lambda_habdler function that actually return your statuscode and body section for function return."""

s3 = boto3.client('s3')

SOURCE_BUCKET = "1234-image"
DESTINATION_BUCKET = "1234-thumnailimage"

def create_thumbnail(image_path, thumb_path, size=(128, 128)):
    with Image.open(image_path) as image:
        image.thumbnail(size)
        image.save(thumb_path)

def lambda_handler(event, context):
    # Extract bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])

    # Download the image from S3
    download_path = f'/tmp/{os.path.basename(object_key)}'
    s3.download_file(bucket_name, object_key, download_path)

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
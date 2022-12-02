import json
import boto3
import cv2
import numpy as np
import os

s3_client = boto3.client("s3")
S3_BUCKET = 'free-parking-spots'
def lambda_handler(event, context):

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key  = event['Records'][0]['s3']['object']['key']

    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=key)
    image = response['Body'].read()
    image_cv2 = cv2.imdecode(np.asarray(bytearray(image)), cv2.IMREAD_COLOR)

    gray_image = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
    key_path, key_file = os.path.split(key)
    os.chdir("/tmp")
    cv2.imwrite(key_file, gray_image)
    key_picture = os.getcwd()
    key_picture = key_picture+ "/" + key_file
    key2 = "grayscale-images/" + key_file

    
    s3_client.upload_file(key_picture, S3_BUCKET, key2)


    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


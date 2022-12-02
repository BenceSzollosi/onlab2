import json
import boto3
import cv2
import numpy as np
import os
from boto3.dynamodb.conditions import Key

s3_client = boto3.client("s3")
S3_BUCKET = 'cars-in-parking-spots'

#REGION = os.environ.get('REGION', "us-east-1")
#dynamodb = boto3.client('dynamodb', REGION)
#dynamodb_table = "ROIcars"

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
#dynamodb_table = dynamodb.Table('ROIcars')
def lambda_handler(event, context):
    bucket_name = "free-parking-spots"
    for record in event['Records']:
        key = record['dynamodb']['NewImage']['picture']['S']
        #print("key: ", key)
        key_id = record['dynamodb']['NewImage']['id']['S']
        #print("key_id: ", key_id)
        x1 = int(record['dynamodb']['NewImage']['x1']['N'])
        #print("x1: ", x1)
        x2 = int(record['dynamodb']['NewImage']['x2']['N'])
        y1 = int(record['dynamodb']['NewImage']['y1']['N'])
        y2 = int(record['dynamodb']['NewImage']['y2']['N'])
    #key = event['picture']
        key_path, key_file = os.path.split(key)
        key2 = "grayscale-images/" + key_file
        response = s3_client.get_object(Bucket=bucket_name, Key=key2)

        image = response['Body'].read()
        image_cv2 = cv2.imdecode(np.asarray(bytearray(image)), cv2.IMREAD_COLOR)
    
    #dynamo_response = dynamodb_table.query(KeyConditionExpression=Key('picture').eq(key_file))
    #print("The query returned the following items:")
    #for item in dynamo_response['Items']:
    #    print(json.dumps(item, indent=4, sort_keys=True))
        
        crop_img = image_cv2[y1:y2, x1:x2]
        os.chdir("/tmp")
        cv2.imwrite(key_id, crop_img)
        key_picture = os.getcwd()
        key_picture = key_picture + "/" + key_id
        key_id2 = "original/" + key_id
        s3_client.upload_file(key_picture, S3_BUCKET, key_id2)

    #print(result)


        
    return {
        'statusCode': 200,
        'body': json.dumps('')
    }


import json
import boto3
import cv2
import numpy as np
import os

s3_client = boto3.client("s3")
#S3_BUCKET = 'free-parking-spots2'
S3_BUCKET = os.environ['S3_BUCKET_NAME_PARKING_TRANSFORMATION']
iot_client = boto3.client('iot-data', region_name='eu-central-1')

lambda_location = os.environ['AWS_EDGE_CLOUD']
def lambda_handler(event, context):

    if (lambda_location == "CLOUD"):
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
        key_picture = key_picture + "/" + key_file
        key2 = "grayscale-images/" + key_file
    
        s3_client.upload_file(key_picture, S3_BUCKET, key2)
    if (lambda_location == "EDGE"):
        key = event['key']
        print("key: ", key)
        # read Grayscale image
        image_cv2 = cv2.imread(key, 0)

        #gray_image = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
        #key_path, key_file = os.path.split(key)
        #os.chdir("/greengrass/v2/grayscale-images-ggv2/")
        #key2 = "/greengrass/v2/grayscale-images-ggv2/" + key_file
        
        #isWritten = cv2.imwrite(key2, image_cv2)
        #if isWritten:
        #    print('Image is successfully saved as file.')
        #else:
        #    print('Image is not saved!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        #key_picture = os.getcwd()
        #key_picture = key_picture + "/" + key_file
        
        
        key_path, key_file = os.path.split(key)
        os.chdir("/home/ggc_user/grayscale-images-ggv2")
        cv2.imwrite(key_file, image_cv2)
        key_picture = os.getcwd()
        key_picture = key_picture + "/" + key_file
        
        
        
        output_location = {
            "key":  key_picture
            #"key":  key2
        }
        print("output_location: ", output_location)
        # Upload Grayscale pic for Crop_car input.
        s3_key = "grayscale-images-ggv2/" + key_file
        s3_client.upload_file(key_picture, S3_BUCKET, s3_key)
        
        print(output_location)
        mqtt_publish_topic = os.environ['MQTT_PUBLISH_TOPIC_PARKING_TRANSFORMATION']
        response = iot_client.publish(
            topic= mqtt_publish_topic, #'greengrass/v2/cardetection',
            qos=0,
            payload=json.dumps(output_location)
            )
        print(response)
 
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }




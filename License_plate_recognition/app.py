import json
import boto3
import cv2
import os
import pytesseract
import numpy as np

s3_client = boto3.client("s3")
S3_BUCKET = 'cars-in-parking-spots'

REGION = os.environ.get('REGION', "us-east-1")
dynamodb = boto3.client('dynamodb', REGION)
dynamodb_table = "ROIcars"

def lambda_handler(event, context):

	bucket_name = event['Records'][0]['s3']['bucket']['name']
	key  = event['Records'][0]['s3']['object']['key']

	# image read
	response = s3_client.get_object(
		Bucket=bucket_name,
		Key=key)
	image = response['Body'].read()
	image_cv2 = cv2.imdecode(np.asarray(bytearray(image)), cv2.IMREAD_COLOR)
	
	#resize_image = cv2.resize(image_cv2, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)
	grayscale_resize_test_license_plate = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
	gaussian_blur_image = cv2.GaussianBlur(grayscale_resize_test_license_plate, (5, 5), 0)
	result_text = pytesseract.image_to_string(gaussian_blur_image)
	filter_result_text = "".join(result_text.split()).replace(":", "").replace("-", "")

	print("license plate: ",filter_result_text)
	print("license plate only grayscale filter: ", pytesseract.image_to_string(grayscale_resize_test_license_plate))
	
	##########################################
	#key_path, key_file = os.path.split(key)
	#os.chdir("/tmp")
	#cv2.imwrite(key_file, sharpen_img)
	#key_picture = os.getcwd()
	#key_picture = key_picture+ "/" + key_file
	#key2 = "/" + key_file

	#s3_client.upload_file(key_picture, S3_BUCKET, key2)
	##########################################
	
	

	return {
		'statusCode': 200,
		'body': json.dumps('')
	}
      

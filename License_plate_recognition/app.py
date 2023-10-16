import json
import boto3
import cv2
import os
import pytesseract
import numpy as np

s3_client = boto3.client("s3")
S3_BUCKET = os.environ['S3_BUCKET_NAME_PARKING_LICENSE'] #'cars-in-parking-spots2'

REGION = os.environ.get('REGION', "eu-central-1")
dynamodb = boto3.client('dynamodb', REGION)
dynamodb_table = os.environ['DYNAMODB_TABLE_NAME_PARKING_LICENSE'] #"ROIcars"

# A Tesseract adatfájl elérési útvonala
tessdata_path = '/usr/share/tesseract/tessdata/'

# Beállítjuk a TESSDATA_PREFIX környezeti változót
os.environ['TESSDATA_PREFIX'] = tessdata_path

def lambda_handler(event, context):

	bucket_name = event['Records'][0]['s3']['bucket']['name']
	key  = event['Records'][0]['s3']['object']['key']

	response = s3_client.get_object(
		Bucket=bucket_name,
		Key=key)
	image = response['Body'].read()
	image_cv2 = cv2.imdecode(np.asarray(bytearray(image)), cv2.IMREAD_COLOR)
	
	# Angol és thai nyelv támogatása a pytesseract-hez
	#custom_config = r'--oem 3 --psm 6 -l eng+tha'

	#resize_image = cv2.resize(image_cv2, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)
	#grayscale_resize_test_license_plate = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
	#gaussian_blur_image = cv2.GaussianBlur(grayscale_resize_test_license_plate, (5, 5), 0)
	#result_text = pytesseract.image_to_string(gaussian_blur_image)
	#filter_result_text = "".join(result_text.split()).replace(":", "").replace("-", "")
	
	text = pytesseract.image_to_string(image_cv2, lang ='tha+eng')
	
	#print("license plate: ",filter_result_text)
	print("license plate: ", text)
	
	# Rendszám szűrése
	if (len(text) < 5 or len(text) > 15):
		text = "unknown"
	
	# Frissítendő adat inicializálása
	update_expression = "SET #new_license = :license_value"  # Új mező hozzáadása
	expression_attribute_names = {'#new_license': 'license'}
	expression_attribute_values = {':license_value': {'S': text}}  # Új mező értéke

	key_path, key_file = os.path.split(key)

	# Frissítési kérés végrehajtása
	response = dynamodb.update_item(
		TableName=dynamodb_table,
		Key={'id': {'S': key_file}},
		UpdateExpression=update_expression,
		ExpressionAttributeNames=expression_attribute_names,
		ExpressionAttributeValues=expression_attribute_values
	)
	
	return {
		'statusCode': 200,
		'body': json.dumps('')
	}
      

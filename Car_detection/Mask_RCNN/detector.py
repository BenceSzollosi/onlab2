import base64
import io
from shapely.geometry import Polygon as shapely_poly
from shapely.geometry import box
import argparse
import pickle
from pathlib import Path
from mrcnn.model import MaskRCNN
import mrcnn.utils
import mrcnn.config
import cv2
import numpy as np
import os
import json
import boto3



class Config(mrcnn.config.Config):
    NAME = "model_config"
    IMAGES_PER_GPU = 1
    GPU_COUNT = 1
    NUM_CLASSES = 81


config = Config()
config.display()

ROOT_DIR = os.getcwd()
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")

print(COCO_MODEL_PATH)
if not os.path.exists(COCO_MODEL_PATH):
    mrcnn.utils.download_trained_weights(COCO_MODEL_PATH)

def get_cars(boxes, class_ids):
    cars = []
    for i, box in enumerate(boxes):
        if class_ids[i] in [3, 8, 6]:
            cars.append(box)
    return np.array(cars)


def compute_overlaps(parked_car_boxes, car_boxes):
    new_car_boxes = []
    for box in car_boxes:
        y1 = box[0]
        x1 = box[1]
        y2 = box[2]
        x2 = box[3]

        p1 = (x1, y1)
        p2 = (x2, y1)
        p3 = (x2, y2)
        p4 = (x1, y2)
        new_car_boxes.append([p1, p2, p3, p4])

    overlaps = np.zeros((len(parked_car_boxes), len(new_car_boxes)))
    for i in range(len(parked_car_boxes)):
        for j in range(car_boxes.shape[0]):
            pol1_xy = parked_car_boxes[i]
            pol2_xy = new_car_boxes[j]
            polygon1_shape = shapely_poly(pol1_xy)
            polygon2_shape = shapely_poly(pol2_xy)

            polygon_intersection = polygon1_shape.intersection(
                polygon2_shape).area
            polygon_union = polygon1_shape.union(polygon2_shape).area
            IOU = polygon_intersection / polygon_union
            overlaps[i][j] = IOU
    return overlaps


REGION = os.environ.get('REGION', "us-east-1")
dynamodb = boto3.client('dynamodb', REGION)
dynamodb_table = "ROIcars"

s3_client = boto3.client("s3")
DEST_S3_BUCKET = 'free-parking-spots'

def lambda_handler(event, context):

    model = MaskRCNN(mode="inference", model_dir=MODEL_DIR, config=Config())
    model.load_weights(COCO_MODEL_PATH, by_name=True)

    regions = "/var/task/regions.p"
    with open(regions, 'rb') as f:
        parked_car_boxes = pickle.load(f)
    
    #VIDEO_SOURCE = args.video_path
    #VIDEO_SOURCE = "parking_cars.png"
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key  = event['Records'][0]['s3']['object']['key']

    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=key)
    image = response['Body'].read()
    image_cv2 = cv2.imdecode(np.asarray(bytearray(image)), cv2.IMREAD_COLOR)
    alpha = 0.6

    im = image_cv2
    video_size = (im.shape[0], im.shape[1])
#    h, w, _ = im.shape
    rgb_image = im[:, :, ::-1]
    results = model.detect([rgb_image], verbose=0)
    overlay = im.copy()

    cars = get_cars(results[0]['rois'], results[0]['class_ids'])
    overlaps = compute_overlaps(parked_car_boxes, cars)

    for parking_area, overlap_areas in zip(parked_car_boxes, overlaps):
        max_IoU_overlap = np.max(overlap_areas)
        if max_IoU_overlap < 0.15:
            cv2.fillPoly(overlay, [np.array(parking_area)], (71, 27, 92))
            free_space = True
    cv2.addWeighted(overlay, alpha, im, 1 - alpha, 0, im)
    
    key_path, key_file = os.path.split(key)
    os.chdir("/tmp")
    cv2.imwrite(key_file, im)
    key_picture = os.getcwd()
    key_picture = key_picture+ "/" + key_file
    key2 = key_file
    
    s3_client.upload_file(key_picture, DEST_S3_BUCKET, key2)
    
    for index, car_box in enumerate(cars):
        y1 = car_box[0]
        x1 = car_box[1]
        y2 = car_box[2]
        x2 = car_box[3]
        #crop_img = rgb_image[y1:y2, x1:x2]
    # kell: melyik kép
    # 4 koordináta, ami a cars-ban van
        key_dynamo = str(index) + key_file
        dynamodb.put_item(TableName=dynamodb_table, Item={
        'id': {'S': key_dynamo},
        'picture': {'S': key_file},
        'y1': {'N': str(y1)},
        'x1': {'N': str(x1)},
        'y2': {'N': str(y2)},
        'x2': {'N': str(x2)}
        })

    return {
    'statusCode': 200,
        'body': json.dumps("OK")
#    'body': json.dumps("There is a free parking space" if free_space else "There is no free parking space")
    }

import cv2
import os
import pytesseract
import numpy as np


path_to_license_plate = "/home/ubuntu/onlab2/license-plate.png"
image_cv2 = cv2.imread(path_to_license_plate)

#resize_image = cv2.resize(image_cv2, None, fx = 2, fy = 2, interpolation = cv2.INTER_CUBIC)
grayscale_image = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
gaussian_blur_image = cv2.GaussianBlur(grayscale_image, (5, 5), 0)
result_text = pytesseract.image_to_string(gaussian_blur_image, lang ='eng+tha')
print(result_text)
filter_result_text = "".join(result_text.split()).replace(":", "").replace("-", "")

print("license plate: ",filter_result_text)
thai_result = pytesseract.image_to_string(image_cv2, lang='eng+tha')
print(thai_result)
thai_result = "".join(thai_result.split()).replace(":", "").replace("-", "")
print(thai_result)

FROM public.ecr.aws/lambda/python:3.7

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN python3.7 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY regions.p ${LAMBDA_TASK_ROOT}
COPY Mask_RCNN/* ${LAMBDA_TASK_ROOT}/
COPY parking_cars.png ${LAMBDA_TASK_ROOT}

#CMD ["python3", "detector.py", "parking_cars.png", "regions.p"]
CMD ["detector.lambda_handler"]


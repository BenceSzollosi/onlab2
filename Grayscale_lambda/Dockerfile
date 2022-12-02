FROM public.ecr.aws/lambda/python:3.7

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN python3.7 -m pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]



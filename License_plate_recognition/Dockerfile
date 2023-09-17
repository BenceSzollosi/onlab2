FROM public.ecr.aws/lambda/python:3.8

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y update
RUN yum -y install tesseract

COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.lambda_handler"]



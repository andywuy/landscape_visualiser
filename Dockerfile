FROM python:3
# avoid to write .pyc files 
ENV PYTHONDONTWRITEBYTECODE=1
# Setting PYTHONUNBUFFERED to a non empty value ensures that the python output
# is sent straight to terminal (e.g. your container log) 
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt
RUN pip install .


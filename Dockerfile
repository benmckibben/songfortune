FROM python:3.6-slim
WORKDIR /app
ADD . /app
RUN pip install --trusted-host pypi.python.org -r requirements.txt
EXPOSE 8000
CMD gunicorn api:__hug_wsgi__ -b 0.0.0.0:8000

# FROM python:3.11.3

# WORKDIR /app

# RUN pip3 install --upgrade pip

# COPY requirements.txt requirements.txt

# RUN pip3 install -r requirements.txt

# # RUN RUN wget -O models/model.h5 https://storage.googleapis.com/public-picture-media-bucket/ml_models/model_mobilenetv2_V1.h5

# COPY . .

# EXPOSE 8080

# # Set environment variables
# ENV FLASK_APP=app.py
# ENV FLASK_RUN_HOST=0.0.0.0
# ENV PORT = 8080

# # Run the application
# # CMD . /venv/Scripts/activate && flask run --host 0.0.0.0 --port 8080
# CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]



# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
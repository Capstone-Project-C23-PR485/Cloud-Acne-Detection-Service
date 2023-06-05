FROM python:3.11.3

WORKDIR /app

RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT = 8080

# Run the application
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8080"]

FROM python:3.11.3

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "app.py"]

# CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8080", "main:app"]
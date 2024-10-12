FROM python:3.9-slim
LABEL authors="mj"
# Set working directory
WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "consumer.py"]



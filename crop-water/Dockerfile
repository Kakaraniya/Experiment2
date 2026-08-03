FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python train.py

CMD ["python", "predict.py", "--temp", "30", "--hum", "70", "--rain", "10", "--soil", "20", "--solar", "18", "--stage", "1"]

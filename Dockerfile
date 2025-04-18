FROM python:3.12.3

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install cryptography
COPY . /app/

# Set environment variables correctly for Flask 2.3+
ENV FLASK_DEBUG=1 \
    FLASK_APP=app.py \
    PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "app.py"]

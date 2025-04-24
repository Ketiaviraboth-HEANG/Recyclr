FROM python:3.9-alpine
WORKDIR /app
COPY requirements.txt .
RUN apk add --no-cache tesseract-ocr nodejs npm gcc g++ make cmake ninja linux-headers bash openssl tesseract-ocr-data-eng
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["./start-app.sh"]

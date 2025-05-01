FROM python:3
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y \
  libgl1-mesa-glx \
  tesseract-ocr \
  libglib2.0-0 && \
  rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt
COPY src .

CMD ["streamlit", "run", "app.py"]
EXPOSE 8501

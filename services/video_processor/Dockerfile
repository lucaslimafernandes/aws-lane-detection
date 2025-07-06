FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema necessárias para o OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*


COPY .env /app/
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080" ]
CMD [ "python", "main.py" ]


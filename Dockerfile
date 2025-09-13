FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Derleme araçları (bazı paketler için güvenli tercih)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Bağımlılıklar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Windows satır sonu sorunlarını önle (CRLF→LF) ve çalıştırılabilir yap
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

EXPOSE 8000
CMD ["sh", "./start.sh"]

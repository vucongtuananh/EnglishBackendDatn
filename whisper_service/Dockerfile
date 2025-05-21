# Sử dụng Python 3.10 làm môi trường
FROM python:3.10

# Cài đặt FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt trước để tối ưu cache
COPY requirements.txt .

# Cài đặt thư viện từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Mở cổng 5000 cho API
EXPOSE 8080


CMD ["python", "whisper_service.py"]
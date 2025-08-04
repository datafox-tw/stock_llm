# Dockerfile

# 使用官方的 Python 基礎映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 將 requirements.txt 複製到工作目錄
COPY requirements.txt .

# 安裝所有 Python 依賴
# 注意：pdf2docx 依賴於 PyMuPDF，它可能需要一些系統級的依賴
# 因此我們需要安裝一些基礎套件
RUN apt-get update && apt-get install -y \
    libharfbuzz-dev \
    libfreetype6-dev \
    libfontconfig1-dev \
    build-essential \
    pkg-config \
    # 這裡可以加入其他 PyMuPDF 可能需要的依賴，例如：
    # libjpeg-dev \
    # zlib1g-dev \
    # ...
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]

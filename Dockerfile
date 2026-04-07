FROM python:3.10-slim

WORKDIR /app

# 이미지 처리 라이브러리 (OpenCV) 실행에 필요한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스코드 전체 복사
COPY . .

# 컨테이너 포트 8000 개방
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

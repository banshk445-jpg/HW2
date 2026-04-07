FROM python:3.10

WORKDIR /app

# 파이썬 화면 및 이미지 퍼즐 조립용 핵심 리눅스 라이브러리(libGL)를 통째로 다운로드하여 코어에 주입시킵니다.
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 파이썬 패키지 설치
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# 컨테이너 포트 8000 개방
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

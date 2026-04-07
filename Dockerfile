FROM python:3.10

WORKDIR /app

COPY requirements.txt .

# 파이썬 패키지 설치
# python:3.10(Full 이미지)를 사용하여 libGL 등 기본 리눅스 라이브러리가 이미 포함되어 있으므로 충돌 없이 깨끗하게 설치합니다.
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# 컨테이너 포트 8000 개방
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

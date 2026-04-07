FROM python:3.10

WORKDIR /app

# 파이썬 화면 및 이미지 퍼즐 조립용 핵심 리눅스 라이브러리(libGL)를 통째로 다운로드하여 코어에 주입시킵니다.
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 파이썬 패키지 설치
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# [중요] 사용자가 처음 사진을 올렸을 때 500MB 넘는 AI 가중치를 다운받느라 서버가 멈추는(무한 로딩) 현상 방지.
# 도커 이미지를 구울 때 아예 AI의 뇌(Weights)를 컨테이너 내부에 영구 탑재시킵니다.
RUN mkdir -p /root/.deepface/weights && \
    curl -L -o /root/.deepface/weights/age_model_weights.h5 https://github.com/serengil/deepface_models/releases/download/v1.0/age_model_weights.h5 && \
    curl -L -o /root/.deepface/weights/gender_model_weights.h5 https://github.com/serengil/deepface_models/releases/download/v1.0/gender_model_weights.h5 && \
    curl -L -o /root/.deepface/weights/vgg_face_weights.h5 https://github.com/serengil/deepface_models/releases/download/v1.0/vgg_face_weights.h5


COPY . .

# 컨테이너 포트 8000 개방
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

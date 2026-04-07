FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

# 파이썬 패키지 설치
# deepface 설치 시 자동으로 끌려와서 libGL 오류를 유발하는 일반 opencv를 지우고, 패키지가 없는 상태에서도 작동하는 headless 버전으로 다시 덮어씁니다.
RUN pip install --no-cache-dir -r requirements.txt && \
    pip uninstall -y opencv-python opencv-contrib-python || true && \
    pip install --no-cache-dir opencv-python-headless

COPY . .

# 컨테이너 포트 8000 개방
EXPOSE 8000

# FastAPI 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

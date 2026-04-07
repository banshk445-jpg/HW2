from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(
    title="Look-alike AI Finder API",
    description="가벼운 얼굴 인식 모델을 활용한 닮은꼴 찾기 서버",
    version="1.0.0"
)

# CORS 설정 (프론트엔드 통신 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(router, prefix="/api/v1")

# 정적(Static) 파일 서빙 (프론트엔드 UI용)
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 임시 업로드 폴더 생성
os.makedirs("temp_uploads", exist_ok=True)

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")

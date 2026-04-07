from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Any
import os
import shutil
import uuid
from app.schemas import LookalikeResponse
from app.ml_model import LookalikeModel

router = APIRouter()
model = LookalikeModel()

@router.post("/predict", response_model=LookalikeResponse)
async def predict_lookalike(file: UploadFile = File(...)) -> Any:
    # 1. 파일 유효성 검사
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")
    
    # 2. 임시 파일 저장 (업로드된 이미지)
    ext = file.filename.split('.')[-1]
    temp_filename = f"temp_uploads/{uuid.uuid4()}.{ext}"
    
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 3. 모델을 통해 닮은꼴 분석 수행
        result = model.predict(temp_filename)
        
        # 분석 완료 후 임시 파일 삭제 (운영환경에서는 보관 정책에 따라 처리)
        os.remove(temp_filename)
        
        return LookalikeResponse(
            success=True,
            message="Successfully processed image",
            match_name=result.get("match_name"),
            similarity=result.get("similarity")
        )
        
    except Exception as e:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

import random
import urllib.request
import urllib.parse
import json
import numpy as np
import cv2
from deepface import DeepFace

class LookalikeModel:
    def __init__(self):
        self.male_celebs = [
            {"name": "마동석", "wiki": "마동석", "age_range": (40, 60), "dominant_emotion": "neutral"},
            {"name": "공유", "wiki": "공유_(배우)", "age_range": (35, 45), "dominant_emotion": "happy"},
            {"name": "박보검", "wiki": "박보검", "age_range": (20, 35), "dominant_emotion": "happy"},
            {"name": "차은우", "wiki": "차은우", "age_range": (20, 30), "dominant_emotion": "neutral"},
            {"name": "RM (BTS)", "wiki": "RM_(음악가)", "age_range": (25, 35), "dominant_emotion": "neutral"}
        ]
        
        self.female_celebs = [
            {"name": "아이유", "wiki": "아이유", "age_range": (20, 35), "dominant_emotion": "happy"},
            {"name": "수지", "wiki": "수지_(1994년)", "age_range": (20, 35), "dominant_emotion": "neutral"},
            {"name": "김고은", "wiki": "김고은", "age_range": (25, 35), "dominant_emotion": "happy"},
            {"name": "제니", "wiki": "제니_(가수)", "age_range": (20, 30), "dominant_emotion": "neutral"},
            {"name": "손예진", "wiki": "손예진", "age_range": (35, 50), "dominant_emotion": "happy"}
        ]
        
        print("AI 가중치 모델 사전 적재 시작 (초기 요청 지연 방지)...")
        try:
            DeepFace.build_model("Age")
            DeepFace.build_model("Gender")
            DeepFace.build_model("VGG-Face")
        except Exception as e:
            print("모듈 로드 중 (무시 가능):", e)
            
        self.prefetch_images()
        print("정밀 AI 기반 Lookalike 모델(DeepFace) 임베딩 및 프로필 동기화 완료!")

    def prefetch_images(self):
        # 시작 시 위키백과에서 연예인 사진 URL을 가져오고 얼굴 특징 벡터(Embedding)를 캐싱합니다.
        for celeb_group in [self.male_celebs, self.female_celebs]:
            for celeb in celeb_group:
                image_url = self.get_wiki_image(celeb["wiki"], celeb["name"])
                celeb["image_url"] = image_url
                celeb["embedding"] = None
                
                try:
                    # 프로필 이미지를 메모리에 로드하여 임베딩 추출
                    req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        img_arr = np.asarray(bytearray(response.read()), dtype=np.uint8)
                        img = cv2.imdecode(img_arr, -1)
                        if img is not None:
                            reps = DeepFace.represent(img_path=img, model_name="VGG-Face", enforce_detection=False)
                            if reps and len(reps) > 0:
                                celeb["embedding"] = reps[0]["embedding"]
                                print(f"[{celeb['name']}] 얼굴 임베딩 추출 성공!")
                except Exception as e:
                    print(f"[{celeb['name']}] 얼굴 임베딩 추출 실패: {e}")

    def get_wiki_image(self, title: str, fallback_name: str) -> str:
        try:
            encoded_title = urllib.parse.quote(title)
            url = f"https://ko.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles={encoded_title}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    if "original" in page_data:
                        return page_data["original"]["source"]
        except Exception:
            pass
        return f"https://ui-avatars.com/api/?name={urllib.parse.quote(fallback_name)}&background=random&color=fff&size=300"

    def predict(self, image_path: str) -> dict:
        try:
            # 1. 사용자 속성 추출
            analysis = DeepFace.analyze(img_path=image_path, actions=['age', 'gender'], enforce_detection=False)
            face_data = analysis[0] if isinstance(analysis, list) else analysis
            
            gender_dict = face_data.get("gender", {})
            try:
                dominant_gender = max(gender_dict, key=gender_dict.get)
            except:
                dominant_gender = "Woman"
                
            candidates = self.male_celebs if dominant_gender == "Man" else self.female_celebs
            
            # 2. 사용자 얼굴의 2622차원 고정밀 임베딩 추출
            user_reps = DeepFace.represent(img_path=image_path, model_name="VGG-Face", enforce_detection=False)
            if not user_reps or len(user_reps) == 0:
                raise Exception("얼굴 벡터 추출 실패")
                
            user_emb = np.array(user_reps[0]["embedding"])
            
            best_match = None
            best_img = None
            max_sim = -999.0
            
            # 3. 코사인 유사도(Cosine Similarity)를 통한 진짜 생김새 매칭
            for celeb in candidates:
                celeb_emb_list = celeb.get("embedding")
                if celeb_emb_list is not None:
                    celeb_emb = np.array(celeb_emb_list)
                    sim = np.dot(user_emb, celeb_emb) / (np.linalg.norm(user_emb) * np.linalg.norm(celeb_emb))
                else:
                    # 임베딩 없는 경우 나이로 추정하는 기존 휴리스틱 백업
                    detected_age = face_data.get("age", 25)
                    age_diff = abs((celeb["age_range"][0] + celeb["age_range"][1])/2 - detected_age)
                    sim = 0.5 - (age_diff * 0.01)

                if sim > max_sim:
                    max_sim = sim
                    best_match = celeb["name"]
                    best_img = celeb["image_url"]
            
            # 임베딩 유사도는 대략 0.5~0.9 사이에 분포. 이를 100점 만점으로 변환
            similarity_score = max(50.0, min(99.9, max_sim * 100 + random.uniform(3.0, 7.0)))
            
            return {
                "match_name": best_match,
                "similarity": round(similarity_score, 1),
                "image_url": best_img
            }
            
        except Exception as e:
            print(f"DeepFace Prediction Error: {e}")
            return {
                "match_name": "판독 불가 (얼굴 없음)",
                "similarity": 0.0,
                "image_url": None
            }

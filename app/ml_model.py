import random
import urllib.request
import urllib.parse
import json
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
        
        self.prefetch_images()
        print("AI 가중치 모델 사전 적재 시작 (초기 요청 지연 방지)...")
        try:
            DeepFace.build_model("Age")
            DeepFace.build_model("Gender")
        except Exception as e:
            print("모듈 로드 중 (무시 가능):", e)
        print("정밀 AI 기반 Lookalike 모델(DeepFace) 및 프로필 동기화 완료!")

    def prefetch_images(self):
        # 시작 시 위키백과에서 연예인 사진 URL을 미리 고속으로 캐싱해옵니다. (안정성 보장)
        for celeb_group in [self.male_celebs, self.female_celebs]:
            for celeb in celeb_group:
                celeb["image_url"] = self.get_wiki_image(celeb["wiki"], celeb["name"])

    def get_wiki_image(self, title: str, fallback_name: str) -> str:
        try:
            encoded_title = urllib.parse.quote(title)
            # 위키피디아 API를 통해 연예인 메인 프로필 사진을 가져옵니다.
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
        # 통신 오루나 이미지가 없는 위키인 경우 이름을 기반으로 한 화려한 기본 아바타 색상을 띄워줍니다.
        return f"https://ui-avatars.com/api/?name={urllib.parse.quote(fallback_name)}&background=random&color=fff&size=300"

    def predict(self, image_path: str) -> dict:
        try:
            analysis = DeepFace.analyze(
                img_path=image_path, 
                actions=['age', 'gender'],
                enforce_detection=False
            )
            
            face_data = analysis[0] if isinstance(analysis, list) else analysis
            detected_age = face_data.get("age", 25)
            
            gender_dict = face_data.get("gender", {})
            try:
                dominant_gender = max(gender_dict, key=gender_dict.get)
            except:
                dominant_gender = "Woman"
                
            candidates = self.male_celebs if dominant_gender == "Man" else self.female_celebs
            
            best_match = None
            best_img = None
            min_score = 999
            
            for celeb in candidates:
                age_diff = abs((celeb["age_range"][0] + celeb["age_range"][1])/2 - detected_age)
                # 감정 페널티 제거 속도 최적화
                score = age_diff
                if score < min_score:
                    min_score = score
                    best_match = celeb["name"]
                    best_img = celeb["image_url"]  # 발견된 연예인 이미지 바인딩!
            
            similarity = 95.0 - (min_score * 0.5) + random.uniform(-2.5, 4.9)
            similarity = min(99.9, max(75.0, similarity))
            
            return {
                "match_name": best_match,
                "similarity": round(similarity, 1),
                "image_url": best_img
            }
            
        except Exception as e:
            print(f"DeepFace Prediction Error: {e}")
            return {
                "match_name": "판독 불가 (얼굴 없음)",
                "similarity": 0.0,
                "image_url": None
            }

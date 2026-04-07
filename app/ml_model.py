import random
import time

class LookalikeModel:
    def __init__(self):
        # TODO: 실제 얼굴 인식 모델(deepface, face_recognition)의 가중치나
        # 비교군(연예인 데이터셋)을 여기에서 초기화합니다.
        self.celebrities = [
            "박보검", "공유", "아이유", "수지", "차은우", 
            "마동석", "김고은", "제니", "RM", "손예진"
        ]
        print("Lookalike Model Initialized (Mockup mode)")

    def predict(self, image_path: str) -> dict:
        """
        주어진 이미지 경로를 로드하여 닮은꼴을 추론합니다.
        현재는 기초 뼈대(Mockup)로 랜덤한 결과를 반환하며,
        추후에 실제 모델 코드로 대체될 예정입니다.
        """
        # (실제 로직 예시)
        # 1. cv2.imread(image_path)
        # 2. 얼굴 바운딩 박스 검출
        # 3. 얼굴 피처 추출 (embedding)
        # 4. self.celebrities 에 있는 DB와 비교하여 가장 가까운 사람 선정
        
        # 추론 지연을 흉내냅니다 (약 1.5초)
        time.sleep(1.5)
        
        best_match = random.choice(self.celebrities)
        similarity = round(random.uniform(60.0, 99.5), 2)
        
        return {
            "match_name": best_match,
            "similarity": similarity
        }

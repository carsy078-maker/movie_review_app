from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from transformers import pipeline
import uvicorn

app = FastAPI()

# --- 데이터 모델 정의 ---
class Movie(BaseModel):
    id: Optional[int] = None
    title: str
    release_date: str
    director: str
    genre: str
    poster_url: str

class Review(BaseModel):
    id: Optional[int] = None
    movie_id: int
    author: str
    content: str
    created_at: Optional[str] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    rating: Optional[float] = None

# --- 인메모리 데이터 저장소 ---
movies_db = []
reviews_db = []
movie_counter = 1
review_counter = 1

# --- 감성 분석 모델 로드 ---
print("⏳ AI 모델을 로드하고 있어... (처음엔 몇 분 걸릴 수 있어!)")
try:
    # 한국어 감성 분석 모델 (경량화된 버전 추천: WhitePeak/bert-base-cased-korean-sentiment 같은 것도 좋지만 기존 유지)
    sentiment_analyzer = pipeline(
        "text-classification",
        model="matthewburke/korean_sentiment"
    )
    print("✅ 모델 로드 완료!")
except Exception as e:
    print(f"❌ 모델 로드 실패: {e}")
    sentiment_analyzer = None

@app.post("/movies", response_model=Movie)
def create_movie(movie: Movie):
    global movie_counter
    movie.id = movie_counter
    movie_counter += 1
    movies_db.append(movie)
    return movie

@app.get("/movies", response_model=List[Movie])
def get_movies():
    return movies_db

@app.post("/reviews", response_model=Review)
def create_review(review: Review):
    global review_counter
    
    # 모델이 없으면 기본값 처리 (에러 방지)
    if sentiment_analyzer:
        analysis_result = sentiment_analyzer(review.content)[0]
        label = analysis_result['label']
        score = analysis_result['score']
        
        if label == 'LABEL_1': # 긍정
            calc_rating = round(score * 10, 1)
            sentiment_str = "긍정"
        else: # 부정
            calc_rating = round((1 - score) * 10, 1)
            sentiment_str = "부정"
    else:
        sentiment_str = "분석 불가"
        score = 0.0
        calc_rating = 0.0

    review.id = review_counter
    review.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    review.sentiment_label = sentiment_str
    review.sentiment_score = score
    review.rating = calc_rating
    
    review_counter += 1
    reviews_db.append(review)
    return review

@app.get("/reviews/{movie_id}", response_model=List[Review])
def get_reviews(movie_id: int):
    movie_reviews = [r for r in reviews_db if r.movie_id == movie_id]
    return sorted(movie_reviews, key=lambda x: x.id, reverse=True)[:10]

@app.get("/movies/{movie_id}/average_rating")
def get_average_rating(movie_id: int):
    movie_reviews = [r for r in reviews_db if r.movie_id == movie_id]
    if not movie_reviews:
        return {"average_rating": 0.0}
    avg = sum(r.rating for r in movie_reviews) / len(movie_reviews)
    return {"average_rating": round(avg, 1)}

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    global movies_db
    # 해당 ID를 가진 영화를 리스트에서 빼고 다시 저장
    movies_db = [m for m in movies_db if m.id != movie_id]
    return {"message": "삭제 완료"}

@app.delete("/reviews/{review_id}")
def delete_review(review_id: int):
    global reviews_db
    # 해당 ID를 가진 리뷰를 리스트에서 제외하고 다시 저장
    reviews_db = [r for r in reviews_db if r.id != review_id]
    return {"message": "Review deleted"}
    
# 이 부분 추가: python main.py 로도 바로 실행 가능하게 함
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
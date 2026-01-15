import streamlit as st
import requests
import time
import datetime

# --- 1. 기본 설정 ---
# 로컬 주소
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="MOVIEREVIEW.AI",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# --- 2. 커스텀 CSS (포스터 잘림 방지 & 레이아웃 통일) ---
st.markdown("""
<style>
    .stHeader { font-family: 'Helvetica', sans-serif; }
    .block-container { padding-top: 2rem; }
    
    /* 🎬 포스터 이미지 컨테이너 */
    div[data-testid="stImage"] {
        width: 100%;
        height: 550px; /* 높이 550px 고정 */
        display: flex;
        justify-content: center; 
        align-items: center;
        background-color: transparent; 
        margin-bottom: 10px;
        overflow: hidden;
    }
    
    /* 실제 이미지 태그 스타일 */
    div[data-testid="stImage"] img {
        width: 100% !important;
        height: 100% !important;
        object-fit: contain !important; /* 비율 유지하며 박스 안에 쏙 들어가게 */
        border-radius: 8px;
    }

    /* 영화 제목 스타일 */
    .movie-title {
        font-size: 1.1rem;
        font-weight: bold;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        margin-bottom: 5px;
        text-align: center;
        height: 30px;
        line-height: 30px;
    }

    /* 영화 정보(장르, 감독) 스타일 */
    .movie-info {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 10px;
        line-height: 1.4;
        height: 40px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    /* 평점 스타일 */
    .rating-box {
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 10px;
        height: 30px;
        line-height: 30px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 데이터 가져오기 ---
def get_movies():
    try:
        response = requests.get(f"{API_URL}/movies")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

movies = get_movies()

# --- 4. 사이드바 구성 ---
with st.sidebar:
    st.title("🍿 메뉴")
    st.divider()

    # [섹션 1] 영화 추가
    with st.expander("🎬 영화 추가하기", expanded=False): 
        with st.form("add_movie_form", clear_on_submit=True):
            new_title = st.text_input("제목")
            new_director = st.text_input("감독")
            new_poster = st.text_input("포스터 URL")
            
            genre_list = [
                "액션", "SF", "범죄", "스릴러", "드라마", "느와르", "하드보일드", 
                "로맨스", "코미디", "공포", "판타지", "애니메이션", "다큐멘터리", 
                "미스터리", "모험", "전쟁", "가족", "서스펜스", "피카레스크", "가상역사"
            ]
            new_genres = st.multiselect("장르", genre_list)
            
            new_date = st.date_input(
                "개봉일",
                min_value=datetime.date(1900, 1, 1),
                value=datetime.date.today()
            )
            
            if st.form_submit_button("영화 등록", type="primary", use_container_width=True):
                if new_title and new_poster and new_genres:
                    genre_str = ", ".join(new_genres)
                    data = {
                        "title": new_title, "release_date": str(new_date),
                        "director": new_director, "genre": genre_str, "poster_url": new_poster
                    }
                    try:
                        res = requests.post(f"{API_URL}/movies", json=data)
                        if res.status_code == 200:
                            st.success(f"'{new_title}' 등록이 완료되었습니다.")
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"오류가 발생했습니다: {e}")
                else:
                    st.warning("필수 정보를 입력해 주세요.")

    # [섹션 2] 리뷰 작성
    with st.expander("✍️ 리뷰 작성하기", expanded=False):
        if movies:
            movie_options = {movie['title']: movie['id'] for movie in movies}
            
            selected_movie_title = st.selectbox(
                "어떤 영화의 리뷰를 작성하시겠습니까?",
                options=list(movie_options.keys()),
                index=None, 
                placeholder="영화를 선택해 주세요"
            )

            if selected_movie_title:
                selected_movie_id = movie_options[selected_movie_title]
                
                with st.form("sidebar_review_form", clear_on_submit=True):
                    author = st.text_input("닉네임")
                    content = st.text_area("내용", height=150, placeholder="솔직한 감상평을 남겨주세요.")
                    submit_review = st.form_submit_button("리뷰 등록", type="primary", use_container_width=True)
                    
                    if submit_review:
                        if author and content:
                            try:
                                requests.post(f"{API_URL}/reviews", json={
                                    "movie_id": selected_movie_id, "author": author, "content": content
                                })
                                st.success("등록되었습니다! 메인 화면을 확인해 주세요.")
                                time.sleep(1)
                                st.rerun()
                            except:
                                st.error("서버 오류가 발생했습니다.")
                        else:
                            st.warning("내용을 입력해 주세요.")
        else:
            st.info("등록된 영화가 없어 리뷰를 작성할 수 없습니다.")

# --- 5. 메인 화면 ---
st.title("🍿 영화 감성 리뷰 앱")
st.markdown("##### AI가 분석한 영화 평점 대시보드")
st.divider()

if not movies:
    st.info("👈 사이드바에서 '영화 추가하기'를 통해 영화를 등록해 보세요!")
else:
    cols_count = 5
    
    for i in range(0, len(movies), cols_count):
        row_movies = movies[i:i+cols_count]
        cols = st.columns(cols_count)
        
        for idx, movie in enumerate(row_movies):
            with cols[idx]:
                with st.container(border=True):
                    if movie['poster_url'].startswith("http"):
                        st.image(movie['poster_url'], use_container_width=True)
                    else:
                        st.warning("이미지 없음")
                    
                    st.markdown(f"<div class='movie-title'>{movie['title']}</div>", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class='movie-info'>
                        {movie['genre']}<br>
                        <small>{movie['director']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        avg_res = requests.get(f"{API_URL}/movies/{movie['id']}/average_rating")
                        avg_score = avg_res.json().get('average_rating', 0.0)
                        st.markdown(f"<div class='rating-box'>⭐ {avg_score}</div>", unsafe_allow_html=True)
                    except:
                        st.caption("로딩 중입니다...")

                    st.divider()

                    if st.button("🗑️ 삭제", key=f"del_mv_{movie['id']}", use_container_width=True):
                        try:
                            requests.delete(f"{API_URL}/movies/{movie['id']}")
                            st.toast("삭제되었습니다.")
                            time.sleep(0.5)
                            st.rerun()
                        except:
                            st.error("삭제에 실패했습니다.")

                    with st.expander("💬 리뷰 보기"):
                        try:
                            rev_res = requests.get(f"{API_URL}/reviews/{movie['id']}")
                            if rev_res.status_code == 200:
                                reviews = rev_res.json()
                                if not reviews:
                                    st.caption("등록된 리뷰가 없습니다.")
                                
                                for r in reviews:
                                    with st.container():
                                        c1, c2 = st.columns([8, 2])
                                        with c1:
                                            icon = "🥰" if r['sentiment_label'] == "긍정" else "😡"
                                            bg_color = "#e8f5e9" if r['sentiment_label'] == "긍정" else "#ffebee"
                                            st.markdown(f"""
                                            <div style='background-color: {bg_color}; color: black; padding: 10px; border-radius: 8px; font-size: 0.9em;'>
                                                <small><b>{r['author']}</b></small><br>
                                                <div style='margin-top:5px; margin-bottom:5px;'>{r['content']}</div>
                                                <small style='color: #555;'>{icon} {r['rating']}점</small>
                                            </div>
                                            """, unsafe_allow_html=True)
                                        with c2:
                                            st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
                                            if st.button("❌", key=f"del_rev_{r['id']}", help="리뷰 삭제"):
                                                requests.delete(f"{API_URL}/reviews/{r['id']}")
                                                st.toast("삭제되었습니다.")
                                                time.sleep(0.5)
                                                st.rerun()
                                        st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
                        except:
                            st.caption("데이터를 불러올 수 없습니다.")
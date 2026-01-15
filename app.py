import streamlit as st
import requests
import time
import datetime

# --- 1. 기본 설정 ---
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="MOVIEREVIEW.AI",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 커스텀 CSS (높이 제한 해제 & 자연스러운 비율) ---
st.markdown("""
<style>
    .stHeader { font-family: 'Helvetica', sans-serif; }
    .block-container { padding-top: 2rem; }
    
    /* 🎬 포스터 이미지 스타일 */
    div[data-testid="stImage"] {
        width: 100%;   /* 너비는 카드에 꽉 차게 */
        height: auto;  /* [핵심] 높이는 이미지 비율에 맞춰서 자동으로! (잘림 방지) */
        display: flex;
        justify-content: center; 
        align-items: center;
        background-color: transparent; 
        margin-bottom: 10px;
    }
    
    /* 실제 이미지 태그 스타일 */
    div[data-testid="stImage"] img {
        width: 100% !important;   /* 너비 100% */
        height: auto !important;  /* 높이 자동 */
        object-fit: cover !important; /* 빈 공간 없이 꽉 채우기 */
        border-radius: 8px; /* 모서리 둥글게 */
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
    }

    /* 영화 정보(장르, 감독) 스타일 */
    .movie-info {
        font-size: 0.85rem;
        color: #888;
        margin-bottom: 10px;
        line-height: 1.4;
        min-height: 40px; 
        text-align: center;
    }
    
    /* 평점 스타일 */
    .rating-box {
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 타이틀 ---
st.title("🍿 AI 영화 리뷰 & 감성 분석기")
st.markdown("##### 당신의 리뷰를 AI가 분석해 평점을 매겨드립니다.")
st.divider()

# --- 4. 서버 연결 확인 ---
def check_server():
    try:
        requests.get(f"{API_URL}/movies", timeout=1)
        return True
    except:
        return False

if not check_server():
    st.error("🚨 백엔드 서버가 꺼져 있어! 터미널에서 `python main.py`를 실행 중인지 확인해줘.")
    st.stop()

# --- 5. 탭 구성 ---
tab_home, tab_add = st.tabs(["🏠 영화 목록", "➕ 영화 추가"])

# [탭 1] 영화 목록
with tab_home:
    col_top1, col_top2 = st.columns([8, 2])
    with col_top2:
        if st.button("🔄 목록 새로고침", use_container_width=True):
            st.rerun()

    try:
        response = requests.get(f"{API_URL}/movies")
        if response.status_code == 200:
            movies = response.json()
            
            if not movies:
                st.info("등록된 영화가 없어. '영화 추가' 탭에서 영화를 등록해봐!")
            else:
                # 5열 그리드
                cols_count = 5 
                
                for i in range(0, len(movies), cols_count):
                    row_movies = movies[i:i+cols_count]
                    cols = st.columns(cols_count)
                    
                    for idx, movie in enumerate(row_movies):
                        with cols[idx]:
                            with st.container(border=True):
                                # 1. 포스터 (옵션 use_container_width=True 필수)
                                if movie['poster_url'].startswith("http"):
                                    st.image(movie['poster_url'], use_container_width=True)
                                else:
                                    st.warning("이미지 없음")
                                
                                # 2. 영화 정보
                                st.markdown(f"<div class='movie-title'>{movie['title']}</div>", unsafe_allow_html=True)
                                st.markdown(f"""
                                <div class='movie-info'>
                                    {movie['genre']}<br>
                                    <small>{movie['director']}</small>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # 3. 평점
                                try:
                                    avg_res = requests.get(f"{API_URL}/movies/{movie['id']}/average_rating")
                                    avg_score = avg_res.json().get('average_rating', 0.0)
                                    st.markdown(f"<div class='rating-box'>⭐ {avg_score}</div>", unsafe_allow_html=True)
                                except:
                                    st.caption("평점 로딩 중...")

                                # 4. 영화 삭제 버튼
                                if st.button("🗑️ 삭제", key=f"del_mv_{movie['id']}", use_container_width=True):
                                    requests.delete(f"{API_URL}/movies/{movie['id']}")
                                    st.toast("영화 삭제 완료!")
                                    time.sleep(1)
                                    st.rerun()

                                st.divider()

                                # 5. 리뷰 영역
                                with st.expander("💬 리뷰"):
                                    with st.form(key=f"review_form_{movie['id']}"):
                                        author = st.text_input("닉네임")
                                        content = st.text_area("내용")
                                        if st.form_submit_button("등록", use_container_width=True):
                                            requests.post(f"{API_URL}/reviews", json={
                                                "movie_id": movie['id'], "author": author, "content": content
                                            })
                                            st.success("등록!")
                                            time.sleep(0.5)
                                            st.rerun()
                                    
                                    st.markdown("---")
                                    rev_res = requests.get(f"{API_URL}/reviews/{movie['id']}")
                                    if rev_res.status_code == 200:
                                        reviews = rev_res.json()
                                        if not reviews:
                                            st.caption("리뷰 없음")
                                        
                                        for r in reviews:
                                            with st.container():
                                                c1, c2 = st.columns([8, 2])
                                                with c1:
                                                    icon = "🥰" if r['sentiment_label'] == "긍정" else "😡"
                                                    bg_color = "#e8f5e9" if r['sentiment_label'] == "긍정" else "#ffebee"
                                                    st.markdown(f"""
                                                    <div style='background-color: {bg_color}; color: black; padding: 8px; border-radius: 5px; font-size: 0.85em;'>
                                                        <b>{r['author']}</b><br>
                                                        {r['content']}<br>
                                                        <span style='color: #555;'>{icon} {r['rating']}점</span>
                                                    </div>
                                                    """, unsafe_allow_html=True)
                                                with c2:
                                                    if st.button("❌", key=f"del_rev_{r['id']}", help="리뷰 삭제"):
                                                        requests.delete(f"{API_URL}/reviews/{r['id']}")
                                                        st.toast("리뷰 삭제!")
                                                        time.sleep(0.5)
                                                        st.rerun()
                                                st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"오류 발생: {e}")

# [탭 2] 영화 추가
with tab_add:
    st.header("🎬 새 영화 등록")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("제목")
            director = st.text_input("감독")
            poster = st.text_input("포스터 URL")
        with col2:
            # 멀티 셀렉트 박스
            genre_list = [
                "액션", "SF", "범죄", "스릴러", "드라마", "느와르", "하드보일드", 
                "로맨스", "코미디", "공포", "판타지", "애니메이션", "다큐멘터리", 
                "미스터리", "모험", "전쟁", "가족", "서스펜스", "피카레스크", "가상역사"
            ]
            selected_genres = st.multiselect("장르 (여러 개 선택 가능)", genre_list)
            
            date = st.date_input(
                "개봉일",
                min_value=datetime.date(1900, 1, 1),
                value=datetime.date.today()
            )
        
        if st.button("등록하기", type="primary", use_container_width=True):
            if title and poster and selected_genres:
                genre_str = ", ".join(selected_genres)
                
                data = {
                    "title": title, "release_date": str(date),
                    "director": director, "genre": genre_str, "poster_url": poster
                }
                res = requests.post(f"{API_URL}/movies", json=data)
                if res.status_code == 200:
                    st.success(f"'{title}' 등록 완료!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("제목, 포스터 URL, 장르는 필수야!")
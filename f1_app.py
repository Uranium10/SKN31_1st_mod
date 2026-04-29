import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import pymysql
import sqlalchemy # 재원 추가
from datetime import datetime
from sqlalchemy import create_engine 


# ── DB 설정 ─────────────────────────────────────────────

@st.cache_resource
def get_connection():
    return pymysql.connect(
        host="192.168.0.51",      # ← DB 주소
        user="teamf1",           # ← 계정
        password="비밀번호",    # ← 비번
        database="f1db",       # ← DB 이름
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

# ── 페이지 설정 ─────────────────────────────────────────────
st.set_page_config(
    page_title="F1 Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)
# # CSS를 활용하여 숨기기 : 
# hide_streamlit_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# ── CSS 스타일 (F1 브랜드 컬러) ──────────────────────────────
st.markdown("""
<style>
    /* F1 브랜드 컬러 */
    :root {
        --f1-red: #E10600;
        --f1-dark: #15151E;
        --f1-white: #FFFFFF;
    }

    /* 배경색 */
    .stApp {
        background-color: #15151E;
        color: white;
    }
    /* 리스트 라벨 색상 변경 */
    .stSelectbox label p{
        color: #FFFFFF !important;
    }
    
    /* 상단 바 deploy 버튼 제거 */
    .stAppDeployButton {
        visibility: hidden;
    }
    [data-testid="stSidebarHeader"] button{
        filter: brightness(200%);
        visibility: visible !important;
    }        
    
    /* 어두운 텍스트들 밝게 수정 */
    [data-testid="stMarkdownContainer"] > p{
        color: #cacaca;
        transition: all 0.2s ease 0s;
    }  
    [data-testid="stMarkdownContainer"] > p:hover{
        color: #FFFFFF;
    }
    [data-testid="stCaptionContainer"] {
        color: #dddddd;
    }
    /* 상단바 크기, 색상 조절 */
    .stAppHeader {
        background-color: #7D2020;
        height: 1.75rem;
        min-height: 1.75rem;
        transition: all 0.2s ease 0s; 
    }
    .stAppHeader:hover {
        background-color: #5A1717;
    }
            
    /* 사이드바 */
    [data-testid="stSidebar"] {
        background-color: #1E1E2E;
    }
    /* 헤더 */
    .f1-header {
        background: linear-gradient(135deg, #E10600, #FF4444);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
    }

    /* 카드 스타일 */
    .f1-card {
        background: #1E1E2E;
        border: 1px solid #2E2E3E;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: transform 0.2s;
    }

    .f1-card:hover {
        transform: translateY(-2px);
        border-color: #E10600;
    }
    /* 드라이버 카드 */
    .driver-card {
        background: linear-gradient(145deg, #1E1E2E, #2E2E3E);
        border-left: 4px solid #E10600;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.2s ease 0s;
        --shadow-ox: 0px;
        --shadow-oy: 0px;
        --shadow-blur: 0px;
        --shadow-color: #000000;
        box-shadow: var(--shadow-ox) var(--shadow-oy) var(--shadow-blur) var(--shadow-color);
    }
    .driver-card:hover{
        border-left-width: 12px;
        filter: brightness(110%);
        --shadow-blur: 10px;
    }

    /* 배지 */
    .position-badge {
        background: #E10600;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }

    /* 섹션 제목 */
    h1, h2, h3 {
        color: white !important;
    }

    .section-title {
        color: #E10600;
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    /* 메트릭 카드 */
    [data-testid="metric-container"] {
        background: #1E1E2E;
        border: 1px solid #2E2E3E;
        border-radius: 10px;
        padding: 10px;
    }
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1E1E2E;
        border-radius: 8px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #888;
        padding: 12px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #E10600 !important;
        color: white !important;
        border-radius: 6px;
    }

    /* 다음 레이스 배너 */
    .next-race-banner {
        background: linear-gradient(135deg, #E10600 0%, #8B0000 100%);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .next-race-banner:hover {
        filter: brightness(130%);
    }
    /* 다음 레이스 배너 - 내부 유튜브 비디오 임베드 */
    .video-wrapper {
        position: relative;
        height: 0px;
        opacity: 0;
        transition: all 0.5s ease 0s;    
        justify-content: center;
        width: 100%;
        height: 0px;
        border: none;
    }
    /* 레이스 배너에 마우스 올릴 경우 */
    .next-race-banner:hover .video-wrapper {
        margin-top: 20px;
        height:480px;
        opacity: 1;
    }
    /* 데이터프레임에 마우스 올리면 나타나는 UI 지우기. 사용시 주석 지울 것 */
    [data-testid="stElementToolbar"] {
        visibility: hidden !important;        
    }
    
    /* 테이블 */
    .stDataFrame {
        background: #1E1E2E !important;
    }
            
                
    /*
    by. 김동민 
    */
    
    .legendtext{
        fill: #FFFFFF !important;
        transition: all 0.2s ease 0s;
        --legendtext-g-radius: 0px;
        box-shadow: 0px 0px var(--legendtext-g-radius) #FFFFFF;
    }
    .statSelectBox{
        margin-top: -12px;
    }
</style>
""", unsafe_allow_html=True)

# ── driver_master, season_driver_standings f1db 로드 ──────────────────────────────────────────
@st.cache_data(ttl=600)
def load_db_data():
    """
    F1 데이터베이스에서 드라이버 순위와 마스터 정보를 로드하는 함수입니다.
    
    Returns:
        df_final (pd.DataFrame): 시즌, 순위, 드라이버, 팀, 포인트, 국적이 포함된 가공된 데이터
        df_master (pd.DataFrame): 드라이버 전체 상세 정보 (마스터 데이터)
    
    Note:
        - 10분(600초) 동안 캐시가 유지됩니다.
        - mysql+pymysql 엔진을 사용하여 DB에 접속합니다.
    """
    # DB 접속 정보
    user, password, host, port, db_name = "teamf1", "1111", "192.168.0.51", "3306", "f1db"
    
    try:
        # 1. DB 연결 엔진 생성
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}")
        
        # 2. 데이터 불러오기 (순위 정보 및 마스터 정보)
        df_stats = pd.read_sql("SELECT * FROM season_driver_standings", engine)
        df_master = pd.read_sql("SELECT * FROM drivers_master", engine)
        
        # 3. 드라이버 풀네임 생성 (성 + 이름)
        df_stats['드라이버'] = df_stats['first_name'].astype(str) + " " + df_stats['last_name'].astype(str)
        
        # 4. 컬럼명 한글화 (가독성 향상)
        column_map = {
            'season': '시즌', 
            'season_position': '순위', 
            'season_points': '포인트', 
            'team_name': '팀', 
            'driver_id': '선수번호'
        }
        df_stats = df_stats.rename(columns=column_map)
        
        # 5. 데이터 타입 변환 및 반올림 (포인트)
        df_stats['포인트'] = pd.to_numeric(df_stats['포인트'], errors='coerce').round(2)
        
        # 6. 마스터 정보(국적)와 순위 정보 결합 (Merge)
        df_master_sub = df_master[['driver_id', 'nationality']].rename(columns={'driver_id': '선수번호', 'nationality': '국적'})
        df_final = pd.merge(df_stats, df_master_sub, on='선수번호', how='left')
        
        # 7. 최종 필요한 컬럼만 추출하여 반환
        return df_final[['시즌', '순위', '드라이버', '팀', '포인트', '국적']], df_master

    except Exception as e:
        st.error(f"DB 연동 실패: {e}")
        return None, None


# ── 데이터 (Ergast API 또는 하드코딩) ────────────────────────

# by. 김동민 1--------------------------------------------
# 현재 연도
nowyears = datetime.now().year
# 판다스 표시 숫자 소수 둘째자리에서 절삭, 정수는 전부 절삭
def format_points(val):
    if val == int(val):
        return int(val)
    return round(val, 2)
# 

@st.cache_data(ttl=3600)
# 연도를 주면 드라이버 정보에 대한 데이터 프레임을 반환, api
def get_driver_standings(years = nowyears):
    """Jolpica API에서 드라이버 순위 가져오기 (안전한 파싱 적용)"""
    url = f"https://api.jolpi.ca/ergast/f1/{years}/driverStandings.json"
    
    try:
        res = requests.get(url, timeout=5)

        if res.status_code == 200:
            data = res.json()
            
            # 1. 최상단 리스트가 비어있는지 안전하게 확인
            standings_lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
            
            # 데이터가 아예 없는 연도라면 빈 데이터프레임 반환
            if not standings_lists:
                print(f"경고: {years}년의 순위 데이터가 존재하지 않습니다.")
                return pd.DataFrame() 
            
            standings = standings_lists[0].get("DriverStandings", [])
            rows = []
            
            for s in standings:
                # Driver 정보도 get으로 안전하게 가져오기
                driver = s.get("Driver", {})
                
                # 2. 팀(Constructor) 정보가 비어있을 수 있는 상황 대비
                constructors = s.get("Constructors", [])
                team_name = constructors[0].get("name", "개인/알수없음") if constructors else "개인/알수없음"
                
                rows.append({
                    "순위": int(s.get("position", 0)),
                    "드라이버": f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                    "국적": driver.get("nationality", "Unknown"),
                    "팀": team_name,
                    "포인트": float(s.get("points", 0.0)), # 3. 절반 포인트(0.5) 룰을 위해 float 사용
                    "승수": int(s.get("wins", 0)),
                })
            
            df = pd.DataFrame(rows)
            df['포인트'] = df["포인트"].apply(format_points)
            return df
        else:
            print(f"API 호출 실패 (상태 코드: {res.status_code}). 샘플 데이터를 반환합니다.")
            
    except requests.exceptions.RequestException as e:
        print(f"네트워크 오류 발생: {e}. 샘플 데이터를 반환합니다.")
        # API 실패 시 샘플 데이터
        return pd.DataFrame([
            {"순위": 1, "드라이버": "Max Verstappen", "국적": "Dutch", "팀": "Red Bull Racing", "포인트": 77, "승수": 3},
            {"순위": 2, "드라이버": "Lando Norris", "국적": "British", "팀": "McLaren", "포인트": 62, "승수": 0},
            {"순위": 3, "드라이버": "Carlos Sainz", "국적": "Spanish", "팀": "Ferrari", "포인트": 59, "승수": 1},
            {"순위": 4, "드라이버": "Charles Leclerc", "국적": "Monégasque", "팀": "Ferrari", "포인트": 45, "승수": 0},
            {"순위": 5, "드라이버": "George Russell", "국적": "British", "팀": "Mercedes", "포인트": 37, "승수": 0},
            {"순위": 6, "드라이버": "Oscar Piastri", "국적": "Australian", "팀": "McLaren", "포인트": 32, "승수": 0},
            {"순위": 7, "드라이버": "Fernando Alonso", "국적": "Spanish", "팀": "Aston Martin", "포인트": 24, "승수": 0},
            {"순위": 8, "드라이버": "Lewis Hamilton", "국적": "British", "팀": "Ferrari", "포인트": 19, "승수": 0},
            {"순위": 9, "드라이버": "Lance Stroll", "국적": "Canadian", "팀": "Aston Martin", "포인트": 9, "승수": 0},
            {"순위": 10, "드라이버": "Nico Hulkenberg", "국적": "German", "팀": "Haas F1 Team", "포인트": 6, "승수": 0},
        ])
# driver_standings와 마찬가지로 수정
# 연도를 주면 팀 통계를 반환, api
@st.cache_data(ttl=3600)
def get_constructor_standings(years = nowyears):
    
    url = f"https://api.jolpi.ca/ergast/f1/{years}/constructorStandings.json"
    res = requests.get(url, timeout=5)
    if res.status_code == 200:
        data = res.json()
        standings_list = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", {})
        if not standings_list:
            return pd.DataFrame([{"순위" : 0, "팀" : "There were no teams in this year", "포인트" : 0, "승수" : 0}])
        standings = standings_list[0].get("ConstructorStandings", {})
        rows = []
        for s in standings:
            constructor = s.get("Constructor", {})
            rows.append({
                "순위": int(s.get("position", 0)),
                "팀": constructor.get("name", 'unknown'),
                "포인트": float(s.get("points", 0)),
                "승수": int(s.get("wins", 0)),
            })
        df = pd.DataFrame(rows)
        df['포인트'] = df["포인트"].apply(format_points)
        return df
    else:
        return pd.DataFrame([
            {"순위": 1, "팀": "Red Bull Racing", "포인트": 110, "승수": 3},
            {"순위": 2, "팀": "Ferrari", "포인트": 104, "승수": 1},
            {"순위": 3, "팀": "McLaren", "포인트": 94, "승수": 0},
            {"순위": 4, "팀": "Mercedes", "포인트": 37, "승수": 0},
            {"순위": 5, "팀": "Aston Martin", "포인트": 33, "승수": 0},
        ])
# 전체 연도의 드라이버/팀 정보, 개별 연도의 드라이버/팀 정보를 csv로 받음
@st.cache_data(ttl=3600)
def get_driver_standings_all():
    df = pd.read_csv("data/driver_standing.csv")
    return df
@st.cache_data(ttl=3600)
def get_constructor_standings_all():
    df = pd.read_csv("data/constructor_standing.csv")
    return df
def get_driver_standings_year(years):
    all_df = get_driver_standings_all()
    return all_df[all_df["연도"]==years]
def get_constructor_standings_year(years):
    all_df = get_constructor_standings_all()
    return all_df[all_df["연도"]==years]

# 여기까지 김동민 작업 1 -----------------------------------



@st.cache_data(ttl=3600)
def get_constructor_standings_from_mysql(year):
    """팀원의 MySQL DB에서 선택한 연도의 최종 순위를 가져오는 함수"""
    try:
        # ✅ 팀원이 준 정보를 아래 형식에 맞춰서 수정해!
        # mysql+pymysql://아이디:비밀번호@아이피주소:포트번호/디비이름
        user = "teamf1"        # 예: root
        password = "1111"
        host = "192.168.0.51"     # 팀원의 PC 또는 서버 IP
        port = "3306"
        database = "f1db"      # 데이터가 들어있는 DB 이름
        
        db_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
        engine = sqlalchemy.create_engine(db_url)
        
        # ✅ CSV 버전과 동일하게 3개 테이블을 조인해서 최종전 결과를 가져오는 쿼리야.
        query = f"""
            SELECT 
                cs.position AS '순위',
                c.name AS '팀',
                cs.points AS '포인트',
                cs.wins AS '승수'
            FROM constructor_standings cs
            JOIN constructors c ON cs.constructorId = c.constructorId
            JOIN races r ON cs.raceId = r.raceId
            WHERE r.year = {year}
              AND r.round = (SELECT MAX(round) FROM races WHERE year = {year})
            ORDER BY cs.position ASC
        """
        
        df = pd.read_sql(query, engine)
        
        # 포인트 포맷팅 (0.5점 등 소수점 처리)
        if not df.empty and 'format_points' in globals():
            df['포인트'] = df['포인트'].apply(format_points)
            
        return df
        
    except Exception as e:
        st.error(f"❌ 팀원 DB 연결 실패: {e}")
        return pd.DataFrame()


# 2026 시즌 레이스 일정 (샘플)
RACE_SCHEDULE = [
    {"라운드": 1, "그랑프리": "🇦🇺 호주", "서킷": "Albert Park", "날짜": "2026-03-13", "상태": "완료"},
    {"라운드": 2, "그랑프리": "🇨🇳 중국", "서킷": "Shanghai", "날짜": "2026-03-20", "상태": "완료"},
    {"라운드": 3, "그랑프리": "🇯🇵 일본", "서킷": "Suzuka", "날짜": "2026-03-27", "상태": "완료"},
    {"라운드": 4, "그랑프리": "🇺🇸 마이애미", "서킷": "Miami International", "날짜": "2026-05-01", "상태": "다음 레이스 🔴"},
    {"라운드": 5, "그랑프리": "🇨🇦 캐나다", "서킷": "Circuit Gilles Villeneuve", "날짜": "2026-05-22", "상태": "예정"},
    {"라운드": 6, "그랑프리": "🇲🇨 모나코", "서킷": "Circuit de Monaco", "날짜": "2026-06-05", "상태": "예정"},
    {"라운드": 7, "그랑프리": "🇪🇸 스페인", "서킷": "Circuit de Barcelona", "날짜": "2026-06-19", "상태": "예정"},
    {"라운드": 8, "그랑프리": "🇦🇹 오스트리아", "서킷": "Red Bull Ring", "날짜": "2026-06-26", "상태": "예정"},
    {"라운드": 9, "그랑프리": "🇬🇧 영국", "서킷": "Silverstone", "날짜": "2026-07-03", "상태": "예정"},
    {"라운드": 10, "그랑프리": "🇭🇺 헝가리", "서킷": "Hungaroring", "날짜": "2026-07-24", "상태": "예정"},
]

# 팀 컬러
TEAM_COLORS = {
    "Red Bull Racing": "#3671C6",
    "Red Bull": "#3671C6",
    "Ferrari": "#E8002D",
    "McLaren": "#FF8000",
    "Mercedes": "#27F4D2",
    "Aston Martin": "#358C75",
    "Alpine F1 Team": "#FF87BC",
    "Williams": "#64C4FF",
    "Haas F1 Team": "#B6BABD",
    "Kick Sauber": "#52E252",
    "RB": "#6692FF",
}


# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px;'>
        <span " style='font-size:48px'>🏎️</span>
        <h2 style='color:#E10600; margin:0;'>F1 Dashboard</h2>
        <p style='color:#888; font-size:12px;'>2026 시즌</p>
    </div>
    """, unsafe_allow_html=True)
    
    page = st.selectbox(
        "📍페이지 선택",
        ["🏠 홈", "🏆 드라이버 순위", "🏁 컨스트럭터 순위", "📅 레이스 일정", "📊 통계 분석", "❓ FAQ"]
    )

    st.markdown("---")
    st.markdown("### 🔴 다음 레이스")
    st.markdown("""
    <div style='background:#E10600; border-radius:8px; padding:12px; text-align:center;'>
        <div style='font-size:24px; color : white;'>🇺🇸</div>
        <div style='font-weight:bold; font-size:16px; color : white;'>Miami GP</div>
        <div style='font-size:12px; color:#FFD0D0;'>2026년 5월 1일</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("Data: Ergast Motor Racing API")


# ── 메인 컨텐츠 ─────────────────────────────────────────────

# 🏠 홈
if page == "🏠 홈":
    # 헤더
    st.markdown("""
    <div class='f1-header'>
        <span style='font-size:48px;'>🏎️</span>
        <div>
            <h1 style='margin:0; color:white; font-size:32px;'>FORMULA 1</h1>
            <p style='margin:0; color:#FFD0D0; font-size:14px;'>2026 월드 챔피언십</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 다음 레이스 배너
    st.markdown("""
    <div class='next-race-banner'>
        <p style='color:#FFD0D0; font-size:12px; letter-spacing:3px; margin:0;'>NEXT RACE</p>
        <h2 style='color:white; font-size:28px; margin:8px 0;'>🇺🇸 MIAMI GRAND PRIX</h2>
        <p style='color:#FFD0D0; font-size:16px; margin:0;'>Miami International Autodrome · 2026년 5월 1-3일</p>
        <iframe class="video-wrapper" src="https://www.youtube.com/embed/C3pAE40Fgc0?si=vX-VxgVNa5rRNYfH" allow="autoplay;"></iframe>
    </div>
    """, unsafe_allow_html=True)

    # 주요 지표
    driver_df = get_driver_standings()
    constructor_df = get_constructor_standings()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏆 드라이버 선두", driver_df.iloc[0]["드라이버"].split()[-1], f"{driver_df.iloc[0]['포인트']}pts")
    with col2:
        st.metric("🏁 컨스트럭터 선두", constructor_df.iloc[0]["팀"], f"{constructor_df.iloc[0]['포인트']}pts")
    with col3:
        gap = driver_df.iloc[0]["포인트"] - driver_df.iloc[1]["포인트"]
        st.metric("📊 1-2위 격차", f"{gap} pts", "")
    with col4:
        st.metric("🔢 완료된 레이스", "3 / 24", "라운드")

    st.markdown("---")

    # 상위 5명 드라이버
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown("### 🏆 2026 드라이버 TOP 5")
        top5 = driver_df.head(5)
        for _, row in top5.iterrows():
            color = TEAM_COLORS.get(row["팀"], "#888")
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][row["순위"] - 1]
            st.markdown(f"""
            <a href='https://www.formula1.com/en/drivers/{row['드라이버'].replace(" ", "-").lower()}' style='text-decoration: none; cursor: pointer;'>
            <div class='driver-card' style='border-left-color:{color}; --shadow-color:{color};'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <span style='font-size:20px; margin-right:8px;'>{medal}</span>
                        <strong style='font-size:16px; color: white;'>{row['드라이버']}</strong>
                        <span style='color:#888; font-size:13px; margin-left:8px;'>{row['팀']}</span>
                    </div>
                    <div style='text-align:right;'>
                        <div style='color:{color}; font-size:20px; font-weight:bold;'>{row['포인트']}</div>
                        <div style='color:#888; font-size:11px;'>PTS</div>
                    </div>
                </div>
            </div>
            </a>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown("### 📊 2026 포인트 차트")
        fig = px.bar(
            top5,
            x="드라이버",
            y="포인트",
            color="팀",
            color_discrete_map=TEAM_COLORS,
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(tickangle=-30),
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)


# 🏆 드라이버 순위
elif page == "🏆 드라이버 순위":
    # 포커싱 이동
    def dr_change_driver():
        st.session_state.sel_team = ""
    def dr_change_team():
        st.session_state.search_input = ""

    st.markdown("## 🏆 F1 드라이버 조회")
    df, df_master = load_db_data()

    if df is not None:
        # 세션 상태 초기화
        if "sel_season" not in st.session_state: st.session_state.sel_season = "전체"
        if "search_input" not in st.session_state: st.session_state.search_input = ""
        if "sel_team" not in st.session_state: st.session_state.sel_team = "전체"

        # 필터 레이아웃
        col1, col2, col3 = st.columns([1, 1.5, 1.5])
        with col1:
            sel_season = st.selectbox("📅 시즌", ["전체"] + sorted(df["시즌"].unique().tolist(), reverse=True), key="sel_season")
        with col2:
            search_name = st.text_input("👤 드라이버 이름 검색", key="search_input", on_change=dr_change_driver).strip()
        with col3:
            teams = ["전체"] + sorted([str(t) for t in df["팀"].unique() if t is not None])
            sel_team = st.selectbox("🏎️ 팀 선택", teams, key="sel_team", on_change=dr_change_team)

        # 버튼 레이아웃
        btn_col1, btn_col2, _ = st.columns([1, 1, 5])
        with btn_col1:
            search_clicked = st.button("🔍 조회하기", use_container_width=True)
        with btn_col2:
            if st.button("🔄 초기화", use_container_width=True):
                for key in ["sel_season", "search_input", "sel_team", "filtered_df"]:
                    if key in st.session_state: del st.session_state[key]
                st.rerun()

        # 필터링 로직
        if 'filtered_df' not in st.session_state or search_clicked:
            f_df = df.copy()
            if st.session_state.sel_season != "전체": f_df = f_df[f_df["시즌"] == st.session_state.sel_season]
            if st.session_state.sel_team != "전체": f_df = f_df[f_df["팀"] == st.session_state.sel_team]
            if st.session_state.search_input: f_df = f_df[f_df["드라이버"].str.contains(st.session_state.search_input, case=False)]
            st.session_state.filtered_df = f_df.sort_values(["시즌", "순위"], ascending=[False, True])

        res_df = st.session_state.filtered_df
        if not res_df.empty:
            st.success(f"검색 결과: {len(res_df)}건")
            st.dataframe(res_df.style.format({"포인트": "{:.2f}"}).background_gradient(subset=["포인트"], cmap="Reds"), use_container_width=True, hide_index=True)
            
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### 🌍 전체 드라이버 국적 분포")
                nat_counts = df_master['nationality'].value_counts().reset_index()
                nat_counts.columns = ['국적', '인원수']
                st.plotly_chart(px.bar(nat_counts.head(10), x='국적', y='인원수', template="plotly_dark", color_discrete_sequence=['#FF4444'], text='인원수'), use_container_width=True)
            with c2:
                st.markdown("##### 🔝 현재 리스트 포인트 ")
                top_10 = res_df.sort_values('포인트', ascending=False).head(10)
                fig = px.bar(top_10, x='포인트', y='드라이버', orientation='h', 
                             template="plotly_dark", 
                             color='포인트', 
                             color_continuous_scale='Reds', 
                             text='포인트')
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("조건에 맞는 드라이버가 없습니다.")

   
# 🏁 컨스트럭터 순위
elif page == "🏁 컨스트럭터 순위":
    
    # 1. 제목과 드롭다운 배치 (기존 코드 활용)
    col_title, col_select = st.columns([3, 1])
    with col_title:
        st.markdown("## 🏁 컨스트럭터 챔피언십")
    with col_select:
        year_list = list(range(2026, 1949, -1))
        selected_year = st.selectbox("시즌 선택", year_list, label_visibility="collapsed")
    
    # 2. ✅ 팀원의 MySQL DB에서 데이터 불러오기!
    df = get_constructor_standings_from_mysql(selected_year)

    if df.empty:
        st.warning(f"데이터베이스에 {selected_year}년 자료가 없거나 연결이 원활하지 않아.")
    else:
        # 3. 불러온 데이터로 표와 차트 그리기 (기존 Plotly 코드 그대로 사용)
        st.dataframe(
            df.style.background_gradient(subset=["포인트"], cmap="Reds"),
            use_container_width=True,
            hide_index=True,
        )
        
        # 파이 차트와 바 차트 그리기
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🍕 포인트 점유율")
            fig = px.pie(
                df.head(8),
                names="팀",
                values="포인트",
                color="팀",
                color_discrete_map=TEAM_COLORS,
                template="plotly_dark",
                hole=0.4,
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### 📊 팀별 포인트")
            fig = px.bar(
                df,
                x="포인트",
                y="팀",
                color="팀",
                color_discrete_map=TEAM_COLORS,
                orientation="h",
                template="plotly_dark",
                text="포인트",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                yaxis={"categoryorder": "total ascending"},
            )
            st.plotly_chart(fig, use_container_width=True)

# 📅 레이스 일정
elif page == "📅 레이스 일정":
    st.markdown("## 📅 F1 레이스 일정")

    # ─────────────────────────────────────────────────────────
    # 연도별 레이스 일정을 API에서 가져오는 함수
    # @st.cache_data → 같은 연도는 다시 불러오지 않고 저장
    # ─────────────────────────────────────────────────────────
    @st.cache_data(ttl=3600)
    def get_schedule(year):
        """Jolpica API에서 특정 연도의 레이스 일정을 가져옵니다."""
        try:
            url = f"https://api.jolpi.ca/ergast/f1/{year}.json" # url에 년도를 넣어서 API 호출
            response = requests.get(url, timeout=10)            # 10초 동안 응답없으면 실패

            if response.status_code != 200:                     # 응답이 200(정상) 이 아니면 
                return pd.DataFrame()                           # DataFrame 반환

            data = response.json()                                                  # API는 JSON 형태로 데이터 줌
            races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])    # Races 안에 경기 리스트 있음 get이 키 없어도 안전 하게 접근

            if not races:
                return pd.DataFrame()      # 레이스 정보 없으면 빈 표 반환

            rows = []
            for race in races:                                                              # 레이스 정보를 하나 씩 꺼내서 딕셔너리 형태 리스트로 반환
                rows.append({
                    "라운드": int(race.get("round", 0)),
                    "그랑프리": race.get("raceName", ""),
                    "나라": race.get("Circuit", {}).get("Location", {}).get("country", ""),
                    "도시": race.get("Circuit", {}).get("Location", {}).get("locality", ""),
                    "서킷": race.get("Circuit", {}).get("circuitName", ""),
                    "날짜": race.get("date", ""),
                })

            return pd.DataFrame(rows)

        except Exception as e:                      # api 오류가 난다면 api 오류 메시지 출력
            print(f"레이스 일정 API 오류: {e}")
            return pd.DataFrame()

    # ─────────────────────────────────────────────────────────
    # 연도 선택 드롭다운 (2026 ~ 1950)
    # list(range(2026, 1949, -1)) → [2026, 2025, 2024, ..., 1950]
    # ─────────────────────────────────────────────────────────
    연도_목록 = list(range(2026, 1949, -1))  # 2026부터 1950까지 숫자 목록 만들기

    선택_연도 = st.selectbox(
        "📅 연도를 선택하세요",
        options=연도_목록,   # 드롭다운에 보여줄 목록
        index=0,             # 기본값: 첫 번째 항목 (2026)
    )

    # ─────────────────────────────────────────────────────────
    # 선택한 연도의 데이터 불러오기
    # ─────────────────────────────────────────────────────────
    with st.spinner(f"⏳ {선택_연도}년 일정을 불러오는 중..."): # {선택_연도} 일정을 불러오는 동안 로딩 표시를 띄우고, 그 작업 결과를 schedule_df에 저장한다
        schedule_df = get_schedule(선택_연도)

    # 데이터가 없으면 안내 메시지 표시
    if schedule_df.empty:       
        st.warning(f"⚠️ {선택_연도}년 데이터를 불러올 수 없어요. 잠시 후 다시 시도해주세요.")   # 데이터가 비어 있다면 {선택_연도} 데이터를 불러 올 수 있다는 메시지를 표시 한다.

    else:
        # ─────────────────────────────────────────────────────
        # 오늘 날짜 기준으로 상태 자동 계산
        # ─────────────────────────────────────────────────────
        from datetime import date

        오늘 = date.today()  # 오늘 날짜

        # 각 레이스가 완료됐는지, 다음인지, 예정인지 자동으로 판단
        상태_목록 = []
        다음레이스_찾음 = False  # 다음 레이스를 아직 못 찾은 상태

        for _, row in schedule_df.iterrows(): # schedule_df의 각 행을 하나씩 꺼내서 index는 버리고, 행 데이터만 row로 사용한다 ('_' 는 인덱스를 무시한 다는 의미)
            레이스날짜 = date.fromisoformat(row["날짜"])  # 문자열 → 날짜로 변환

            if 레이스날짜 < 오늘:                     # 레이스 날짜를 오늘과 비교한다 
                상태_목록.append("✅ 완료")          # 오늘보다 이전 = 완료
            elif not 다음레이스_찾음:                 # 아직 "다음 레이스"를 안 찾았다면 이걸 다음 레이스로 지정
                상태_목록.append("🔴 다음 레이스")    # 처음 만나는 미래 날짜 = 다음 레이스
                다음레이스_찾음 = True
            else:
                상태_목록.append("🔘 예정")            # 그 이후 = 예정 (다음 레이스 하나가 선택 되면 나머지는 모두 예정)

        schedule_df["상태"] = 상태_목록  # 표에 상태 컬럼 추가 (만들어둔 상태 리스트를 DataFrame의 "상태" 컬럼으로 추가)

        # ─────────────────────────────────────────────────────
        # 통계 요약 숫자 (상단에 크게 표시)
        # ─────────────────────────────────────────────────────
        전체 = len(schedule_df)                                     # DataFrame 행 개수 = 전체 레이스 수
        완료수 = schedule_df["상태"].str.contains("완료").sum()      # 상태 컬럼에서 완료 라는 글자를 찾아서 그 개수를 센다
        예정수 = schedule_df["상태"].str.contains("예정").sum()      # 상태 컬럼에서 예정이라는 글자를 찾아서 그 개수를 센다

        col1, col2, col3 = st.columns(3)                            # 한 행을 3개의 열로 나눈다
        with col1:
            st.metric("🏁 전체 레이스", f"{전체}개")                # st.metric(가독성 높은 형태로 보여준다) , 전체 개수를 가져와 보여준다
        with col2:
            st.metric("✅ 완료", f"{완료수}개")                     # st.metric(가독성 높은 형태로 보여준다) , 완료수 개수를 가져와 보여준다
        with col3:
            st.metric("🔘 남은 레이스", f"{예정수}개")              # st.metric(가독성 높은 형태로 보여준다) , 예정수 개수를 가져와 보여준다

        st.divider()                                                # 화면에 구분선을 보여준다 (배경이 검은색이라서 보이지 않음)

        # ─────────────────────────────────────────────────────
        # 다음 레이스 강조 배너 (해당 연도에 다음 레이스가 있을 때만 표시)
        # ─────────────────────────────────────────────────────
        다음레이스_df = schedule_df[schedule_df["상태"] == "🔴 다음 레이스"] # 상태 컬럼에서 "🔴 다음 레이스"인 행만 골라서 다음레이스_df 생성

        if not 다음레이스_df.empty: # 비어있지 않으면 (즉, 다음 레이스가 있으면) 실행, 없으면 아무 것도 안함
            r = 다음레이스_df.iloc[0]  # 다음 레이스는 하나 밖에 없으니 첫 번째 행 꺼내기
            st.markdown(f"""
            <div class='next-race-banner'>
                <p style='color:#FFD0D0; font-size:12px; letter-spacing:3px; margin:0;'>NEXT RACE</p> 
                <h2 style='color:white; font-size:26px; margin:8px 0;'>🏎️ {r['그랑프리']}</h2>
                <p style='color:#FFD0D0; font-size:15px; margin:0;'>
                    📍 {r['도시']}, {r['나라']} &nbsp;|&nbsp; 🏟️ {r['서킷']} &nbsp;|&nbsp; 📅 {r['날짜']}
                </p>
            </div>
            """, unsafe_allow_html=True)    # HTML 태그 사용 허용 없으면 그냥 문자로 출력 됨
             # 배너 박스 (CSS 스타일 적용용)
             # 첫 째 줄에 'NEXT RACE'
             # 둘 째 줄에 그랑프리 이름
             # 셋 째 줄에 도시, 나라, 서킷, 날짜 
            st.write("")  # 여백

        # ─────────────────────────────────────────────────────
        # 레이스 목록 표 출력
        # ─────────────────────────────────────────────────────
        st.subheader(f"📋 {선택_연도}년 전체 일정")

        # 행마다 색깔을 다르게 칠해주는 함수
        def 색깔_적용(row):
            if "완료" in row["상태"]:
                return ["background-color: #1a3a2a; color: #4CAF50"] * len(row)  # 상태가 완료 라면 배경 색이 초록 색
            elif "다음" in row["상태"]:
                return ["background-color: #3a1a1a; color: #E10600"] * len(row)  # 상태가 다음이라면 배경 색이 빨강 색
            else:
                return ["color: #888888"] * len(row)  # 회색

        # 표 출력 (색깔 적용)
        st.dataframe(
            schedule_df.style.apply(색깔_적용, axis=1),
            use_container_width=True,   # 화면 너비에 꽉 맞게
            hide_index=True,            # 왼쪽 숫자 인덱스 숨기기
            height=560,                 # 표 높이
        )

        st.caption("📌 날짜 기준은 레이스 당일 입니다")


# 📊 통계 분석 by. 김동민
elif page == "📊 통계 분석":
    st.markdown("## 📊 시즌별 통계")
    def state_reset():
        st.session_state.dbut_active = {}
        st.session_state.tbut_active = {}
    if 'dbut_active' not in st.session_state:
        st.session_state.dbut_active = {}
    if 'tbut_active' not in st.session_state:
        st.session_state.tbut_active = {}

    stat_col1, stat_col2 = st.columns([3, 1])
    stat_years_list = list(range(nowyears, 1949, -1))
    stat_years_list.insert(0, "전체")
    with stat_col1:
        tab1, tab2 = st.tabs(["드라이버 통계", "팀 통계"])
    with stat_col2:
        stat_years = st.selectbox("", stat_years_list, index=1, label_visibility="collapsed", on_change=state_reset)
    driver_df = None
    constructor_df = None
    # 연도별 보기와 전체 기간 보기. 
    # 전체기간 보기면 선수 이름 기준, 승점과 포인트를 합쳐서 보여준다
    spec_driver_all_df = get_driver_standings_all()
    spec_constructor_all_df = get_driver_standings_all()
    if stat_years != "전체":
        driver_df = get_driver_standings_year(stat_years)
        constructor_df = get_constructor_standings_year(stat_years)
    else:
        driver_df = get_driver_standings_all()
        constructor_df = get_constructor_standings_all()
        # 이름 기준으로 포인트, 승수는 더하고, 국적과 팀은 마지막 정보 사용.
        stats_df = driver_df.groupby('드라이버')[['포인트', '승수']].sum().reset_index()
        info_df = driver_df.groupby('드라이버')[['순위', '국적', '팀']].last().reset_index()
        driver_df = pd.merge(stats_df, info_df, on='드라이버')

        con_stats_df = constructor_df.groupby('팀')[['포인트', '승수']].sum().reset_index()
        con_info_df = constructor_df.groupby('팀')[['순위']].last().reset_index()
        constructor_df = pd.merge(con_stats_df, con_info_df, on='팀').sort_values(by='포인트', ascending=False)
    with tab1:
        with st.spinner("Loading..."):
            st.markdown(f"### {stat_years}시즌 포인트 vs 승수 산점도")
            fig = px.scatter(
                driver_df,
                x="포인트",
                y="승수",
                color="팀",
                size="포인트",
                hover_name="드라이버",
                color_discrete_map=TEAM_COLORS,
                template="plotly_dark"
            )
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(30,30,46,0.5)")
            fig.update_traces(textposition="top center", textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🏆 TOP 10 드라이버")
        top5 = driver_df.sort_values(by='포인트', ascending=False).reset_index().head(10)
        def change_status(dname):
            cur_state = st.session_state.dbut_active.get(f"dbut_{dname}", False)
            st.session_state.dbut_active[f"dbut_{dname}"] = not cur_state
        for rank , row in top5.iterrows():
            color = TEAM_COLORS.get(row["팀"], "#888")
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"][rank]
            # 키 값으로 공백이나 특수문자를 인식할 수 없으므로 제거한다.
            dname = "".join(filter(str.isalnum, row['드라이버']))
            but_css= f"""
                .driver-card {{
                    background: linear-gradient(145deg, #1E1E2E, #2E2E3E);
                    border-left: 4px solid #E10600;
                    border-radius: 8px;
                    padding: 16px;
                    margin: 8px 0;
                    transition: all 0.2s ease 0s;
                    --shadow-ox: 0px;
                    --shadow-oy: 0px;
                    --shadow-blur: 0px;
                    --shadow-color: #000000;
                    box-shadow: var(--shadow-ox) var(--shadow-oy) var(--shadow-blur) var(--shadow-color);
                }}
                .driver-card:hover{{
                    border-left-width: 12px;
                    filter: brightness(110%);
                    --shadow-blur: 10px;
                }}
                .driver-card .notice{{
                    text-align: center;
                    font-size: 10px;
                    color: #dddddd;
                    display: block;
                    margin: auto;
                    height: 0px;
                    opacity : 0;
                    transition: all 0.2s ease 0s;
                }}
                .driver-card:hover .notice{{
                    height: 4px;
                    opacity: 1;
                }}
                .driver-card:active {{
                    filter: brightness(180%);
                }}
            """
            but_html = f"""
                <div class='driver-card' id='dcard-{dname}' style='border-left-color:{color}; --shadow-color:{color}; cursor : pointer;'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <span style='font-size:20px; margin-right:8px;'>{medal}</span>
                            <strong style='font-size:16px;'>{row['드라이버']}</strong>
                            <span style='color:#888; font-size:13px; margin-left:8px;'>{row['팀']}</span>
                        </div>
                        <div style='text-align:right;position:absolute; right: 20%;'>
                            <div style='color:{color}; font-size:20px; font-weight:bold;'>{row['승수']}</div>
                            <div style='color:#888; font-size:11px;'>WINS</div>
                        </div>
                        <div style='text-align:right;'>
                            <div style='color:{color}; font-size:20px; font-weight:bold;'>{row['포인트']}</div>
                            <div style='color:#888; font-size:11px;'>PTS</div>
                        </div>
                    </div>
                    <span class='notice'>연도별 승점 열람</span>
                </div>
                """
            but_js = f"""
                export default function(component) {{
                    const {{ setTriggerValue, parentElement }} = component;
                    const btn = parentElement.querySelector('#dcard-{dname}');
                    btn.onclick = () => {{
                        // 파이썬 쪽으로 'clicked'라는 이름의 신호(true)를 쏩니다!
                        // streamlit은 상태의 '변화'만을 인지하므로, 현재 시간을 보내서 계속 다른 값을 보내도록함
                        setTriggerValue('clicked', Date.now()); 
                    }};
            }}
            """
            # 이름이 같은 but_comp간의 충돌을 막기 위해 이름에 연도를 추가로 붙여준다
            but_comp = st.components.v2.component(f"dbut_{stat_years}_{dname}" ,css=but_css, html=but_html, js=but_js)
            res = but_comp(on_clicked_change=lambda x=dname: change_status(x))
            if st.session_state.dbut_active.get(f"dbut_{dname}", False):
                with st.spinner(f"🏎️loading..."):
                    with st.container():
                        st.markdown(f"<span style='color:white; font-size:16px; text-align:right; margin-right: 16px;'> 📉 연도별 포인트 획득</span><span style='color:white; font-size:16px; text-align:right; margin-right: 16px;'>|</span><span style='color:white; font-size:16px; color:{color};'>{row['드라이버']}</span>", unsafe_allow_html=True)
                        spec_driver_df = spec_driver_all_df[spec_driver_all_df["드라이버"]==row["드라이버"]]
                        st.line_chart(
                            spec_driver_df,
                            x='연도',
                            y='포인트',
                            color=color
                        )


    with tab2:
        with st.spinner("Loading..."):
            st.markdown(f"### {stat_years}시즌 팀 포인트 비교")
            fig = go.Figure(data=[
                go.Bar(
                    name="포인트",
                    x=constructor_df["팀"],
                    y=constructor_df["포인트"],
                    marker_color=[TEAM_COLORS.get(t, "#888") for t in constructor_df["팀"]],
                )
            ])
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(30,30,46,0.5)",
                xaxis_tickangle=-30,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🏆 TOP 10 팀")
        
        top5 = constructor_df.sort_values(by='포인트', ascending=False).reset_index().head(10)

        def tchange_status(tname):
            cur_state = st.session_state.tbut_active.get(f"tbut_{tname}", False)
            st.session_state.tbut_active[f"tbut_{tname}"] = not cur_state
        for rank , row in top5.iterrows():
            color = TEAM_COLORS.get(row["팀"], "#888")
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"][rank]
            # 키 값으로 공백이나 특수문자를 인식할 수 없으므로 제거한다.
            tname = "".join(filter(str.isalnum, row['팀']))
            but_css= f"""
                .driver-card {{
                    background: linear-gradient(145deg, #1E1E2E, #2E2E3E);
                    border-left: 4px solid #E10600;
                    border-radius: 8px;
                    padding: 16px;
                    margin: 8px 0;
                    transition: all 0.2s ease 0s;
                    --shadow-ox: 0px;
                    --shadow-oy: 0px;
                    --shadow-blur: 0px;
                    --shadow-color: #000000;
                    box-shadow: var(--shadow-ox) var(--shadow-oy) var(--shadow-blur) var(--shadow-color);
                }}
                .driver-card:hover{{
                    border-left-width: 12px;
                    filter: brightness(110%);
                    --shadow-blur: 10px;
                }}
                .driver-card:active {{
                    filter: brightness(180%); 
                }}
                .driver-card .notice{{
                    text-align: center;
                    font-size: 10px;
                    color: #dddddd;
                    display: block;
                    margin: auto;
                    height: 0px;
                    opacity : 0;
                    transition: all 0.2s ease 0s;
                }}
                .driver-card:hover .notice{{
                    height: 4px;
                    opacity: 1;
                }}
            """
            but_html = f"""
                <div class='driver-card' id='tcard-{tname}'style='border-left-color:{color}; --shadow-color:{color};'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <div>
                            <span style='font-size:20px; margin-right:8px;'>{medal}</span>
                            <strong style='font-size:16px;'>{row['팀']}</strong>
                        </div>
                        <div style='text-align:right;position:absolute; right: 20%;'>
                            <div style='color:{color}; font-size:20px; font-weight:bold;'>{row['승수']}</div>
                            <div style='color:#888; font-size:11px;'>WINS</div>
                        </div>
                        <div style='text-align:right;'>
                            <div style='color:{color}; font-size:20px; font-weight:bold;'>{row['포인트']}</div>
                            <div style='color:#888; font-size:11px;'>PTS</div>
                        </div>
                    </div>
                    <span class='notice'>연도별 승점 열람</span>
                </div>
                """
            but_js = f"""
                export default function(component) {{
                    const {{ setTriggerValue, parentElement }} = component;
                    const btn = parentElement.querySelector('#tcard-{tname}');
                    btn.onclick = () => {{
                        // 파이썬 쪽으로 'clicked'라는 이름의 신호(true)를 쏩니다!
                        // streamlit은 상태의 '변화'만을 인지하므로, 현재 시간을 보내서 계속 다른 값을 보내도록함
                        setTriggerValue('clicked', Date.now()); 
                    }};
            }}
            """
            # 이름이 같은 but_comp간의 충돌을 막기 위해 이름에 연도를 추가로 붙여준다
            but_comp = st.components.v2.component(f"tbut_{stat_years}_{tname}" ,css=but_css, html=but_html, js=but_js)
            res = but_comp(on_clicked_change=lambda x=tname: tchange_status(x))
            if st.session_state.tbut_active.get(f"tbut_{tname}", False):
                with st.spinner(f"🏎️loading..."):
                    with st.container():
                        st.markdown(f"<span style='color:white; font-size:16px; text-align:right; margin-right: 16px;'> 📉 연도별 포인트 획득</span><span style='color:white; font-size:16px; text-align:right; margin-right: 16px;'>|</span><span style='color:white; font-size:16px; color:{color};'>{row['팀']}</span>", unsafe_allow_html=True)
                        spec_constructor_df = spec_constructor_all_df[spec_constructor_all_df["팀"]==row["팀"]]
                        st.line_chart(
                            spec_constructor_df,
                            x='연도',
                            y='포인트',
                            color=color
                        )





        
            
# ❓ 자주 묻는 질문 (FAQ) 페이지
elif page == "❓ FAQ":
    # 헤더 디자인
    st.markdown("""
    <div class='f1-header'>
        <span style='font-size:48px;'>❓</span>
        <div>
            <h1 style='margin:0; color:white; font-size:32px;'>FAQ</h1>
            <p style='margin:0; color:#FFD0D0; font-size:14px;'>F1에 대해 자주 묻는 질문들을 모았습니다.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.info("💡 궁금한 질문을 클릭하면 답변을 확인하실 수 있습니다.")
    st.markdown("---")

    # 10가지 질문과 답변 (확장 패널 형태)
    with st.expander("1. F1에서 '컨스트럭터(Constructor)'란 무엇인가요?"):
        st.write("단순히 레이싱카를 운전하는 팀이 아니라, F1 규정에 맞춰 차량의 섀시(차체)를 직접 설계하고 제작하는 팀(제조사)을 뜻합니다. (예: 페라리, 메르세데스, 레드불)")

    with st.expander("2. DRS가 무엇인가요?"):
        st.write("Drag Reduction System의 약자입니다. 앞차와의 간격이 1초 이내일 때 리어 윙(뒷날개)을 열어 공기 저항을 줄이고, 직선 구간 속도를 극대화하여 추월을 돕는 시스템입니다.")

    with st.expander("3. 타이어 색깔(빨강, 노랑, 하양)은 무슨 뜻인가요?"):
        st.write("타이어의 '컴파운드(단단함 정도)'를 나타냅니다. \n* **빨간색(소프트):** 가장 빠르지만 빨리 닳습니다.\n* **노란색(미디엄):** 속도와 내구성의 균형이 좋습니다.\n* **하얀색(하드):** 속도는 제일 느리지만 가장 오래 버팁니다.")

    with st.expander("4. 피트 스탑(Pit Stop)에서는 주로 무엇을 하나요?"):
        st.write("마모된 타이어를 새것으로 교체하고, 차량의 앞날개 각도를 조절하거나 파손된 부품을 빠르게 교체합니다. 현재 F1 규정상 경기 중 주유는 금지되어 있어 보통 2~3초 만에 타이어 교체가 끝납니다!")

    with st.expander("5. 해일로(Halo)는 어떤 장치인가요?"):
        st.write("드라이버의 머리를 보호하기 위해 조종석(콕핏) 위에 설치된 Y자 형태의 티타늄 보호대입니다. 대형 사고 시 외부 파편이나 충격으로부터 드라이버의 생명을 구하는 핵심 장치입니다.")

    with st.expander("6. F1 차량의 최고 속도는 얼마나 되나요?"):
        st.write("직선 구간에서 시속 약 350km ~ 370km까지 올라갑니다. 코너링 시에는 전투기 조종사가 겪는 것과 비슷한 4~6G의 엄청난 중력 가속도를 견뎌야 합니다.")

    with st.expander("7. 폴 포지션(Pole Position)이 무슨 뜻인가요?"):
        st.write("본 경기 전날 열리는 예선전(Qualifying)에서 랩타임 1위를 차지해, 본선 레이스 출발선 맨 앞자리(1번 그리드)에서 출발하는 유리한 권리를 말합니다.")

    with st.expander("8. 경기 중 흔드는 깃발 색깔은 어떤 의미인가요?"):
        st.write("* **노란 깃발:** 앞쪽에 위험 상황 발생 (추월 금지 및 감속)\n* **빨간 깃발:** 심각한 사고로 경기 중단\n* **파란 깃발:** 뒤에 빠른 차가 오고 있으니 양보하라는 의미 (주로 랩 타임이 뒤처진 차량에게 줌)\n* **체커기:** 경기 종료")

    with st.expander("9. 챔피언십 포인트는 몇 등까지 받나요?"):
        st.write("본선 레이스 기준 1등(25점)부터 10등(1점)까지 포인트를 받습니다. 또한 가장 빠른 랩타임(Fastest Lap)을 기록한 드라이버가 10위권 내에 있다면 1점의 보너스 포인트를 추가로 받습니다.")

    with st.expander("10. 스프린트(Sprint) 레이스란 무엇인가요?"):
        st.write("일반적인 본선 레이스 거리의 약 1/3 (약 100km)만 달리는 짧고 빠른 미니 레이스입니다. 피트 스탑 의무가 없어 처음부터 끝까지 전속력으로 달리며, 상위 8명에게 추가 포인트를 줍니다.")

    st.markdown("---")
    st.caption("감사합니다 2팀이었습니다.!")
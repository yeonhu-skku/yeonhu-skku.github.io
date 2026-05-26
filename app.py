import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. Page Configuration (High-aesthetic Minimal tone)
st.set_page_config(
    page_title="Run-Step: Running Course Recommendation",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Custom High-Aesthetic CSS (Minimal Cream, Soft Shadows, and Glassmorphic Player Card)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #F7F4EB;
        color: #242220;
        font-family: 'Inter', sans-serif;
    }
    /* Dynamic Typography Polish */
    h1, h2, h3, h4, h5, h6 {
        color: #1A1918 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    div.stButton > button:first-child {
        background-color: #242220;
        color: #F7F4EB;
        border-radius: 24px;
        padding: 12px 32px;
        font-weight: 600;
        border: none;
        letter-spacing: -0.01em;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #D45134; /* Elegant terracotta orange point color */
        color: #F7F4EB;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(212,81,52,0.25);
    }
    /* Streamlit Tab Customization for High Sensitivity Vibe */
    div.stTabs [data-baseweb="tab"] {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #7A756E !important;
        padding: 12px 20px !important;
        border-bottom: 2px solid transparent !important;
    }
    div.stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #D45134 !important;
        border-bottom: 2px solid #D45134 !important;
    }
    /* Music Streaming Style Glassmorphic Player Box */
    .player-row {
        display: flex;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        border-radius: 16px;
        padding: 14px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 18px rgba(36,34,32,0.02);
        border: 1px solid rgba(239, 236, 230, 0.8);
        transition: all 0.25s ease;
    }
    .player-row:hover {
        transform: scale(1.005);
        background-color: rgba(255, 255, 255, 0.98);
        box-shadow: 0 6px 24px rgba(36,34,32,0.05);
    }
    /* Highly-Stable Embedded SVG Icon Cover to Prevent Broken Image Links */
    .player-icon-box {
        width: 55px;
        height: 55px;
        background-color: #242220;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .player-info {
        flex-grow: 1;
    }
    .player-title {
        font-size: 16px;
        font-weight: 600;
        color: #242220;
        margin-bottom: 3px;
    }
    .player-artist {
        font-size: 13px;
        color: #7A756E;
        font-weight: 500;
    }
    .play-btn {
        background-color: #242220;
        color: #F7F4EB !important;
        padding: 8px 18px;
        border-radius: 30px;
        text-decoration: none;
        font-size: 13px;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .play-btn:hover {
        background-color: #D45134;
        box-shadow: 0 4px 12px rgba(212,81,52,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# 2. Initialize Session State for Multi-step Navigation
if "page_stage" not in st.session_state:
    st.session_state.page_stage = "welcome"
if "user_level" not in st.session_state:
    st.session_state.user_level = "Beginner"

# 3. Dataset Setup with Verified Hotspots, Links, and Track Metadata
@st.cache_data
def load_course_data():
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["여의도 한강공원", "석촌호수", "동네 근린공원", 
                       "남산 둘레길", "양재천", "북서울꿈의숲", 
                       "인왕산", "뚝섬 한강공원", "부암동"],
        "Distance_KM": [3.0, 2.5, 2.0, 7.0, 8.5, 5.0, 12.0, 21.0, 15.0],
        "Elevation_Desc": ["Flat (Very Low)", "Flat (Low)", "Flat (Low)", "Sloped (Medium)", "Moderate (Medium)", "Steep (Medium-High)", "Rugged (High)", "Varied (High)", "Very Steep (Extreme)"],
        "Pros": [
            "The terrain is exceptionally flat with refreshing riverside breezes and excellent public convenience facilities.", 
            "It is highly optimized for maintaining a steady running pace, offering a spectacular night view of the Lotte World Tower.", 
            "Extremely accessible for a light, secure daily jog with well-lit street lamps and safe environments.",
            "Features dense tree canopies providing rich shade, keeping the track cool even during daytime hours with beautiful seasonal scenery.", 
            "Completely free of traffic lights, making it the premier choice for long-distance endurance and pace sustainability training.", 
            "Includes short yet high-intensity uphill sections that are ideal for strengthening cardiovascular endurance and anaerobic capacity.",
            "Delivers an immersive, dynamic trail running experience within the city center, ensuring an engaging workout without monotony.", 
            "Closely replicates actual marathon course conditions, serving as an excellent track for pre-race strategic pacing checks.", 
            "Demands extreme physical exertion; highly effective for testing anaerobic thresholds and building maximum lower-body strength."
        ],
        "Cons": [
            "High volume of bicycle traffic requires runners to remain highly alert; reducing earphone volume is strongly recommended.", 
            "Heavy pedestrian crowds during weekend evenings can significantly restrict continuous overtaking or fast-paced running.", 
            "The total distance per loop is relatively short, which may cause the session to feel slightly repetitive.",
            "Contains multiple steep segments that trigger sudden heart rate elevation; careful pace distribution is vital to prevent overexertion.", 
            "Lacks sufficient shade throughout the track, making UV protection and hydration mandatory during daytime workouts.", 
            "The initial incline is steeper than anticipated, necessitating caution to prevent acute knee joint strain.",
            "Constructed with uneven rocky paths and stairs; technical trail running shoes are mandatory to minimize ankle injury risks.", 
            "Given the substantial distance, runners must carefully plan their hydration and energy gel consumption intervals in advance.", 
            "Presents an extreme risk of joint and muscle injury; strictly prohibited for beginners or individuals with joint vulnerabilities."
        ],
        "Map_Center": [
            [37.5289, 126.9331], [37.5074, 127.1031], [37.5145, 127.0607],
            [37.5509, 126.9909], [37.4934, 127.0601], [37.6257, 127.0371],
            [37.5758, 126.9583], [37.5408, 127.0717], [37.5921, 126.9423]
        ],
        
        # --- 2 REAL POST-RUN CAFES & RESTAURANTS PER COURSE ---
        "Spots": [
            # 1. 여의도
            [
                {"name": "세상의모든아침 여의도점", "tags": "#브런치맛집 #양식레스토랑 #초고층호텔뷰 #탄수화물보충", "map": "https://maps.google.com/?q=세상의모든아침+여의도점", "insta": "https://www.instagram.com/all_thats_morning/"},
                {"name": "카페 진정성 여의도점", "tags": "#밀크티맛집 #러닝후당충전 #모던카페 #인스타핫플", "map": "https://maps.google.com/?q=카페+진정성+여의도점", "insta": "https://www.instagram.com/cafe_jinjungsung/"}
            ],
            # 2. 석촌호수
            [
                {"name": "뷰클런즈 (Vrewcleans)", "tags": "#송리단길카페 #힐링우드인테리어 #시원한아이스티 #땀식히기좋은곳", "map": "https://maps.google.com/?q=뷰클런즈", "insta": "https://www.instagram.com/vrewcleans/"},
                {"name": "니커버커베이글 (Knickerbocker Bagel)", "tags": "#베이글맛집 #탄수화물치트키 #뉴욕감성브런치 #호수뷰테라스", "map": "https://maps.google.com/?q=니커버커베이글+송파점", "insta": "https://www.instagram.com/knickerbockerbagel_korea/"}
            ],
            # 3. 동네근린공원
            [
                {"name": "파리바게뜨 로컬 스토어", "tags": "#갓구운샌드위치 #단백질충전 #접근성최고 #가성비브런치", "map": "https://maps.google.com/?q=파리바게뜨", "insta": "https://www.instagram.com/parisbaguette_kr/"},
                {"name": "이디야커피 공원점", "tags": "#시원한엑스트라아메리카노 #초고속수분보충 #가성비러닝스팟", "map": "https://maps.google.com/?q=이디야커피", "insta": "https://www.instagram.com/ediya.coffee/"}
            ],
            # 4. 남산 둘레길
            [
                {"name": "101번지 남산돈까스 본점", "tags": "#남산필수코스 #경양식돈까스 #러너단백질보충 #원조맛집", "map": "https://maps.google.com/?q=101번지+남산돈까스", "insta": "https://www.instagram.com/explore/tags/남산돈까스/"},
                {"name": "이중생업 남산", "tags": "#남산한식퓨전양식 #정갈한파스타 #러닝데이트코스 #깔끔한레스토랑", "map": "https://maps.google.com/?q=이중생업+남산", "insta": "https://www.instagram.com/explore/tags/남산맛집/"}
            ],
            # 5. 양재천
            [
                {"name": "룸서비스301 (Room Service 301)", "tags": "#양재천카페거리 #통창숲뷰 #감성디저트카페 #아이스커피맛집", "map": "https://maps.google.com/?q=룸서비스301", "insta": "https://www.instagram.com/roomservice301/"},
                {"name": "캐틀앤비 (Cattle & Bee)", "tags": "#레이먼킴브런치 #이탈리안양식 #테라스카페 #도곡동맛집", "map": "https://maps.google.com/?q=캐틀앤비+양재점", "insta": "https://www.instagram.com/cattle_bee/"}
            ],
            # 6. 북서울꿈의숲
            [
                {"name": "라포레스타 (La Foresta)", "tags": "#꿈의숲복합레스토랑 #피자파스타맛집 #통창그린뷰 #가족러닝추천", "map": "https://maps.google.com/?q=라포레스타", "insta": "https://www.instagram.com/explore/tags/라포레스타/"},
                {"name": "꿈의숲 미술관 카페", "tags": "#전망대전경카페 #시원한스무디 #문화예술스팟 #하체릴렉스", "map": "https://maps.google.com/?q=북서울꿈의숲", "insta": "https://www.instagram.com/explore/tags/북서울꿈의숲/"}
            ],
            # 7. 인왕산
            [
                {"name": "H라운지 (H Lounge) 서촌", "tags": "#서촌이탈리안양식 #정원테라스 브런치 #인왕산하산푸드 #파스타맛집", "map": "https://maps.google.com/?q=H라운지", "insta": "https://www.instagram.com/explore/tags/서촌브런치/"},
                {"name": "스태픽스 (Staff Picks)", "tags": "#서촌야외테라스 #은행나무맛집 #인스타감성카페 #러너휴식성지", "map": "https://maps.google.com/?q=스태픽스", "insta": "https://www.instagram.com/staffpicks_official/"}
            ],
            # 8. 뚝섬 한강공원
            [
                {"name": "아구아구 (Agu Agu) 뚝섬", "tags": "#프레시샐러드볼 #러너식단일체 #보울양식 #라이트식사", "map": "https://maps.google.com/?q=아구아구+뚝섬", "insta": "https://www.instagram.com/explore/tags/뚝섬맛집/"},
                {"name": "뚝섬한강공원 강변편의점", "tags": "#파워에이드드링킹 #얼음컵보급 #수변광장라면 #러닝피날레", "map": "https://maps.google.com/?q=뚝섬한강공원", "insta": "https://www.instagram.com/explore/tags/뚝섬한강공원/"}
            ],
            # 9. 부암동
            [
                {"name": "클럽에스프레소 (Club Espresso)", "tags": "#부암동터줏대감 #전통드립커피 #러너라이더성지 #아메리카노수분충전", "map": "https://maps.google.com/?q=클럽에스프레소", "insta": "https://www.instagram.com/clubespresso/"},
                {"name": "계열사 (Gyeyalsa)", "tags": "#서울3대치킨 #인왕산업힐보상 #치맥단백질보충 #바삭한후라이드", "map": "https://maps.google.com/?q=계열사+부암동", "insta": "https://www.instagram.com/explore/tags/계열사/"}
            ]
        ],

        "Playlist_Title": [
            "Chill Acoustic & Gentle Breeze Pop", "Trendy City Night Grooves", "Bright Morning Warm-Up Beats",
            "Rhythmic Mid-Tempo Running Hits", "Groovy Bassline Urban Anthems", "High-Stamina Cardio Boosters",
            "High-Octane K-Pop Energy Booster", "Relentless Global Rap Pace Maker", "Ultimate Adrenaline Limit Breaker"
        ],
        "Playlist_Tracks": [
            # Beginner 1
            [
                {"title": "Paris in the Rain", "artist": "Lauv", "link": "https://www.youtube.com/watch?v=kOCkne-Bku4"},
                {"title": "ILYSB", "artist": "LANY", "link": "https://www.youtube.com/watch?v=SSTp0rknOgA"},
                {"title": "Youth", "artist": "Troye Sivan", "link": "https://www.youtube.com/watch?v=XYAghEq5Lfw"}
            ],
            # Beginner 2
            [
                {"title": "Super Far", "artist": "LANY", "link": "https://www.youtube.com/watch?v=B88Zas_DclM"},
                {"title": "Strawberries & Cigarettes", "artist": "Troye Sivan", "link": "https://www.youtube.com/watch?v=Z3LgC8u_R8Y"},
                {"title": "I Like Me Better", "artist": "Lauv", "link": "https://www.youtube.com/watch?v=BcqxLCWn-CE"}
            ],
            # Beginner 3
            [
                {"title": "Feelings", "artist": "Lauv", "link": "https://www.youtube.com/watch?v=421w1jR-SgE"},
                {"title": "Pink Skies", "artist": "LANY", "link": "https://www.youtube.com/watch?v=eE7T_I9vInU"},
                {"title": "Wild", "artist": "Troye Sivan", "link": "https://www.youtube.com/watch?v=fdXNNveYOfU"}
            ],
            # Intermediate 1
            [
                {"title": "Attention", "artist": "Charlie Puth", "link": "https://www.youtube.com/watch?v=nfs8NYg7yQM"},
                {"title": "Shivers", "artist": "Ed Sheeran", "link": "https://www.youtube.com/watch?v=Il0S8BoucSA"},
                {"title": "Light Switch", "artist": "Charlie Puth", "link": "https://www.youtube.com/watch?v=WFsAon_TWPQ"}
            ],
            # Intermediate 2
            [
                {"title": "How Long", "artist": "Charlie Puth", "link": "https://www.youtube.com/watch?v=TdylllyoV9c"},
                {"title": "Unholy", "artist": "Sam Smith", "link": "https://www.youtube.com/watch?v=Uq9gPaizbe8"},
                {"title": "Bad Habits", "artist": "Ed Sheeran", "link": "https://www.youtube.com/watch?v=orJSJGHjBLI"}
            ],
            # Intermediate 3
            [
                {"title": "Shape of You", "artist": "Ed Sheeran", "link": "https://www.youtube.com/watch?v=JGwWNGJdvx8"},
                {"title": "Diamonds", "artist": "Sam Smith", "link": "https://www.youtube.com/watch?v=8RvAKRoDB7o"},
                {"title": "Left and Right", "artist": "Charlie Puth (feat. Jungkook)", "link": "https://www.youtube.com/watch?v=a7GITgqwDVg"}
            ],
            # Advanced 1
            [
                {"title": "Dynamite", "artist": "BTS", "link": "https://www.youtube.com/watch?v=gdZLi9oWNZg"},
                {"title": "Kill This Love", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=2S24-y0Ij3Y"},
                {"title": "HUMBLE.", "artist": "Kendrick Lamar", "link": "https://www.youtube.com/watch?v=tvTRZJ-4EyI"}
            ],
            # Advanced 2
            [
                {"title": "Pink Venom", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=glhXCuM_Y7M"},
                {"title": "SICKO MODE", "artist": "Travis Scott", "link": "https://www.youtube.com/watch?v=d-JBBNg8YKs"},
                {"title": "MIC Drop", "artist": "BTS (Steve Aoki Remix)", "link": "https://www.youtube.com/watch?v=kTlv5_i8ICM"}
            ],
            # Advanced 3
            [
                {"title": "Run BTS", "artist": "BTS", "link": "https://www.youtube.com/watch?v=9tG70B3DLIY"},
                {"title": "How You Like That", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=ioNng23DkIM"},
                {"title": "Lose Yourself", "artist": "Eminem", "link": "https://www.youtube.com/watch?v=_Yhyp_hXnyU"}
            ]
        ]
    }
    return pd.DataFrame(data)

df = load_course_data()

# 4. High-Fidelity Real Geographic Course Trajectories Mapping Function
def get_real_geographic_route(center_lat, center_lng, course_idx):
    points = []
    
    # 1) 여의도 한강공원 (정밀 한강 둔치 러닝 선형 궤적 트랙킹)
    if course_idx == 0:
        raw_coords = [
            [37.5289, 126.9331], [37.5312, 126.9295], [37.5338, 126.9252], 
            [37.5360, 126.9210], [37.5342, 126.9185], [37.5315, 126.9220],
            [37.5285, 126.9270], [37.5262, 126.9315], [37.5289, 126.9331]
        ]
        # 여의도는 전 구간 평지 -> All Green (🟢)
        colors = ["#06D6A0"] * len(raw_coords)
        
    # 2) 석촌호수 (호수 둑길의 부드러운 타원형 트랙킹)
    elif course_idx == 1:
        raw_coords = [
            [37.5074, 127.1031], [37.5090, 127.1010], [37.5105, 127.0980],
            [37.5100, 127.0950], [37.5080, 127.0945], [37.5055, 127.0970],
            [37.5050, 127.1010], [37.5065, 127.1040], [37.5074, 127.1031]
        ]
        # 다리 진입부만 미세한 경사 -> 1구간 Yellow (🟡)
        colors = ["#06D6A0"] * 3 + ["#FFD166"] + ["#06D6A0"] * (len(raw_coords) - 4)

    # 4) 남산 둘레길 (구불구불한 등고선 순환 트랙킹)
    elif course_idx == 3:
        raw_coords = [
            [37.5509, 126.9909], [37.5490, 126.9940], [37.5465, 126.9930],
            [37.5440, 126.9890], [37.5460, 126.9830], [37.5495, 126.9810],
            [37.5525, 126.9850], [37.5530, 126.9890], [37.5509, 126.9909]
        ]
        # 오르막 내리막 반복 국면 -> Green, Yellow, Red 골고루 혼합
        colors = ["#06D6A0", "#FFD166", "#E25B3C", "#FFD166", "#06D6A0", "#06D6A0", "#FFD166", "#E25B3C", "#06D6A0"]

    # 5) 양재천 (탄천을 향해 곧게 뻗은 하천 직선 궤적)
    elif course_idx == 4:
        raw_coords = [
            [37.4934, 127.0601], [37.4950, 127.0650], [37.4975, 127.0720],
            [37.5002, 127.0790], [37.4990, 127.0810], [37.4960, 127.0740],
            [37.4935, 127.0670], [37.4915, 127.0615], [37.4934, 127.0601]
        ]
        colors = ["#06D6A0"] * len(raw_coords)

    # 6) 북서울꿈의숲 (공원 내부 호수 및 야산 경사로 궤적)
    elif course_idx == 5:
        raw_coords = [
            [37.6257, 127.0371], [37.6235, 127.0395], [37.6210, 127.0410],
            [37.6190, 127.0380], [37.6205, 127.0340], [37.6230, 127.0325],
            [37.6250, 127.0350], [37.6257, 127.0371]
        ]
        # 상단 진입로 가파른 고도 구현 -> Yellow와 Red(🔴) 중심 매핑
        colors = ["#FFD166", "#E25B3C", "#E25B3C", "#FFD166", "#06D6A0", "#06D6A0", "#FFD166", "#FFD166"]

    # 7) 인왕산 트레일러닝 (지그재그 험난한 능선 암벽 등반 패스)
    elif course_idx == 6:
        raw_coords = [
            [37.5758, 126.9583], [37.5785, 126.9550], [37.5810, 126.9535],
            [37.5845, 126.9560], [37.5860, 126.9600], [37.5830, 126.9630],
            [37.5795, 126.9615], [37.5758, 126.9583]
        ]
        # 트레일 하드코어 업힐 지형 -> Red(🔴) 대폭 지배 레이아웃
        colors = ["#FFD166", "#E25B3C", "#E25B3C", "#E25B3C", "#E25B3C", "#FFD166", "#FFD166", "#FFD166"]

    # 그 외 기본 공원 루프 궤적 스케일링
    else:
        raw_coords = [
            [center_lat, center_lng],
            [center_lat + 0.002, center_lng + 0.001],
            [center_lat + 0.003, center_lng + 0.004],
            [center_lat + 0.001, center_lng + 0.005],
            [center_lat - 0.001, center_lng + 0.003],
            [center_lat, center_lng]
        ]
        colors = ["#06D6A0", "#FFD166", "#E25B3C", "#FFD166", "#06D6A0", "#06D6A0"]

    for idx, coord in enumerate(raw_coords):
        points.append({"coord": coord, "color": colors[idx]})
        
    return points

# --- PAGE 1: INTRO WELCOME PAGE ---
if st.session_state.page_stage == "welcome":
    st.title("🏃‍♂️ Run-Step Datahub")
    st.markdown("### Welcome to the Personalized Running Course Recommendation System")
    st.write("Run-Step analyzes your running stamina and target pace to provide optimal running trails across Seoul, complete with real-time terrain difficulty grading and curated lifestyle hotspots.")
    st.markdown("---")
    st.markdown("""
        **Project Metadata:**
        * **Course:** Arts and Big Data (Sungkyunkwan University)
        * **Developer:** Yeonhu Lee (Student ID: 2024314274)
    """)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Get Started"):
        st.session_state.page_stage = "survey"
        st.rerun()

# --- PAGE 2: DIAGNOSTIC SURVEY PAGE ---
elif st.session_state.page_stage == "survey":
    st.title("🏃‍♂️ Run-Step Datahub")
    st.subheader("Analyze Your Running Profile")
    st.write("Please answer two simple questions to unlock your custom running tracks.")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ⏱️ Target Pace")
        user_pace = st.selectbox(
            "What is your average pace per 1 kilometer?", 
            ["Select your pace...", "Over 7 minutes (Slow jog / walk-run)", "5 to 6 minutes (Steady, continuous running)", "Under 4 minutes (Fast pace / competitive racing)"]
        )
    with col2:
        st.markdown("### 👟 Experience")
        user_experience = st.radio(
            "How long have you been consistently running?", 
            ["Less than 1 month (Beginner)", "1 to 6 months (Consistent Runner)", "More than 6 months (Advanced)"]
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("✨ Find My Custom Courses"):
        if user_pace == "Select your pace...":
            st.error("Please select your running pace to proceed!")
        else:
            if user_pace == "Over 7 minutes (Slow jog / walk-run)" or user_experience == "Less than 1 month (Beginner)":
                st.session_state.user_level = "Beginner"
            elif user_pace == "Under 4 minutes (Fast pace / competitive racing)" or user_experience == "More than 6 months (Advanced)":
                st.session_state.user_level = "Advanced"
            else:
                st.session_state.user_level = "Intermediate"
            
            st.session_state.page_stage = "dashboard"
            st.rerun()

# --- PAGE 3: MAIN RECOMMENDATION DASHBOARD ---
else:
    col_back, col_level_select = st.columns([1, 1])
    
    with col_back:
        if st.button("↩️ Re-take Diagnostic Test"):
            st.session_state.page_stage = "welcome"
            st.rerun()
            
    with col_level_select:
        st.session_state.user_level = st.selectbox(
            "🌐 Explore Other Levels Directly:",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.user_level)
        )
        
    st.title("🏃‍♂️ Your Custom Run-Step Dashboard")
    st.markdown(f"The currently selected course difficulty level is **[{st.session_state.user_level}]**.")
    st.markdown("---")
    
    filtered_df = df[df["Level"] == st.session_state.user_level]
    
    tab_names = [f"📌 {row['Course_Name']}" for _, row in filtered_df.iterrows()]
    tabs = st.tabs(tab_names)
    
    def render_course_tab(course_row, internal_idx):
        st.markdown(f"# {course_row['Course_Name']}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(label="Total Distance", value=f"{course_row['Distance_KM']} km")
        c2.metric(label="Incline Elevation", value=course_row['Elevation_Desc'])
        c3.markdown("")
        
        st.success(f"**👍 PROS:** {course_row['Pros']}")
        st.warning(f"**👎 CAUTIONS:** {course_row['Cons']}")
        st.markdown(" ")
        
        # 2) Full Width Map Segment
        st.markdown("#### 🗺️ Route Elevation Visualizer")
        st.caption("🟢 Green: Flat Terrain | 🟡 Yellow: Moderate Incline | 🔴 Red: Steep Incline Section (Drag and zoom to explore)")
        
        # Initialize folium map focusing precisely on target track centers
        m = folium.Map(location=course_row['Map_Center'], zoom_start=15, tiles="CartoDB positron")
        
        # Fetching High-Fidelity Real Terrain Vectors
        route_points = get_real_geographic_route(course_row['Map_Center'][0], course_row['Map_Center'][1], internal_idx)
        for idx in range(len(route_points) - 1):
            p1 = route_points[idx]["coord"]
            p2 = route_points[idx+1]["coord"]
            color_code = route_points[idx]["color"]
            folium.PolyLine(locations=[p1, p2], color=color_code, width=6, opacity=0.9).add_to(m)
        
        folium.Marker(location=course_row['Map_Center'], popup="Start Point", icon=folium.Icon(color="black", icon="play", prefix="fa")).add_to(m)
        st_folium(m, width=1400, height=350, key=f"full_map_{internal_idx}")
        
        st.markdown("---")
        
        # 3) Full Width Post-Run Hotspots
        st.markdown("#### ☕ Post-Run Cafes & Restaurants")
        spot_list = course_row['Spots']
        col_spot1, col_spot2 = st.columns(2)
        
        with col_spot1:
            st.markdown(f"##### 📍 {spot_list[0]['name']}")
            st.caption(spot_list[0]['tags'])
            sc1, sc2 = st.columns(2)
            sc1.link_button("🗺️ View on Google Maps", spot_list[0]['map'])
            sc2.link_button("📸 View on Instagram", spot_list[0]['insta'])
            
        with col_spot2:
            st.markdown(f"##### 📍 {spot_list[1]['name']}")
            st.caption(spot_list[1]['tags'])
            sc3, sc4 = st.columns(2)
            sc3.link_button("🗺️ View on Google Maps", spot_list[1]['map'])
            sc4.link_button("📸 View on Instagram", spot_list[1]['insta'])
            
        st.markdown("---")
        
        # 4) Full Width Custom Music Player Grid
        st.markdown("#### 🎵 Recommended Playlist")
        st.write(f"**Theme: {course_row['Playlist_Title']}**")
        st.caption("Click '▶ Play' to instantly open and stream the track on YouTube.")
        
        for track in course_row['Playlist_Tracks']:
            st.markdown(f"""
                <div class="player-row">
                    <div class="player-icon-box">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 3V13.55C11.41 13.21 10.73 13 10 13C7.79 13 6 14.79 6 17C6 19.21 7.79 21 10 21C12.21 21 14 19.21 14 17V7H18V3H12Z" fill="#F7F4EB"/>
                        </svg>
                    </div>
                    <div class="player-info">
                        <div class="player-title">{track['title']}</div>
                        <div class="player-artist">{track['artist']}</div>
                    </div>
                    <a href="{track['link']}" target="_blank" class="play-btn">▶ Play</a>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown(" ")

    for i, (orig_idx, row) in enumerate(filtered_df.iterrows()):
        with tabs[i]:
            render_course_tab(row, orig_idx)
        
    st.markdown("---")
    st.caption("Run-Step Dashboard v6.4 | Developed by Yeonhu Lee (SKKU Student ID: 2024314274)")

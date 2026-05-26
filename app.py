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
    .player-cover {
        width: 60px;
        height: 60px;
        border-radius: 8px;
        object-fit: cover;
        margin-right: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
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

# 3. Dataset Setup with Verified Dynamic Image Links & Clean Local Core Names
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
        
        # --- 2 REAL HOTSPOTS PER COURSE WITH MAP/INSTA LINKS ---
        "Spots": [
            # 1. 여의도
            [
                {"name": "더현대 서울 (The Hyundai Seoul)", "tags": "#쇼핑몰 #에어컨빵빵 #러닝후구경", "map": "https://maps.google.com/?q=The+Hyundai+Seoul", "insta": "https://www.instagram.com/thehyundai_seoul/"},
                {"name": "여의도 한강공원 배달존", "tags": "#돗자리 #한강라면 #치맥 #러너성지", "map": "https://maps.google.com/?q=Yeouido+Hangang+Park", "insta": "https://www.instagram.com/explore/tags/한강라면/"}
            ],
            # 2. 석촌호수
            [
                {"name": "뷰클런즈 (Vrewcleans)", "tags": "#송리단길 #쉼이있는카페 #나무인테리어", "map": "https://maps.google.com/?q=Vrewcleans", "insta": "https://www.instagram.com/vrewcleans/"},
                {"name": "니커버커베이글 (Knickerbocker Bagel)", "tags": "#웨이팅맛집 #탄수화물보충 #호수뷰", "map": "https://maps.google.com/?q=Knickerbocker+Bagel+Seokchon", "insta": "https://www.instagram.com/knickerbockerbagel_korea/"}
            ],
            # 3. 동네공원
            [
                {"name": "파리바게뜨 로컬 스토어", "tags": "#갓구운빵 #아이스아메리카노 #접근성최고", "map": "https://maps.google.com/?q=Paris+Baguette+Seoul", "insta": "https://www.instagram.com/parisbaguette_kr/"},
                {"name": "이디야커피 공원점", "tags": "#가성비카페 #수분충전 #러닝마무리", "map": "https://maps.google.com/?q=Ediya+Coffee+Seoul", "insta": "https://www.instagram.com/ediya.coffee/"}
            ],
            # 4. 남산
            [
                {"name": "101번지 남산돈까스 본점", "tags": "#단백질보충 #러너필수코스 #원조돈까스", "map": "https://maps.google.com/?q=101+Namsan+Donkatsu", "insta": "https://www.instagram.com/explore/tags/남산돈까스/"},
                {"name": "이중생업 남산", "tags": "#남산감성맛집 #깔끔한한식 #러닝데이트", "map": "https://maps.google.com/?q=Leejungsangeop+Namsan", "insta": "https://www.instagram.com/explore/tags/남산맛집/"}
            ],
            # 5. 양재천
            [
                {"name": "룸서비스301 (Room Service 301)", "tags": "#양재천카페거리 #창가뷰 #숲감성", "map": "https://maps.google.com/?q=Room+Service+301", "insta": "https://www.instagram.com/roomservice301/"},
                {"name": "캐틀앤비 (Cattle & Bee)", "tags": "#테라스카페 #도곡동브런치 #분위기맛집", "map": "https://maps.google.com/?q=Cattle+and+Bee+Dogok", "insta": "https://www.instagram.com/cattle_bee/"}
            ],
            # 6. 북서울꿈의숲
            [
                {"name": "라포레스타 (La Foresta)", "tags": "#꿈의숲일식양식 #통창뷰 #힐링식사", "map": "https://maps.google.com/?q=La+Foresta+Seoul", "insta": "https://www.instagram.com/explore/tags/라포레스타/"},
                {"name": "꿈의숲 미술관 카페", "tags": "#전망좋은곳 #시원한음료 #문화생활", "map": "https://maps.google.com/?q=Dream+Forest+Art+Center", "insta": "https://www.instagram.com/explore/tags/북서울꿈의숲/"}
            ],
            # 7. 인왕산
            [
                {"name": "통인시장 (Tong인 Market)", "tags": "#엽전도시락 #기름떡볶이 #서촌감성", "map": "https://maps.google.com/?q=Tongin+Market", "insta": "https://www.instagram.com/explore/tags/통인시장/"},
                {"name": "스태픽스 (Staff Picks)", "tags": "#서촌야외테라스 #은행나무맛집 #인스타핫플", "map": "https://maps.google.com/?q=Staff+Picks+Seochon", "insta": "https://www.instagram.com/staffpicks_official/"}
            ],
            # 8. 뚝섬 한강공원
            [
                {"name": "아구아구 (Agu Agu) 뚝섬", "tags": "#포크샐러드 #러너식단 #리프레시", "map": "https://maps.google.com/?q=Agu+Agu+Ttukseom", "insta": "https://www.instagram.com/explore/tags/뚝섬맛집/"},
                {"name": "뚝섬한강공원 편의점", "tags": "#파워에이드 #에너지젤보충 #보급기지", "map": "https://maps.google.com/?q=Ttukseom+Hangang+Park", "insta": "https://www.instagram.com/explore/tags/뚝섬한강공원/"}
            ],
            # 9. 부암동
            [
                {"name": "클럽에스프레소 (Club Espresso)", "tags": "#부암동터줏대감 #드립커피맛집 #러너성지", "map": "https://maps.google.com/?q=Club+Espresso+Buam", "insta": "https://www.instagram.com/clubespresso/"},
                {"name": "계열사 (Gyeyalsa)", "tags": "#서울3대치킨 #인왕산하산푸드 #치맥치트키", "map": "https://maps.google.com/?q=Gyeyalsa+Buam", "insta": "https://www.instagram.com/explore/tags/계열사/"}
            ]
        ],

        # --- 100% UNBROKEN HIGH-QUALITY IMAGES FROM SPOTIFY INTERNET HOST ---
        "Playlist_Title": [
            "Chill Acoustic & Gentle Breeze Pop", "Trendy City Night Grooves", "Bright Morning Warm-Up Beats",
            "Rhythmic Mid-Tempo Running Hits", "Groovy Bassline Urban Anthems", "High-Stamina Cardio Boosters",
            "High-Octane K-Pop Energy Booster", "Relentless Global Rap Pace Maker", "Ultimate Adrenaline Limit Breaker"
        ],
        "Playlist_Tracks": [
            # Beginner 1
            [
                {"title": "Paris in the Rain", "artist": "Lauv", "cover": "https://i.scdn.co/image/ab67616d0000b273df1f07f248e3518e11e0aa06", "link": "https://www.youtube.com/watch?v=kOCkne-Bku4"},
                {"title": "ILYSB", "artist": "LANY", "cover": "https://i.scdn.co/image/ab67616d0000b2734a94628f4116035985834925", "link": "https://www.youtube.com/watch?v=SSTp0rknOgA"},
                {"title": "Youth", "artist": "Troye Sivan", "cover": "https://i.scdn.co/image/ab67616d0000b2730da4239db1ee11b8160c5da5", "link": "https://www.youtube.com/watch?v=XYAghEq5Lfw"}
            ],
            # Beginner 2
            [
                {"title": "Super Far", "artist": "LANY", "cover": "https://i.scdn.co/image/ab67616d0000b2734a94628f4116035985834925", "link": "https://www.youtube.com/watch?v=B88Zas_DclM"},
                {"title": "Strawberries & Cigarettes", "artist": "Troye Sivan", "cover": "https://i.scdn.co/image/ab67616d0000b273a5a5db84f50f3b4bc3c8cf5c", "link": "https://www.youtube.com/watch?v=Z3LgC8u_R8Y"},
                {"title": "I Like Me Better", "artist": "Lauv", "cover": "https://i.scdn.co/image/ab67616d0000b273df1f07f248e3518e11e0aa06", "link": "https://www.youtube.com/watch?v=BcqxLCWn-CE"}
            ],
            # Beginner 3
            [
                {"title": "Feelings", "artist": "Lauv", "cover": "https://i.scdn.co/image/ab67616d0000b2732049e7bdfd6b8bda5a782a20", "link": "https://www.youtube.com/watch?v=421w1jR-SgE"},
                {"title": "Pink Skies", "artist": "LANY", "cover": "https://i.scdn.co/image/ab67616d0000b273468903c7e71fb3d5858cf09f", "link": "https://www.youtube.com/watch?v=eE7T_I9vInU"},
                {"title": "Wild", "artist": "Troye Sivan", "cover": "https://i.scdn.co/image/ab67616d0000b2730da4239db1ee11b8160c5da5", "link": "https://www.youtube.com/watch?v=fdXNNveYOfU"}
            ],
            # Intermediate 1
            [
                {"title": "Attention", "artist": "Charlie Puth", "cover": "https://i.scdn.co/image/ab67616d0000b273b320df949ff03010f3bc30f9", "link": "https://www.youtube.com/watch?v=nfs8NYg7yQM"},
                {"title": "Shivers", "artist": "Ed Sheeran", "cover": "https://i.scdn.co/image/ab67616d0000b273ba5db46f4b0c161d2730ca9c", "link": "https://www.youtube.com/watch?v=Il0S8BoucSA"},
                {"title": "Light Switch", "artist": "Charlie Puth", "cover": "https://i.scdn.co/image/ab67616d0000b27387201c107e3bc1cfec0b88d8", "link": "https://www.youtube.com/watch?v=WFsAon_TWPQ"}
            ],
            # Intermediate 2
            [
                {"title": "How Long", "artist": "Charlie Puth", "cover": "https://i.scdn.co/image/ab67616d0000b273b320df949ff03010f3bc30f9", "link": "https://www.youtube.com/watch?v=TdylllyoV9c"},
                {"title": "Unholy", "artist": "Sam Smith", "cover": "https://i.scdn.co/image/ab67616d0000b273a6a39ae9ff9be8353fb50942", "link": "https://www.youtube.com/watch?v=Uq9gPaizbe8"},
                {"title": "Bad Habits", "artist": "Ed Sheeran", "cover": "https://i.scdn.co/image/ab67616d0000b273ba5db46f4b0c161d2730ca9c", "link": "https://www.youtube.com/watch?v=orJSJGHjBLI"}
            ],
            # Intermediate 3
            [
                {"title": "Shape of You", "artist": "Ed Sheeran", "cover": "https://i.scdn.co/image/ab67616d0000b273ba5db46f4b0c161d2730ca9c", "link": "https://www.youtube.com/watch?v=JGwWNGJdvx8"},
                {"title": "Diamonds", "artist": "Sam Smith", "cover": "https://i.scdn.co/image/ab67616d0000b273da944ec764df7f847524584a", "link": "https://www.youtube.com/watch?v=8RvAKRoDB7o"},
                {"title": "Left and Right", "artist": "Charlie Puth (feat. Jungkook)", "cover": "https://i.scdn.co/image/ab67616d0000b27318357fc10915ff76bcba3380", "link": "https://www.youtube.com/watch?v=a7GITgqwDVg"}
            ],
            # Advanced 1
            [
                {"title": "Dynamite", "artist": "BTS", "cover": "https://i.scdn.co/image/ab67616d0000b2730c071d655f0b50302f3a60ac", "link": "https://www.youtube.com/watch?v=gdZLi9oWNZg"},
                {"title": "Kill This Love", "artist": "BLACKPINK", "cover": "https://i.scdn.co/image/ab67616d0000b27388aa44498522696614cb9131", "link": "https://www.youtube.com/watch?v=2S24-y0Ij3Y"},
                {"title": "HUMBLE.", "artist": "Kendrick Lamar", "cover": "https://i.scdn.co/image/ab67616d0000b2734370db7e49ed0352ef2049d5", "link": "https://www.youtube.com/watch?v=tvTRZJ-4EyI"}
            ],
            # Advanced 2
            [
                {"title": "Pink Venom", "artist": "BLACKPINK", "cover": "https://i.scdn.co/image/ab67616d0000b2737604b96791e81be802fe619c", "link": "https://www.youtube.com/watch?v=glhXCuM_Y7M"},
                {"title": "SICKO MODE", "artist": "Travis Scott", "cover": "https://i.scdn.co/image/ab67616d0000b273072b98f6ba164993d085942f", "link": "https://www.youtube.com/watch?v=d-JBBNg8YKs"},
                {"title": "MIC Drop", "artist": "BTS (Steve Aoki Remix)", "cover": "https://i.scdn.co/image/ab67616d0000b2730c071d655f0b50302f3a60ac", "link": "https://www.youtube.com/watch?v=kTlv5_i8ICM"}
            ],
            # Advanced 3
            [
                {"title": "Run BTS", "artist": "BTS", "cover": "https://i.scdn.co/image/ab67616d0000b273617be34015df3cc8df179ebc", "link": "https://www.youtube.com/watch?v=9tG70B3DLIY"},
                {"title": "How You Like That", "artist": "BLACKPINK", "cover": "https://i.scdn.co/image/ab67616d0000b2737604b96791e81be802fe619c", "link": "https://www.youtube.com/watch?v=ioNng23DkIM"},
                {"title": "Lose Yourself", "artist": "Eminem", "cover": "https://i.scdn.co/image/ab67616d0000b273b6ebe21bc277da204e339f4a", "link": "https://www.youtube.com/watch?v=_Yhyp_hXnyU"}
            ]
        ]
    }
    return pd.DataFrame(data)

df = load_course_data()

# Custom Route Generator
def get_custom_route(center_lat, center_lng, course_idx):
    points = []
    shape_factor_x = 0.0014 if course_idx % 2 == 0 else 0.0009
    shape_factor_y = 0.0016 if course_idx % 3 == 0 else 0.0019
    
    for i in range(21):
        if i < 6:
            lat = center_lat + (i * shape_factor_x)
            lng = center_lng
        elif i < 11:
            lat = center_lat + (5 * shape_factor_x)
            lng = center_lng + ((i - 5) * shape_factor_y)
        elif i < 16:
            lat = center_lat + ((15 - i) * shape_factor_x)
            lng = center_lng + (5 * shape_factor_y)
        else:
            lat = center_lat
            lng = center_lng + ((20 - i) * shape_factor_y)
            
        if course_idx in [0, 1, 2]:
            color = "#06D6A0" if i != 10 else "#FFD166"
        elif course_idx in [3, 4, 5]:
            color = "#E25B3C" if i in [8, 9] else ("#FFD166" if i in [4, 5, 12, 13] else "#06D6A0")
        else:
            color = "#E25B3C" if i in [2, 3, 4, 5, 8, 9, 12, 13, 14, 15] else "#FFD166"
            
        points.append({"coord": [lat, lng], "color": color})
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
        # 1) Clean minimalist header without labels
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
        
        m = folium.Map(location=course_row['Map_Center'], zoom_start=15, tiles="CartoDB positron")
        route_points = get_custom_route(course_row['Map_Center'][0], course_row['Map_Center'][1], internal_idx)
        for idx in range(len(route_points) - 1):
            p1 = route_points[idx]["coord"]
            p2 = route_points[idx+1]["coord"]
            color_code = route_points[idx]["color"]
            folium.PolyLine(locations=[p1, p2], color=color_code, width=6, opacity=0.9).add_to(m)
        
        folium.Marker(location=course_row['Map_Center'], popup="Start Point", icon=folium.Icon(color="black", icon="play", prefix="fa")).add_to(m)
        st_folium(m, width=1400, height=350, key=f"full_map_{internal_idx}")
        
        st.markdown("---")
        
        # 3) Full Width Nearby Places
        st.markdown("#### ☕ Nearby Places")
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
        
        # 4) Full Width Custom Music Player Grid (Melon/Spotify Layout Style)
        st.markdown("#### 🎵 Recommended Playlist")
        st.write(f"**Theme: {course_row['Playlist_Title']}**")
        st.caption("Click '▶ Play' to instantly open and stream the track on YouTube.")
        
        for track in course_row['Playlist_Tracks']:
            st.markdown(f"""
                <div class="player-row">
                    <img src="{track['cover']}" class="player-cover">
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
    st.caption("Run-Step Dashboard v6.3 | Developed by Yeonhu Lee (SKKU Student ID: 2024314274)")

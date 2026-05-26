import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. Page Configuration (Ivory theme tone)
st.set_page_config(
    page_title="Run-Step: Running Course Recommendation",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Custom CSS for Ivory Background, Clean UI & Music Player Grid
st.markdown("""
    <style>
    .stApp {
        background-color: #FDFBF7;
        color: #2D2A26;
    }
    div.stButton > button:first-child {
        background-color: #2D2A26;
        color: #FDFBF7;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #E25B3C;
        color: #FDFBF7;
    }
    /* Playlist Player Box Styling */
    .player-row {
        display: flex;
        align-items: center;
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        border: 1px solid #EFECE6;
    }
    .player-cover {
        width: 55px;
        height: 55px;
        border-radius: 6px;
        object-fit: cover;
        margin-right: 16px;
    }
    .player-info {
        flex-grow: 1;
    }
    .player-title {
        font-size: 16px;
        font-weight: bold;
        color: #2D2A26;
        margin-bottom: 2px;
    }
    .player-artist {
        font-size: 13px;
        color: #7A756E;
    }
    .play-btn {
        background-color: #2D2A26;
        color: #FDFBF7 !important;
        padding: 6px 14px;
        border-radius: 20px;
        text-decoration: none;
        font-size: 13px;
        font-weight: bold;
        transition: 0.2s;
    }
    .play-btn:hover {
        background-color: #E25B3C;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Initialize Session State for Multi-step Navigation (Welcome -> Survey -> Dashboard)
if "page_stage" not in st.session_state:
    st.session_state.page_stage = "welcome"
if "user_level" not in st.session_state:
    st.session_state.user_level = "Beginner"

# 3. Dataset Setup with Geographic Coordinates, Real Hotspots, Links, and Track Metadata
@st.cache_data
def load_course_data():
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["한강시민공원 여의도 코스", "석촌호수 루프 트레일", "동네 근린공원 산책로", 
                       "남산 둘레길 시닉 코스", "양재천-탄천 연계 롱런 코스", "북서울꿈의숲 업힐 트랙", 
                       "인왕산 정복 트레일러닝", "하프 마라톤 실전 정복 코스", "지옥의 10비트 고개 코스"],
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
        
        # --- 2 REAL HOTSPOTS PER COURSE ---
        "Spots": [
            # 1. 여의도
            [
                {"name": "더현대 서울 (The Hyundai Seoul)", "tags": "#쇼핑몰 #에어컨빵빵 #러닝후구경", "map": "https://maps.google.com/?q=The+Hyundai+Seoul", "insta": "https://www.instagram.com/thehyundai_seoul/"},
                {"name": "여의도 한강공원 배달존", "tags": "#돗자리 #한강라면 #치맥 #러너성지", "map": "https://maps.google.com/?q=Yeouido+Hangang+Park", "insta": "https://www.instagram.com/explore/tags/한강라면/"}
            ],
            # 2. 석촌호수
            [
                {"name": "뷰클런즈 (Vrewcleans)", "tags": "#송리단길 #쉼이있는카페 #나무인테리어", "map": "https://maps.google.com/?q=Vrewcleans", "insta": "https://www.instagram.com/vrewcleans/"},
                {"name": "니커버커베이글 (Knickerbocker Bagel)", "tags": "#웨이팅맛집 #탄수화물보충 #호수뷰", "map": "https://maps.google.com/?q=Knickerbocker+Bagel+Seoul", "insta": "https://www.instagram.com/knickerbockerbagel_korea/"}
            ],
            # 3. 동네공원
            [
                {"name": "파리바게뜨 로컬 스토어", "tags": "#갓구운빵 #아이스아메리카노 #접근성최고", "map": "https://maps.google.com/?q=Paris+Baguette+Korea", "insta": "https://www.instagram.com/parisbaguette_kr/"},
                {"name": "이디야커피 공원점", "tags": "#가성비카페 #수분충전 #러닝마무리", "map": "https://maps.google.com/?q=Ediya+Coffee", "insta": "https://www.instagram.com/ediya.coffee/"}
            ],
            # 4. 남산
            [
                {"name": "101번지 남산돈까스 본점", "tags": "#단백질보충 #러너필수코스 #원조돈까스", "map": "https://maps.google.com/?q=101+Namsan+Donkatsu", "insta": "https://www.instagram.com/explore/tags/남산돈까스/"},
                {"name": "이중생업 남산", "tags": "#남산감성맛집 #깔끔한한식 #러닝데이트", "map": "https://maps.google.com/?q=Namsan+Seoul", "insta": "https://www.instagram.com/explore/tags/남산맛집/"}
            ],
            # 5. 양재천
            [
                {"name": "룸서비스301 (Room Service 301)", "tags": "#양재천카페거리 #창가뷰 #숲감성", "map": "https://maps.google.com/?q=Room+Service+301", "insta": "https://www.instagram.com/roomservice301/"},
                {"name": "캐틀앤비 (Cattle & Bee)", "tags": "#테라스카페 #도곡동브런치 #분위기맛집", "map": "https://maps.google.com/?q=Cattle+and+Bee+Dogok", "insta": "https://www.instagram.com/cattle_bee/"}
            ],
            # 6. 북서울꿈의숲
            [
                {"name": "라포레스타 (La Foresta)", "tags": "#꿈의숲일식양식 #통창뷰 #힐링식사", "map": "https://maps.google.com/?q=La+Foresta+Seoul", "insta": "https://www.instagram.com/explore/tags/라포레스타/"},
                {"name": "꿈의숲 미술관 카페", "tags": "#전망좋은곳 #시원한음료 #문화생활", "map": "https://maps.google.com/?q=North+Seoul+Dream+Forest", "insta": "https://www.instagram.com/explore/tags/북서울꿈의숲/"}
            ],
            # 7. 인왕산
            [
                {"name": "통인시장 (Tongin Market)", "tags": "#엽전도시락 #기름떡볶이 #서촌감성", "map": "https://maps.google.com/?q=Tongin+Market", "insta": "https://www.instagram.com/explore/tags/통인시장/"},
                {"name": "스태픽스 (Staff Picks)", "tags": "#서촌야외테라스 #은행나무맛집 #인스타핫플", "map": "https://maps.google.com/?q=Staff+Picks+Seoul", "insta": "https://www.instagram.com/staffpicks_official/"}
            ],
            # 8. 하프 마라톤
            [
                {"name": "아구아구 (Agu Agu) 뚝섬", "tags": "#포크샐러드 #러너식단 #리프레시", "map": "https://maps.google.com/?q=Ttukseom+Park", "insta": "https://www.instagram.com/explore/tags/뚝섬맛집/"},
                {"name": "뚝섬한강공원 편의점", "tags": "#파워에이드 #에너지젤보충 #보급기지", "map": "https://maps.google.com/?q=Ttukseom+Hangang+Park", "insta": "https://www.instagram.com/explore/tags/뚝섬한강공원/"}
            ],
            # 9. 10비트
            [
                {"name": "클럽에스프레소 (Club Espresso)", "tags": "#부암동터줏대감 #드립커피맛집 #러너성지", "map": "https://maps.google.com/?q=Club+Espresso+Buam", "insta": "https://www.instagram.com/clubespresso/"},
                {"name": "계열사 (Gyeyalsa)", "tags": "#서울3대치킨 #인왕산하산푸드 #치맥치트키", "map": "https://maps.google.com/?q=Gyeyalsa", "insta": "https://www.instagram.com/explore/tags/계열사/"}
            ]
        ],

        # --- REAL PLAYER SONGS WITH BEAUTIFUL ALBUM ARTWORKS ---
        "Playlist_Title": [
            "Chill Acoustic & Gentle Breeze Pop", "Trendy City Night Grooves", "Bright Morning Warm-Up Beats",
            "Rhythmic Mid-Tempo Running Hits", "Groovy Bassline Urban Anthems", "High-Stamina Cardio Boosters",
            "High-Octane K-Pop Energy Booster", "Relentless Global Rap Pace Maker", "Ultimate Adrenaline Limit Breaker"
        ],
        "Playlist_Tracks": [
            # Beginner 1
            [
                {"title": "Paris in the Rain", "artist": "Lauv", "cover": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=100&q=80", "link": "https://www.youtube.com/watch?v=kOCkne-Bku4"},
                {"title": "ILYSB", "artist": "LANY", "cover": "https://images.unsplash.com/photo-1498038432885-c6f3f1b912ee?w=100&q=80", "link": "https://www.youtube.com/watch?v=SSTp0rknOgA"},
                {"title": "Youth", "artist": "Troye Sivan", "cover": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=100&q=80", "link": "https://www.youtube.com/watch?v=XYAghEq5Lfw"}
            ],
            # Beginner 2
            [
                {"title": "Super Far", "artist": "LANY", "cover": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=100&q=80", "link": "https://www.youtube.com/watch?v=B88Zas_DclM"},
                {"title": "Strawberries & Cigarettes", "artist": "Troye Sivan", "cover": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=100&q=80", "link": "https://www.youtube.com/watch?v=Z3LgC8u_R8Y"},
                {"title": "I Like Me Better", "artist": "Lauv", "cover": "https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=100&q=80", "link": "https://www.youtube.com/watch?v=BcqxLCWn-CE"}
            ],
            # Beginner 3
            [
                {"title": "Feelings", "artist": "Lauv", "cover": "https://images.unsplash.com/photo-1501386761578-eac5c94b800a?w=100&q=80", "link": "https://www.youtube.com/watch?v=421w1jR-SgE"},
                {"title": "Pink Skies", "artist": "LANY", "cover": "https://images.unsplash.com/photo-1487180142328-054b783ef471?w=100&q=80", "link": "https://www.youtube.com/watch?v=eE7T_I9vInU"},
                {"title": "Wild", "artist": "Troye Sivan", "cover": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=100&q=80", "link": "https://www.youtube.com/watch?v=fdXNNveYOfU"}
            ],
            # Intermediate 1
            [
                {"title": "Attention", "artist": "Charlie Puth", "cover": "https://images.unsplash.com/photo-1506157786151-b8491531f063?w=100&q=80", "link": "https://www.youtube.com/watch?v=nfs8NYg7yQM"},
                {"title": "Shivers", "artist": "Ed Sheeran", "cover": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=100&q=80", "link": "https://www.youtube.com/watch?v=Il0S8BoucSA"},
                {"title": "Light Switch", "artist": "Charlie Puth", "cover": "https://images.unsplash.com/photo-1484876065684-b683cf17d276?w=100&q=80", "link": "https://www.youtube.com/watch?v=WFsAon_TWPQ"}
            ],
            # Intermediate 2
            [
                {"title": "How Long", "artist": "Charlie Puth", "cover": "https://images.unsplash.com/photo-1453090923802-60c396337ed3?w=100&q=80", "link": "https://www.youtube.com/watch?v=TdylllyoV9c"},
                {"title": "Unholy", "artist": "Sam Smith", "cover": "https://images.unsplash.com/photo-1525362081669-2b476bb628c3?w=100&q=80", "link": "https://www.youtube.com/watch?v=Uq9gPaizbe8"},
                {"title": "Bad Habits", "artist": "Ed Sheeran", "cover": "https://images.unsplash.com/photo-1574169208507-84376144848b?w=100&q=80", "link": "https://www.youtube.com/watch?v=orJSJGHjBLI"}
            ],
            # Intermediate 3
            [
                {"title": "Shape of You", "artist": "Ed Sheeran", "cover": "https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=100&q=80", "link": "https://www.youtube.com/watch?v=JGwWNGJdvx8"},
                {"title": "Diamonds", "artist": "Sam Smith", "cover": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=100&q=80", "link": "https://www.youtube.com/watch?v=8RvAKRoDB7o"},
                {"title": "Left and Right", "artist": "Charlie Puth (feat. Jungkook)", "cover": "https://images.unsplash.com/photo-1483412033650-1015ddeb83d1?w=100&q=80", "link": "https://www.youtube.com/watch?v=a7GITgqwDVg"}
            ],
            # Advanced 1
            [
                {"title": "Dynamite", "artist": "BTS", "cover": "https://images.unsplash.com/photo-1563841930606-67e2bce48b78?w=100&q=80", "link": "https://www.youtube.com/watch?v=gdZLi9oWNZg"},
                {"title": "Kill This Love", "artist": "BLACKPINK", "cover": "https://images.unsplash.com/photo-1528722828814-77b9b83aafb2?w=100&q=80", "link": "https://www.youtube.com/watch?v=2S24-y0Ij3Y"},
                {"title": "HUMBLE.", "artist": "Kendrick Lamar", "cover": "https://images.unsplash.com/photo-1482440308425-276ad0f28b19?w=100&q=80", "link": "https://www.youtube.com/watch?v=tvTRZJ-4EyI"}
            ],
            # Advanced 2
            [
                {"title": "Pink Venom", "artist": "BLACKPINK", "cover": "https://images.unsplash.com/photo-1511735111819-9a3f7709049c?w=100&q=80", "link": "https://www.youtube.com/watch?v=glhXCuM_Y7M"},
                {"title": "SICKO MODE", "artist": "Travis Scott", "cover": "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17?w=100&q=80", "link": "https://www.youtube.com/watch?v=d-JBBNg8YKs"},
                {"title": "MIC Drop", "artist": "BTS (Steve Aoki Remix)", "cover": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=100&q=80", "link": "https://www.youtube.com/watch?v=kTlv5_i8ICM"}
            ],
            # Advanced 3
            [
                {"title": "Run BTS (달려라 방탄)", "artist": "BTS", "cover": "https://images.unsplash.com/photo-1598387181032-a3103a2db5b3?w=100&q=80", "link": "https://www.youtube.com/watch?v=9tG70B3DLIY"},
                {"title": "How You Like That", "artist": "BLACKPINK", "cover": "https://images.unsplash.com/photo-1571330735066-03add575b712?w=100&q=80", "link": "https://www.youtube.com/watch?v=ioNng23DkIM"},
                {"title": "Lose Yourself", "artist": "Eminem", "cover": "https://images.unsplash.com/photo-1503095396549-807759245b35?w=100&q=80", "link": "https://www.youtube.com/watch?v=_Yhyp_hXnyU"}
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
        # 1) Clean Header with raw course name
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
        
        # 3) Full Width Nearby Places with Anglicized Buttons & Genuine Hotspots
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
        
        # 4) Full Width Custom Music Player Grid
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
    st.caption("Run-Step Dashboard v6.2 | Developed by Yeonhu Lee (SKKU Student ID: 2024314274)")

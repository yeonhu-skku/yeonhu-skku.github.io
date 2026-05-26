import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ============================================================
# 1. PAGE CONFIGURATION & CUSTOM THEME (Apple Minimal)
# ============================================================
st.set_page_config(
    page_title="Run-Step | Seoul Running Guide",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Premium Minimal CSS Theme - Fully Inspired by Apple iOS & Apple Fitness Aesthetics
st.markdown("""
<style>
    /* Global Reset & Base */
    .stApp {
        background: linear-gradient(180deg, #FAFAFC 0%, #F5F5F7 100%);
        font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Apple Typography System */
    h1 {
        font-size: 2.75rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
        color: #1D1D1F !important;
        line-height: 1.15 !important;
    }
    h2 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.015em !important;
        color: #1D1D1F !important;
    }
    h3 {
        font-size: 1.125rem !important;
        font-weight: 600 !important;
        color: #1D1D1F !important;
        letter-spacing: -0.01em !important;
    }
    p, .stMarkdown {
        color: #515154;
        line-height: 1.55;
    }
    
    /* Apple Premium Card Component */
    .premium-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 0, 0, 0.05);
        border-radius: 18px;
        padding: 28px;
        box-shadow: 
            0 4px 30px rgba(0, 0, 0, 0.02),
            0 1px 2px rgba(0, 0, 0, 0.01);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .premium-card:hover {
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 
            0 12px 36px rgba(0, 0, 0, 0.05),
            0 4px 12px rgba(0, 0, 0, 0.02);
    }
    
    /* Metric Display */
    .metric-container {
        background: #FFFFFF;
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: 14px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.01);
        transition: all 0.25s ease;
    }
    .metric-container:hover {
        transform: scale(1.02);
        border-color: rgba(0, 0, 0, 0.15);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1D1D1F;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #86868B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Accent Metric */
    .metric-accent {
        background: #1D1D1F;
        border: none;
    }
    .metric-accent .metric-value {
        color: #FF453A;
    }
    .metric-accent .metric-label {
        color: rgba(255, 255, 255, 0.5);
    }
    
    /* Tag Pills */
    .tag-pill {
        display: inline-block;
        background: #E8E8ED;
        color: #424245;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 4px 4px 4px 0;
        transition: all 0.2s ease;
    }
    .tag-pill:hover {
        background: #D2D2D7;
        color: #1D1D1F;
    }
    
    /* Level Badge */
    .level-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        border-radius: 24px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    .level-beginner {
        background: rgba(52, 199, 89, 0.15);
        color: #248A3D;
    }
    .level-intermediate {
        background: rgba(255, 149, 0, 0.15);
        color: #C27200;
    }
    .level-advanced {
        background: rgba(255, 59, 48, 0.15);
        color: #D32F2F;
    }
    
    /* Apple Music Style Player Card */
    .player-card {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 10px;
        border: 1px solid rgba(0, 0, 0, 0.06);
        transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .player-card:hover {
        background: #FFFFFF;
        border-color: rgba(0, 0, 0, 0.15);
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .player-artwork {
        width: 52px;
        height: 52px;
        background: linear-gradient(135deg, #FF2D55 0%, #FA243C 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        flex-shrink: 0;
        box-shadow: 0 4px 10px rgba(250,36,60,0.2);
    }
    .player-info {
        flex-grow: 1;
        min-width: 0;
    }
    .player-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1D1D1F;
        margin-bottom: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .player-artist {
        font-size: 0.8rem;
        color: #86868B;
        font-weight: 500;
    }
    .play-button {
        background: #1D1D1F;
        color: #FFFFFF !important;
        padding: 10px 20px;
        border-radius: 24px;
        text-decoration: none !important;
        font-size: 0.8rem;
        font-weight: 600;
        transition: all 0.2s ease;
        flex-shrink: 0;
    }
    .play-button:hover {
        background: #FA243C;
        transform: scale(1.04);
        box-shadow: 0 4px 12px rgba(250,36,60,0.3);
    }
    
    /* Apple Maps Style Spot Card & Unified Link layout fixing spacer gap bugs */
    .spot-card {
        background: #FFFFFF;
        border-radius: 18px;
        padding: 24px;
        border: 1px solid rgba(0, 0, 0, 0.06);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.01);
        transition: all 0.3s ease;
    }
    .spot-card:hover {
        border-color: #007AFF;
        box-shadow: 0 8px 30px rgba(0, 122, 255, 0.06);
    }
    .spot-header-group {
        margin-bottom: 20px;
    }
    .spot-name {
        font-size: 1.15rem;
        font-weight: 600;
        color: #1D1D1F;
        margin-bottom: 4px;
        letter-spacing: -0.01em;
    }
    .spot-tags {
        font-size: 0.825rem;
        color: #86868B;
        line-height: 1.5;
        margin-top: 8px;
    }
    .spot-action-container {
        display: flex;
        gap: 10px;
        width: 100%;
    }
    .spot-link-btn {
        flex: 1;
        text-align: center;
        background: transparent;
        color: #007AFF !important;
        border: 1px solid rgba(0, 122, 255, 0.2);
        border-radius: 20px;
        padding: 10px 0;
        font-size: 0.85rem;
        font-weight: 600;
        text-decoration: none !important;
        transition: all 0.2s ease;
    }
    .spot-link-btn:hover {
        border-color: #007AFF;
        background: #007AFF;
        color: #FFFFFF !important;
    }
    
    /* Custom Streamlit Buttons */
    .stButton > button {
        background: #1D1D1F !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 28px !important;
        padding: 14px 36px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: -0.01em !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
    }
    .stButton > button:hover {
        background: #007AFF !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(0, 122, 255, 0.25) !important;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(120, 120, 128, 0.08) !important;
        padding: 5px !important;
        border-radius: 14px !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 10px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        color: #1D1D1F !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.4) !important;
    }
    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #1D1D1F !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }
    
    /* Select Box */
    .stSelectbox [data-baseweb="select"] {
        background: #FFFFFF;
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.15);
    }
    .stSelectbox [data-baseweb="select"]:focus-within { border-color: #007AFF; }
    
    /* Radio Buttons */
    .stRadio > div { gap: 12px; }
    .stRadio label {
        background: #FFFFFF;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .stRadio label:hover { border-color: rgba(0,0,0,0.25); }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background: rgba(0, 0, 0, 0.08);
        margin: 32px 0;
    }
    
    /* Hero Section */
    .hero-section {
        text-align: center;
        padding: 60px 20px 40px;
    }
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: #1D1D1F;
        margin-bottom: 16px;
        line-height: 1;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #86868B;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto 40px;
        line-height: 1.55;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 122, 255, 0.08);
        color: #007AFF;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 24px;
    }
    
    /* Weather Widget */
    .weather-widget {
        background: linear-gradient(145deg, #5AC8FA 0%, #007AFF 100%);
        border-radius: 16px;
        padding: 20px 24px;
        color: white;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 4px 15px rgba(0,122,255,0.15);
    }
    .weather-temp { font-size: 2.5rem; font-weight: 600; }
    .weather-info { font-size: 0.9rem; opacity: 0.95; font-weight: 500; }
    
    /* Map Container */
    .map-container {
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }
    
    /* Section Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .section-icon {
        width: 40px;
        height: 40px;
        background: rgba(0, 0, 0, 0.04);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. SESSION STATE INITIALIZATION
# ============================================================
if "page_stage" not in st.session_state:
    st.session_state.page_stage = "welcome"
if "user_level" not in st.session_state:
    st.session_state.user_level = "Beginner"
if "comparison_list" not in st.session_state:
    st.session_state.comparison_list = []

# ============================================================
# 3. DATA LAYER
# ============================================================
@st.cache_data
def load_course_data():
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", 
                  "Intermediate", "Intermediate", "Intermediate", 
                  "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["Yeouido Hangang Park", "Seokchon Lake", "Neighborhood Park", 
                       "Namsan Dulle-gil", "Yangjaecheon Stream", "Dream Forest", 
                       "Inwangsan Trail", "Ttukseom Hangang Park", "Buamdong Hills"],
        "Course_Name_KR": ["여의도 한강공원", "석촌호수", "동네 근린공원",
                          "남산 둘레길", "양재천", "북서울꿈의숲",
                          "인왕산", "뚝섬 한강공원", "부암동"],
        "Distance_KM": [3.0, 2.5, 2.0, 7.0, 8.5, 5.0, 12.0, 21.0, 15.0],
        "Estimated_Time": ["25-30 min", "20-25 min", "15-20 min",
                          "50-60 min", "60-75 min", "40-50 min",
                          "90-120 min", "150-180 min", "120-150 min"],
        "Calories": [180, 150, 120, 450, 550, 320, 900, 1600, 1200],
        "Elevation_Gain": [5, 3, 2, 120, 45, 85, 280, 50, 320],
        "Elevation_Desc": ["Flat", "Flat", "Flat", 
                          "Moderate", "Low", "Moderate", 
                          "Steep", "Varied", "Very Steep"],
        "Surface": ["Paved", "Paved", "Paved", 
                   "Mixed", "Paved", "Mixed", 
                   "Trail", "Paved", "Trail"],
        "ShLevel": ["Low", "Medium", "Medium",
                    "High", "Low", "High",
                    "High", "Low", "Medium"],
        "Water_Fountains": [8, 4, 2, 6, 12, 5, 3, 15, 2],
        "Restrooms": [6, 3, 1, 4, 8, 4, 2, 10, 1],
        "Best_Time": ["Evening", "Night", "Morning",
                     "Morning", "Evening", "Afternoon",
                     "Morning", "Evening", "Morning"],
        "Crowd_Level": ["High", "High", "Low",
                       "Medium", "Medium", "Low",
                       "Low", "High", "Low"],
        "Pros": [
            "Exceptionally flat terrain with refreshing riverside breeze. Excellent facilities including water fountains, restrooms, and convenience stores every 500m.",
            "Perfect oval track optimized for consistent pacing. Stunning night views of Lotte World Tower. Well-lit paths for evening runs.",
            "Maximum accessibility for daily training. Safe, well-lit environment with minimal traffic. Ideal for building running habits.",
            "Dense tree coverage provides natural cooling. Beautiful seasonal scenery with cherry blossoms in spring and foliage in fall.",
            "Zero traffic lights for uninterrupted long runs. Premier choice for marathon training with consistent pacing opportunities.",
            "Short but intense hill sections perfect for interval training. Excellent for building cardiovascular endurance.",
            "Immersive trail experience within city limits. Dynamic terrain keeps workouts engaging. Panoramic city views at summit.",
            "Closely replicates official marathon conditions. Excellent for race-day strategy testing and pacing practice.",
            "Maximum intensity training ground. Tests anaerobic thresholds effectively. Builds exceptional lower-body strength."
        ],
        "Cons": [
            "High volume of bicycle traffic requires errors awareness. Can be crowded on weekends. Limited shade during summer.",
            "Heavy pedestrian traffic on weekend evenings. The popular photo spots can cause congestion on the path.",
            "Short loop distance may feel repetitive. Limited amenities compared to major parks.",
            "Steep sections cause sudden heart rate spikes. Requires careful pace management to avoid overexertion.",
            "Minimal shade coverage - UV protection essential. Long stretches without landmarks can feel monotonous.",
            "Initial incline steeper than expected. Easy to underestimate intensity leading to knee strain.",
            "Uneven rocky paths and stairs throughout. Technical trail shoes mandatory. High injury risk for beginners.",
            "Long distance requires careful hydration planning. Limited emergency exit points in middle sections.",
            "Extreme joint stress - not suitable for beginners or those with joint issues. Proper conditioning required."
        ],
        "Map_Center": [
            [37.5289, 126.9331], [37.5074, 127.1031], [37.5145, 127.0607],
            [37.5509, 126.9909], [37.4934, 127.0601], [37.6257, 127.0371],
            [37.5758, 126.9583], [37.5408, 127.0717], [37.5921, 126.9423]
        ],
        "Spots": [
            [
                {"name": "세상의모든아침 (All That's Morning)", "name_kr": "세상의모든아침 여의도점", "tags": "📷 Brunch · Hotel View · Carb Refuel", "map": "https://maps.google.com/?q=세상의모든아침+여의도점", "insta": "https://www.instagram.com/all_thats_morning/"},
                {"name": "카페 진정성 (Cafe Jinjeongseong)", "name_kr": "카페 진정성 여의도점", "tags": "☕ Milk Tea · Modern · Instagram Hot", "map": "https://maps.google.com/?q=카페+진정성+여의도점", "insta": "https://www.instagram.com/cafe_jinjungsung/"}
            ],
            [
                {"name": "뷰클런즈 (Vrewcleans)", "name_kr": "뷰클런즈 송리단길점", "tags": "☕ Songlidangil · Wood Interior · Iced Tea", "map": "https://maps.google.com/?q=뷰클런즈", "insta": "https://www.instagram.com/vrewcleans/"},
                {"name": "니커버커베이글 (Knickerbocker Bagel)", "name_kr": "니커버커베이글 석촌호수점", "tags": "🥯 NYC Style · Carb Heaven · Lake View", "map": "https://maps.google.com/?q=니커버커베이글+송파점", "insta": "https://www.instagram.com/knickerbockerbagel_korea/"}
            ],
            [
                {"name": "파리바게뜨 (Paris Baguette Local)", "name_kr": "파리바게뜨 로컬 스토어", "tags": "🍞 Fresh Sandwich · Protein · Accessible", "map": "https://maps.google.com/?q=파리바게뜨", "insta": "https://www.instagram.com/parisbaguette_kr/"},
                {"name": "이디야커피 (Ediya Coffee)", "name_kr": "이디야커피 공원점", "tags": "☕ Iced Americano · Quick Hydration", "map": "https://maps.google.com/?q=이디야커피", "insta": "https://www.instagram.com/ediya.coffee/"}
            ],
            [
                {"name": "101번지 남산돈까스 (101 Namsan Tonkatsu)", "name_kr": "101번지 남산돈까스 본점", "tags": "🔨 Classic · Protein Refuel · Must-Try", "map": "https://maps.google.com/?q=101번지+남산돈까스", "insta": "https://www.instagram.com/explore/tags/남산돈까스/"},
                {"name": "이중생업 남산 (Yijungsaengup)", "name_kr": "이중생업 남산", "tags": "🍝 Korean Fusion · Clean Pasta · Date Spot", "map": "https://maps.google.com/?q=이중생업+남산", "insta": "https://www.instagram.com/explore/tags/남산맛집/"}
            ],
            [
                {"name": "룸서비스301 (Room Service 301)", "name_kr": "룸서비스301 양재천점", "tags": "🌳 Forest View · Dessert Cafe · Aesthetic", "map": "https://maps.google.com/?q=룸서비스301", "insta": "https://www.instagram.com/roomservice301/"},
                {"name": "캐틀앤비 (Cattle & Bee)", "name_kr": "캐틀앤비 도곡점", "tags": "🍳 Italian Brunch · Terrace · Dogok", "map": "https://maps.google.com/?q=캐틀앤비+양재점", "insta": "https://www.instagram.com/cattle_bee/"}
            ],
            [
                {"name": "라포레스타 (La Foresta)", "name_kr": "라포레스타 꿈의숲점", "tags": "🍕 Pizza & Pasta · Green View · Family", "map": "https://maps.google.com/?q=라포레스타", "insta": "https://www.instagram.com/explore/tags/라포레스타/"},
                {"name": "꿈의숲 미술관 카페", "name_kr": "꿈의숲 미술관 카페", "tags": "🏙️ Observatory · Smoothie · Culture", "map": "https://maps.google.com/?q=북서울꿈의숲", "insta": "https://www.instagram.com/explore/tags/북서울꿈의숲/"}
            ],
            [
                {"name": "H라운지 (H Lounge Seochon)", "name_kr": "H라운지 서촌점", "tags": "🍝 Italian · Garden Terrace · Post-Hike", "map": "https://maps.google.com/?q=H라운지", "insta": "https://www.instagram.com/explore/tags/서촌브런치/"},
                {"name": "스태픽스 (Staff Picks)", "name_kr": "스태픽스 서촌", "tags": "🍂 Outdoor Terrace · Ginkgo · Runner Haven", "map": "https://maps.google.com/?q=스태픽스", "insta": "https://www.instagram.com/staffpicks_official/"}
            ],
            [
                {"name": "아구아구 (Agu Agu Ttukseom)", "name_kr": "아구아구 뚝섬점", "tags": "🥗 Fresh Salad Bowl · Light Meal · Healthy", "map": "https://maps.google.com/?q=아구아구+뚝섬", "insta": "https://www.instagram.com/explore/tags/뚝섬맛집/"},
                {"name": "한강공원 편의점 (Riverside Convenience)", "name_kr": "뚝섬한강공원 편의점", "tags": "🥤 Powerade · Ice Cup · Instant Ramyun", "map": "https://maps.google.com/?q=뚝섬한강공원", "insta": "https://www.instagram.com/explore/tags/뚝섬한강공원/"}
            ],
            [
                {"name": "클럽에스프레소 (Club Espresso)", "name_kr": "클럽에스프레소 부암본점", "tags": "☕ Drip Coffee · Cyclist Haven · Classic", "map": "https://maps.google.com/?q=클럽에스프레소", "insta": "https://www.instagram.com/clubespresso/"},
                {"name": "계열사 (Gyeyalsa Chicken)", "name_kr": "계열사 부암점", "tags": "🍗 Seoul Top 3 Chicken · Protein Reward", "map": "https://maps.google.com/?q=계열사+부암동", "insta": "https://www.instagram.com/explore/tags/계열사/"}
            ]
        ],
        "Playlist_Title": [
            "Chill Acoustic Breeze", "City Night Grooves", "Morning Warm-Up",
            "Mid-Tempo Rhythm", "Urban Bassline", "Cardio Booster",
            "K-Pop Energy", "Global Rap Pace", "Adrenaline Peak"
        ],
        "Playlist_BPM": ["100-120", "110-125", "105-120",
                        "130-145", "135-150", "140-155",
                        "150-170", "155-175", "160-180"],
        "Playlist_Tracks": [
            [
                {"title": "Paris in the Rain", "artist": "Lauv", "link": "https://www.youtube.com/watch?v=kOCkne-Bku4"},
                {"title": "ILYSB", "artist": "LANY", "link": "https://www.youtube.com/watch?v=SSTp0rknOgA"},
                {"title": "Youth", "artist": "Troye Sivan", "link": "https://www.youtube.com/watch?v=XYAghEq5Lfw"}
            ],
            [
                {"title": "Super Far", "artist": "LANY", "link": "https://www.youtube.com/watch?v=B88Zas_DclM"},
                {"title": "Strawberries & Cigarettes", "artist": "Troye Sivan", "link": "https://www.youtube.com/watch?v=Z3LgC8u_R8Y"},
                {"title": "I Like Me Better", "artist": "Lauv", "link": "https://www.youtube.com/watch?v=BcqxLCWn-CE"}
            ],
            [
                {"title": "Feelings", "artist": "Lauv", "link": "https://www.youtube.com/watch?v=421w1jR-SgE"},
                {"title": "Pink Skies", "artist": "LANY", "link": "https://www.youtube.com/watch?v=eE7T_I9vInU"},
                {"title": "Wild", "artist": "Troye Sivan", "link": "https://www.youtube.com/watch?v=fdXNNveYOfU"}
            ],
            [
                {"title": "Attention", "artist": "Charlie Puth", "link": "https://www.youtube.com/watch?v=nfs8NYg7yQM"},
                {"title": "Shivers", "artist": "Ed Sheeran", "link": "https://www.youtube.com/watch?v=Il0S8BoucSA"},
                {"title": "Light Switch", "artist": "Charlie Puth", "link": "https://www.youtube.com/watch?v=WFsAon_TWPQ"}
            ],
            [
                {"title": "How Long", "artist": "Charlie Puth", "link": "https://www.youtube.com/watch?v=TdylllyoV9c"},
                {"title": "Unholy", "artist": "Sam Smith", "link": "https://www.youtube.com/watch?v=Uq9gPaizbe8"},
                {"title": "Bad Habits", "artist": "Ed Sheeran", "link": "https://www.youtube.com/watch?v=orJSJGHjBLI"}
            ],
            [
                {"title": "Shape of You", "artist": "Ed Sheeran", "link": "https://www.youtube.com/watch?v=JGwWNGJdvx8"},
                {"title": "Diamonds", "artist": "Sam Smith", "link": "https://www.youtube.com/watch?v=8RvAKRoDB7o"},
                {"title": "Left and Right", "artist": "Charlie Puth ft. Jungkook", "link": "https://www.youtube.com/watch?v=a7GITgqwDVg"}
            ],
            [
                {"title": "Dynamite", "artist": "BTS", "link": "https://www.youtube.com/watch?v=gdZLi9oWNZg"},
                {"title": "Kill This Love", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=2S24-y0Ij3Y"},
                {"title": "HUMBLE.", "artist": "Kendrick Lamar", "link": "https://www.youtube.com/watch?v=tvTRZJ-4EyI"}
            ],
            [
                {"title": "Pink Venom", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=glhXCuM_Y7M"},
                {"title": "SICKO MODE", "artist": "Travis Scott", "link": "https://www.youtube.com/watch?v=d-JBBNg8YKs"},
                {"title": "MIC Drop", "artist": "BTS (Steve Aoki Remix)", "link": "https://www.youtube.com/watch?v=kTlv5_i8ICM"}
            ],
            [
                {"title": "Run BTS", "artist": "BTS", "link": "https://www.youtube.com/watch?v=9tG70B3DLIY"},
                {"title": "How You Like That", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=ioNng23DkIM"},
                {"title": "Lose Yourself", "artist": "Eminem", "link": "https://www.youtube.com/watch?v=_Yhyp_hXnyU"}
            ]
        ]
    }
    return pd.DataFrame(data)

df = load_course_data()

# ============================================================
# 4. HELPER FUNCTIONS
# ============================================================
def get_route_coordinates(center_lat, center_lng, course_idx):
    """Generate realistic route coordinates with elevation-based coloring."""
    routes = {
        0: {  # Yeouido - Flat riverside
            "coords": [
                [37.5289, 126.9331], [37.5312, 126.9295], [37.5338, 126.9252],
                [37.5360, 126.9210], [37.5342, 126.9185], [37.5315, 126.9220],
                [37.5285, 126.9270], [37.5262, 126.9315], [37.5289, 126.9331]
            ],
            "colors": ["#34C759"] * 8
        },
        1: {  # Seokchon Lake
            "coords": [
                [37.5074, 127.1031], [37.5090, 127.1010], [37.5105, 127.0980],
                [37.5100, 127.0950], [37.5080, 127.0945], [37.5055, 127.0970],
                [37.5050, 127.1010], [37.5065, 127.1040], [37.5074, 127.1031]
            ],
            "colors": ["#34C759", "#34C759", "#34C759", "#FF9500", "#34C759", "#34C759", "#34C759", "#34C759"]
        },
        3: {  # Namsan
            "coords": [
                [37.5509, 126.9909], [37.5490, 126.9940], [37.5465, 126.9930],
                [37.5440, 126.9890], [37.5460, 126.9830], [37.5495, 126.9810],
                [37.5525, 126.9850], [37.5530, 126.9890], [37.5509, 126.9909]
            ],
            "colors": ["#34C759", "#FF9500", "#FF3B30", "#FF9500", "#34C759", "#34C759", "#FF9500", "#FF3B30"]
        },
        4: {  # Yangjaecheon
            "coords": [
                [37.4934, 127.0601], [37.4950, 127.0650], [37.4975, 127.0720],
                [37.5002, 127.0790], [37.4990, 127.0810], [37.4960, 127.0740],
                [37.4935, 127.0670], [37.4915, 127.0615], [37.4934, 127.0601]
            ],
            "colors": ["#34C759"] * 8
        },
        5: {  # Dream Forest
            "coords": [
                [37.6257, 127.0371], [37.6235, 127.0395], [37.6210, 127.0410],
                [37.6190, 127.0380], [37.6205, 127.0340], [37.6230, 127.0325],
                [37.6250, 127.0350], [37.6257, 127.0371]
            ],
            "colors": ["#FF9500", "#FF3B30", "#FF3B30", "#FF9500", "#34C759", "#34C759", "#FF9500", "#FF9500"]
        },
        6: {  # Inwangsan
            "coords": [
                [37.5758, 126.9583], [37.5785, 126.9550], [37.5810, 126.9535],
                [37.5845, 126.9560], [37.5860, 126.9600], [37.5830, 126.9630],
                [37.5795, 126.9615], [37.5758, 126.9583]
            ],
            "colors": ["#FF9500", "#FF3B30", "#FF3B30", "#FF3B30", "#FF3B30", "#FF9500", "#FF9500", "#FF9500"]
        }
    }
    
    if course_idx in routes:
        return routes[course_idx]
    else:
        return {
            "coords": [
                [center_lat, center_lng],
                [center_lat + 0.002, center_lng + 0.001],
                [center_lat + 0.003, center_lng + 0.004],
                [center_lat + 0.001, center_lng + 0.005],
                [center_lat - 0.001, center_lng + 0.003],
                [center_lat, center_lng]
            ],
            "colors": ["#34C759", "#FF9500", "#FF3B30", "#FF9500", "#34C759", "#34C759"]
        }

def get_level_badge(level):
    """Return HTML for level badge."""
    badges = {
        "Beginner": '<span class="level-badge level-beginner">🌱 Beginner</span>',
        "Intermediate": '<span class="level-badge level-intermediate">🔥 Intermediate</span>',
        "Advanced": '<span class="level-badge level-advanced">⚡ Advanced</span>'
    }
    return badges.get(level, "")

def get_difficulty_stars(level):
    """Return difficulty indicator."""
    stars = {"Beginner": "●○○", "Intermediate": "●●○", "Advanced": "●●●"}
    return stars.get(level, "○○○")

def get_current_weather():
    """Simulated weather data for Seoul."""
    return {
        "temp": 22,
        "condition": "Partly Cloudy",
        "humidity": 45,
        "wind": 8,
        "running_score": 92,
        "recommendation": "Excellent conditions for running"
    }

# ============================================================
# 5. PAGE: WELCOME
# ============================================================
if st.session_state.page_stage == "welcome":
    st.markdown("""
        <div class="hero-section">
            <div class="hero-badge">✨ Personalized Running Intelligence</div>
            <div class="hero-title">Run-Step</div>
            <div class="hero-subtitle">
                Discover your perfect running route in Seoul. 
                AI-powered recommendations based on your fitness level, 
                complete with real-time terrain analysis and lifestyle integration.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="premium-card" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 16px;">🗺️</div>
                <h3 style="margin-bottom: 8px;">Smart Route Mapping</h3>
                <p style="font-size: 0.9rem; color: #6A6A6A;">
                    Real-time terrain visualization with elevation grading
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="premium-card" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 16px;">🎵</div>
                <h3 style="margin-bottom: 8px;">BPM-Matched Playlists</h3>
                <p style="font-size: 0.9rem; color: #6A6A6A;">
                    Curated music synced to your running cadence
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="premium-card" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 16px;">☕</div>
                <h3 style="margin-bottom: 8px;">Post-Run Hotspots</h3>
                <p style="font-size: 0.9rem; color: #6A6A6A;">
                    Handpicked cafes and restaurants for recovery
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        if st.button("Start Your Journey →", use_container_width=True):
            st.session_state.page_stage = "survey"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; padding: 20px; color: #8A8A8A; font-size: 0.85rem;">
            <strong>Arts and Big Data</strong> · Sungkyunkwan University<br>
            Developed by Yeonhu Lee (2024314274)
        </div>
    """, unsafe_allow_html=True)

# ============================================================
# 6. PAGE: SURVEY
# ============================================================
elif st.session_state.page_stage == "survey":
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>Find Your Perfect Route</h1>
            <p style="font-size: 1.1rem; color: #6A6A6A;">
                Answer two quick questions to unlock personalized recommendations
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="premium-card">
                <div class="section-header">
                    <div class="section-icon">⏱️</div>
                    <h3 style="margin: 0;">Your Pace</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        user_pace = st.selectbox(
            "Average pace per kilometer",
            ["Select your pace...", 
             "Over 7 min/km (Easy jog)", 
             "5-6 min/km (Steady run)", 
             "Under 5 min/km (Fast pace)"],
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("""
            <div class="premium-card">
                <div class="section-header">
                    <div class="section-icon">📅</div>
                    <h3 style="margin: 0;">Experience</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        user_experience = st.selectbox(
            "Running experience",
            ["Select your experience...",
             "Less than 1 month",
             "1-6 months",
             "More than 6 months"],
            label_visibility="collapsed"
        )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        if st.button("Get My Recommendations →", use_container_width=True):
            if user_pace == "Select your pace..." or user_experience == "Select your experience...":
                st.error("Please complete both questions to continue.")
            else:
                if "Over 7" in user_pace or "Less than 1" in user_experience:
                    st.session_state.user_level = "Beginner"
                elif "Under 5" in user_pace or "More than 6" in user_experience:
                    st.session_state.user_level = "Advanced"
                else:
                    st.session_state.user_level = "Intermediate"
                
                st.session_state.page_stage = "dashboard"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_back = st.columns([1, 3, 1])[0]
    with col_back:
        if st.button("← Back"):
            st.session_state.page_stage = "welcome"
            st.rerun()

# ============================================================
# 7. PAGE: DASHBOARD
# ============================================================
else:
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    
    with header_col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                <h1 style="margin: 0;">Your Routes</h1>
                {get_level_badge(st.session_state.user_level)}
            </div>
        """, unsafe_allow_html=True)
    
    with header_col2:
        new_level = st.selectbox(
            "Switch Level",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.user_level),
            label_visibility="collapsed"
        )
        if new_level != st.session_state.user_level:
            st.session_state.user_level = new_level
            st.rerun()
    
    with header_col3:
        if st.button("← Retake Quiz"):
            st.session_state.page_stage = "welcome"
            st.rerun()
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    weather = get_current_weather()
    st.markdown(f"""
        <div class="weather-widget" style="margin-bottom: 24px;">
            <div style="font-size: 2rem;">☀️</div>
            <div>
                <div class="weather-temp">{weather['temp']}°C</div>
                <div class="weather-info">{weather['condition']}</div>
            </div>
            <div style="margin-left: auto; text-align: right;">
                <div style="font-size: 1.5rem; font-weight: 700;">{weather['running_score']}</div>
                <div class="weather-info">Run Score</div>
            </div>
            <div style="margin-left: 24px; padding-left: 24px; border-left: 1px solid rgba(255,255,255,0.25);">
                <div class="weather-info">💧 {weather['humidity']}% humidity</div>
                <div class="weather-info">💨 {weather['wind']} km/h wind</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    filtered_df = df[df["Level"] == st.session_state.user_level]
    
    tab_names = [row['Course_Name'] for _, row in filtered_df.iterrows()]
    tabs = st.tabs(tab_names)
    
    for tab_idx, (df_idx, row) in enumerate(filtered_df.iterrows()):
        with tabs[tab_idx]:
            st.markdown(f"""
                <div style="margin-bottom: 24px;">
                    <h2 style="margin-bottom: 4px;">{row['Course_Name']}</h2>
                    <p style="color: #86868B; font-size: 0.95rem;">{row['Course_Name_KR']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            m1, m2, m3, m4, m5 = st.columns(5)
            
            with m1:
                st.markdown(f"""
                    <div class="metric-container metric-accent">
                        <div class="metric-value">{row['Distance_KM']}</div>
                        <div class="metric-label">Kilometers</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with m2:
                st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{row['Estimated_Time'].split('-')[0]}</div>
                        <div class="metric-label">Est. Minutes</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with m3:
                st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{row['Calories']}</div>
                        <div class="metric-label">Calories</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with m4:
                st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{row['Elevation_Gain']}m</div>
                        <div class="metric-label">Elevation</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with m5:
                st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-value">{row['Water_Fountains']}</div>
                        <div class="metric-label">Water Stops</div>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            tags = [
                f"🏃 {row['Surface']} Surface",
                f"🌳 {row['Shade_Level']} Shade",
                f"🚻 {row['Restrooms']} Restrooms",
                f"⏰ Best: {row['Best_Time']}",
                f"👥 {row['Crowd_Level']} Traffic"
            ]
            
            st.markdown(
                "".join([f'<span class="tag-pill">{tag}</span>' for tag in tags]),
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            pros_col, cons_col = st.columns(2)
            
            with pros_col:
                st.markdown(f"""
                    <div class="premium-card" style="border-left: 4px solid #34C759;">
                        <h3 style="color: #34C759; margin-bottom: 12px;">✓ Highlights</h3>
                        <p style="font-size: 0.95rem; line-height: 1.7;">{row['Pros']}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with cons_col:
                st.markdown(f"""
                    <div class="premium-card" style="border-left: 4px solid #FF9500;">
                        <h3 style="color: #FF9500; margin-bottom: 12px;">⚠ Considerations</h3>
                        <p style="font-size: 0.95rem; line-height: 1.7;">{row['Cons']}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div class="section-header">
                    <div class="section-icon">🗺️</div>
                    <div>
                        <h3 style="margin: 0;">Route Map</h3>
                        <p style="margin: 0; font-size: 0.85rem; color: #86868B;">
                            🟢 Flat · 🟡 Moderate · 🔴 Steep
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            m = folium.Map(
                location=row['Map_Center'],
                zoom_start=15,
                tiles="CartoDB positron"
            )
            
            route_data = get_route_coordinates(row['Map_Center'][0], row['Map_Center'][1], df_idx)
            coords = route_data["coords"]
            colors = route_data["colors"]
            
            for i in range(len(coords) - 1):
                folium.PolyLine(
                    locations=[coords[i], coords[i + 1]],
                    color=colors[i],
                    weight=6,
                    opacity=0.9
                ).add_to(m)
            
            folium.Marker(
                location=row['Map_Center'],
                popup="Start / Finish",
                icon=folium.Icon(color="black", icon="play", prefix="fa")
            ).add_to(m)
            
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st_folium(m, width=None, height=400, key=f"map_{tab_idx}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            st.markdown("""
                <div class="section-header">
                    <div class="section-icon">☕</div>
                    <h3 style="margin: 0;">Post-Run Refuel</h3>
                </div>
            """, unsafe_allow_html=True)
            
            spot_col1, spot_col2 = st.columns(2)
            
            # Integrated Hotspot Component Block (Fixed Spacing Bug)
            for spot_idx, (spot, col) in enumerate(zip(row['Spots'], [spot_col1, spot_col2])):
                with col:
                    st.markdown(f"""
                        <div class="spot-card">
                            <div class="spot-header-group">
                                <div class="spot-name">{spot['name']}</div>
                                <div style="font-size: 0.825rem; color: #86868B; font-weight: 500;">{spot['name_kr']}</div>
                                <div class="spot-tags">{spot['tags']}</div>
                            </div>
                            <div class="spot-action-container">
                                <a href="{spot['map']}" target="_blank" class="spot-link-btn">🗺️ View on Google Maps</a>
                                <a href="{spot['insta']}" target="_blank" class="spot-link-btn">📸 View on Instagram</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="section-header">
                    <div class="section-icon">🎵</div>
                    <div>
                        <h3 style="margin: 0;">{row['Playlist_Title']}</h3>
                        <p style="margin: 0; font-size: 0.85rem; color: #86868B;">
                            {row['Playlist_BPM']} BPM · Optimized for your pace
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            for track in row['Playlist_Tracks']:
                st.markdown(f"""
                    <div class="player-card">
                        <div class="player-artwork">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                                <path d="M12 3V13.55C11.41 13.21 10.73 13 10 13C7.79 13 6 14.79 6 17C6 19.21 7.79 21 10 21C12.21 21 14 19.21 14 17V7H18V3H12Z" fill="#FFFFFF"/>
                            </svg>
                        </div>
                        <div class="player-info">
                            <div class="player-title">{track['title']}</div>
                            <div class="player-artist">{track['artist']}</div>
                        </div>
                        <a href="{track['link']}" target="_blank" class="play-button">▶ Play</a>
                    </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 20px; color: #86868B; font-size: 0.8rem;">
            <strong>Run-Step</strong> v2.0 · Built with Streamlit<br>
            Yeonhu Lee · Sungkyunkwan University · 2024314274
        </div>
    """, unsafe_allow_html=True)

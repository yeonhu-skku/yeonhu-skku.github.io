import streamlit as st
import pandas as pd
import folium
import altair as alt
from streamlit_folium import st_folium
import math

def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        .stApp {
            background: linear-gradient(180deg, #FAFAF8 0%, #F5F3EE 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        h1 { font-size: 2.75rem !important; font-weight: 800 !important; letter-spacing: -0.03em !important; color: #1A1A1A !important; line-height: 1.1 !important; }
        h2 { font-size: 1.5rem !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: #1A1A1A !important; }
        h3 { font-size: 1.125rem !important; font-weight: 600 !important; color: #2D2D2D !important; }
        p, .stMarkdown { color: #4A4A4A; line-height: 1.6; }
        
        .premium-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .premium-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.04);
        }
        
        .metric-container {
            background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%);
            border-radius: 16px;
            padding: 20px 24px;
            text-align: center;
            transition: transform 0.2s ease;
        }
        .metric-container:hover { transform: scale(1.02); }
        .metric-value { font-size: 2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 4px; }
        .metric-label { font-size: 0.75rem; font-weight: 600; color: rgba(255, 255, 255, 0.6); text-transform: uppercase; letter-spacing: 0.08em; }
        
        .metric-accent { background: linear-gradient(135deg, #E85A3C 0%, #D64A2C 100%); }
        
        .tag-pill {
            display: inline-block; background: #F0EDE6; color: #5C5C5C;
            padding: 6px 14px; border-radius: 20px; font-size: 0.8rem;
            font-weight: 500; margin: 4px 4px 4px 0; transition: all 0.2s ease;
        }
        .tag-pill:hover { background: #E8E4DC; color: #3A3A3A; }
        
        .level-badge {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 8px 16px; border-radius: 24px; font-size: 0.85rem;
            font-weight: 600; letter-spacing: -0.01em;
        }
        .level-beginner { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); color: #2E7D32; }
        .level-intermediate { background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); color: #E65100; }
        .level-advanced { background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%); color: #C62828; }
        
        .player-card {
            display: flex; align-items: center; background: #FFFFFF;
            border-radius: 14px; padding: 16px 20px; margin-bottom: 10px;
            border: 1px solid #F0EDE6; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .player-card:hover { background: #FAFAF8; border-color: #E8E4DC; transform: translateX(4px); }
        .player-artwork {
            width: 52px; height: 52px; background: linear-gradient(135deg, #1A1A1A 0%, #3D3D3D 100%);
            border-radius: 10px; display: flex; align-items: center; justify-content: center;
            margin-right: 16px; flex-shrink: 0;
        }
        .player-info { flex-grow: 1; min-width: 0; }
        .player-title { font-size: 0.95rem; font-weight: 600; color: #1A1A1A; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .player-artist { font-size: 0.8rem; color: #8A8A8A; font-weight: 500; }
        
        .play-button {
            background: #1A1A1A; color: #FFFFFF !important; padding: 10px 20px;
            border-radius: 24px; text-decoration: none !important; font-size: 0.8rem;
            font-weight: 600; transition: all 0.2s ease; flex-shrink: 0;
        }
        .play-button:hover { background: #E85A3C; transform: scale(1.05); }
        
        .spot-card {
            background: #FFFFFF; border-radius: 16px; padding: 24px;
            border: 1px solid #F0EDE6; height: 100%; transition: all 0.3s ease;
        }
        .spot-card:hover { border-color: #E85A3C; box-shadow: 0 8px 30px rgba(232, 90, 60, 0.1); }
        .spot-name { font-size: 1.1rem; font-weight: 700; color: #1A1A1A; margin-bottom: 12px; }
        .spot-tags { font-size: 0.8rem; color: #8A8A8A; line-height: 1.5; margin-bottom: 16px; }
        
        .stButton > button {
            background: #1A1A1A !important; color: #FFFFFF !important; border: none !important;
            border-radius: 28px !important; padding: 14px 36px !important; font-weight: 600 !important;
            font-size: 0.95rem !important; letter-spacing: -0.01em !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15) !important;
        }
        .stButton > button:hover {
            background: #E85A3C !important; transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(232, 90, 60, 0.3) !important;
        }
        
        .stLinkButton > a {
            background: transparent !important; color: #1A1A1A !important; border: 2px solid #E8E4DC !important;
            border-radius: 24px !important; padding: 10px 20px !important; font-weight: 600 !important;
            font-size: 0.85rem !important; transition: all 0.2s ease !important;
        }
        .stLinkButton > a:hover { border-color: #1A1A1A !important; background: #1A1A1A !important; color: #FFFFFF !important; }
        
        .stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; padding: 4px; }
        .stTabs [data-baseweb="tab"] {
            background: #F0EDE6 !important; border-radius: 12px !important; padding: 12px 24px !important;
            font-weight: 600 !important; font-size: 0.9rem !important; color: #5C5C5C !important;
            border: none !important; transition: all 0.2s ease !important;
        }
        .stTabs [data-baseweb="tab"]:hover { background: #E8E4DC !important; color: #1A1A1A !important; }
        .stTabs [aria-selected="true"] { background: #1A1A1A !important; color: #FFFFFF !important; }
        .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
        
        .stSelectbox [data-baseweb="select"] { background: #FFFFFF; border-radius: 12px; border: 2px solid #E8E4DC; }
        .stSelectbox [data-baseweb="select"]:focus-within { border-color: #1A1A1A; }
        
        .custom-divider { height: 1px; background: linear-gradient(90deg, transparent, #E8E4DC, transparent); margin: 32px 0; }
        
        .hero-section { text-align: center; padding: 60px 20px 40px; }
        .hero-title { font-size: 3.5rem; font-weight: 800; letter-spacing: -0.04em; color: #1A1A1A; margin-bottom: 16px; line-height: 1; }
        .hero-subtitle { font-size: 1.25rem; color: #6A6A6A; font-weight: 400; max-width: 600px; margin: 0 auto 40px; line-height: 1.6; }
        .hero-badge {
            display: inline-flex; align-items: center; gap: 8px; background: rgba(232, 90, 60, 0.1);
            color: #E85A3C; padding: 8px 16px; border-radius: 20px; font-size: 0.85rem;
            font-weight: 600; margin-bottom: 24px;
        }
        
        .weather-widget { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px; padding: 20px 24px; color: white; display: flex; align-items: center; gap: 16px; }
        .weather-temp { font-size: 2.5rem; font-weight: 700; }
        .weather-info { font-size: 0.9rem; opacity: 0.9; }
        
        .map-container { border-radius: 20px; overflow: hidden; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); }
        .section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
        .section-icon { width: 40px; height: 40px; background: #F0EDE6; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    if "page_stage" not in st.session_state:
        st.session_state.page_stage = "welcome"
    if "user_level" not in st.session_state:
        st.session_state.user_level = "Beginner"

@st.cache_data
def load_course_data() -> pd.DataFrame:
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["Yeouido Hangang Park", "Seokchon Lake", "Neighborhood Park", "Namsan Dulle-gil", "Yangjaecheon Stream", "Dream Forest", "Inwangsan Trail", "Ttukseom Hangang Park", "Buamdong Hills"],
        "Course_Name_KR": ["여의도 한강공원", "석촌호수", "동네 근린공원", "남산 둘레길", "양재천", "북서울꿈의숲", "인왕산", "뚝섬 한강공원", "부암동"],
        "Distance_KM": [3.0, 2.5, 2.0, 7.0, 8.5, 5.0, 12.0, 21.0, 15.0],
        "Estimated_Time": ["25-30 min", "20-25 min", "15-20 min", "50-60 min", "60-75 min", "40-50 min", "90-120 min", "150-180 min", "120-150 min"],
        "Calories": [180, 150, 120, 450, 550, 320, 900, 1600, 1200],
        "Elevation_Gain": [5, 3, 2, 120, 45, 85, 280, 50, 320],
        "Elevation_Desc": ["Flat", "Flat", "Flat", "Moderate", "Low", "Moderate", "Steep", "Varied", "Very Steep"],
        "Surface": ["Paved", "Paved", "Paved", "Mixed", "Paved", "Mixed", "Trail", "Paved", "Trail"],
        "Shade_Level": ["Low", "Medium", "Medium", "High", "Low", "High", "High", "Low", "Medium"],
        "Water_Fountains": [8, 4, 2, 6, 12, 5, 3, 15, 2],
        "Restrooms": [6, 3, 1, 4, 8, 4, 2, 10, 1],
        "Best_Time": ["Evening", "Night", "Morning", "Morning", "Evening", "Afternoon", "Morning", "Evening", "Morning"],
        "Crowd_Level": ["High", "High", "Low", "Medium", "Medium", "Low", "Low", "High", "Low"],
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
            "High volume of bicycle traffic requires constant awareness. Can be crowded on weekends. Limited shade during summer.",
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
                {"name": "All That's Morning", "name_kr": "세상의모든아침", "tags": "Brunch · Hotel View · Carb Refuel", "map": "https://maps.google.com/?q=세상의모든아침+여의도점", "insta": "https://www.instagram.com/all_thats_morning/"},
                {"name": "Cafe Jinjeongseong", "name_kr": "카페 진정성", "tags": "Milk Tea · Modern · Instagram Hot", "map": "https://maps.google.com/?q=카페+진정성+여의도점", "insta": "https://www.instagram.com/cafe_jinjungsung/"}
            ],
            [
                {"name": "Vrewcleans", "name_kr": "뷰클런즈", "tags": "Songlidangil · Wood Interior · Iced Tea", "map": "https://maps.google.com/?q=뷰클런즈", "insta": "https://www.instagram.com/vrewcleans/"},
                {"name": "Knickerbocker Bagel", "name_kr": "니커버커베이글", "tags": "NYC Style · Carb Heaven · Lake View", "map": "https://maps.google.com/?q=니커버커베이글+송파점", "insta": "https://www.instagram.com/knickerbockerbagel_korea/"}
            ],
            [
                {"name": "Paris Baguette Local", "name_kr": "파리바게뜨", "tags": "Fresh Sandwich · Protein · Accessible", "map": "https://maps.google.com/?q=파리바게뜨", "insta": "https://www.instagram.com/parisbaguette_kr/"},
                {"name": "Ediya Coffee", "name_kr": "이디야커피", "tags": "Iced Americano · Quick Hydration", "map": "https://maps.google.com/?q=이디야커피", "insta": "https://www.instagram.com/ediya.coffee/"}
            ],
            [
                {"name": "101 Namsan Tonkatsu", "name_kr": "101번지 남산돈까스", "tags": "Classic · Protein Refuel · Must-Try", "map": "https://maps.google.com/?q=101번지+남산돈까스", "insta": "https://www.instagram.com/explore/tags/남산돈까스/"},
                {"name": "Yijungsaengup", "name_kr": "이중생업", "tags": "Korean Fusion · Clean Pasta · Date Spot", "map": "https://maps.google.com/?q=이중생업+남산", "insta": "https://www.instagram.com/explore/tags/남산맛집/"}
            ],
            [
                {"name": "Room Service 301", "name_kr": "룸서비스301", "tags": "Forest View · Dessert Cafe · Aesthetic", "map": "https://maps.google.com/?q=룸서비스301", "insta": "https://www.instagram.com/roomservice301/"},
                {"name": "Cattle & Bee", "name_kr": "캐틀앤비", "tags": "Italian Brunch · Terrace · Dogok", "map": "https://maps.google.com/?q=캐틀앤비+양재점", "insta": "https://www.instagram.com/cattle_bee/"}
            ],
            [
                {"name": "La Foresta", "name_kr": "라포레스타", "tags": "Pizza & Pasta · Green View · Family", "map": "https://maps.google.com/?q=라포레스타", "insta": "https://www.instagram.com/explore/tags/라포레스타/"},
                {"name": "Dream Forest Museum Cafe", "name_kr": "꿈의숲 미술관 카페", "tags": "Observatory · Smoothie · Culture", "map": "https://maps.google.com/?q=북서울꿈의숲", "insta": "https://www.instagram.com/explore/tags/북서울꿈의숲/"}
            ],
            [
                {"name": "H Lounge Seochon", "name_kr": "H라운지", "tags": "Italian · Garden Terrace · Post-Hike", "map": "https://maps.google.com/?q=H라운지", "insta": "https://www.instagram.com/explore/tags/서촌브런치/"},
                {"name": "Staff Picks", "name_kr": "스태픽스", "tags": "Outdoor Terrace · Ginkgo · Runner Haven", "map": "https://maps.google.com/?q=스태픽스", "insta": "https://www.instagram.com/staffpicks_official/"}
            ],
            [
                {"name": "Agu Agu Ttukseom", "name_kr": "아구아구", "tags": "Fresh Salad Bowl · Light Meal · Healthy", "map": "https://maps.google.com/?q=아구아구+뚝섬", "insta": "https://www.instagram.com/explore/tags/뚝섬맛집/"},
                {"name": "Riverside Convenience Store", "name_kr": "한강공원 편의점", "tags": "Powerade · Ice Cup · Instant Ramyun", "map": "https://maps.google.com/?q=뚝섬한강공원", "insta": "https://www.instagram.com/explore/tags/뚝섬한강공원/"}
            ],
            [
                {"name": "Club Espresso", "name_kr": "클럽에스프레소", "tags": "Drip Coffee · Cyclist Haven · Classic", "map": "https://maps.google.com/?q=클럽에스프레소", "insta": "https://www.instagram.com/clubespresso/"},
                {"name": "Gyeyalsa Chicken", "name_kr": "계열사", "tags": "Seoul Top 3 Chicken · Protein Reward", "map": "https://maps.google.com/?q=계열사+부암동", "insta": "https://www.instagram.com/explore/tags/계열사/"}
            ]
        ],
        "Playlist_Title": [
            "Chill Acoustic Breeze", "City Night Grooves", "Morning Warm-Up",
            "Mid-Tempo Rhythm", "Urban Bassline", "Cardio Booster",
            "K-Pop Energy", "Global Rap Pace", "Adrenaline Peak"
        ],
        "Playlist_BPM": ["100-120", "110-125", "105-120", "130-145", "135-150", "140-155", "150-170", "155-175", "160-180"],
        "Playlist_Tracks": [
            [{"title": "Paris in the Rain", "artist": "Lauv", "link": "https://www.youtube.com/watch?v=kOCkne-Bku4"}, {"title": "ILYSB", "artist": "LANY", "link": "https://www.youtube.com/watch?v=SSTp0rknOgA"}],
            [{"title": "Super Far", "artist": "LANY", "link": "https://www.youtube.com/watch?v=B88Zas_DclM"}, {"title": "Strawberries & Cigarettes", "artist": "Troye Sivan", "link": "https://www.youtube.com/watch?v=Z3LgC8u_R8Y"}],
            [{"title": "Feelings", "artist": "Lauv", "link": "https://www.youtube.com/watch?v=421w1jR-SgE"}, {"title": "Pink Skies", "artist": "LANY", "link": "https://www.youtube.com/watch?v=eE7T_I9vInU"}],
            [{"title": "Attention", "artist": "Charlie Puth", "link": "https://www.youtube.com/watch?v=nfs8NYg7yQM"}, {"title": "Shivers", "artist": "Ed Sheeran", "link": "https://www.youtube.com/watch?v=Il0S8BoucSA"}],
            [{"title": "How Long", "artist": "Charlie Puth", "link": "https://www.youtube.com/watch?v=TdylllyoV9c"}, {"title": "Unholy", "artist": "Sam Smith", "link": "https://www.youtube.com/watch?v=Uq9gPaizbe8"}],
            [{"title": "Shape of You", "artist": "Ed Sheeran", "link": "https://www.youtube.com/watch?v=JGwWNGJdvx8"}, {"title": "Diamonds", "artist": "Sam Smith", "link": "https://www.youtube.com/watch?v=8RvAKRoDB7o"}],
            [{"title": "Dynamite", "artist": "BTS", "link": "https://www.youtube.com/watch?v=gdZLi9oWNZg"}, {"title": "Kill This Love", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=2S24-y0Ij3Y"}],
            [{"title": "Pink Venom", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=glhXCuM_Y7M"}, {"title": "SICKO MODE", "artist": "Travis Scott", "link": "https://www.youtube.com/watch?v=d-JBBNg8YKs"}],
            [{"title": "Run BTS", "artist": "BTS", "link": "https://www.youtube.com/watch?v=9tG70B3DLIY"}, {"title": "How You Like That", "artist": "BLACKPINK", "link": "https://www.youtube.com/watch?v=ioNng23DkIM"}]
        ]
    }
    return pd.DataFrame(data)

def generate_elevation_data(distance: float, max_elevation: int) -> pd.DataFrame:
    points = 50
    x_vals = [i * (distance / points) for i in range(points + 1)]
    y_vals = [max(0, max_elevation * math.sin(math.pi * (i / points)) + (max_elevation * 0.1 * math.sin(3 * math.pi * (i / points)))) for i in range(points + 1)]
    return pd.DataFrame({"Distance (km)": x_vals, "Elevation (m)": y_vals})

def get_route_coordinates(center_lat: float, center_lng: float) -> dict:
    return {
        "coords": [
            [center_lat, center_lng],
            [center_lat + 0.002, center_lng + 0.001],
            [center_lat + 0.003, center_lng + 0.004],
            [center_lat + 0.001, center_lng + 0.005],
            [center_lat - 0.001, center_lng + 0.003],
            [center_lat, center_lng]
        ],
        "colors": ["#22C55E", "#F59E0B", "#EF4444", "#F59E0B", "#22C55E", "#22C55E"]
    }

def get_level_badge(level: str) -> str:
    badges = {
        "Beginner": '<span class="level-badge level-beginner">🌱 Beginner</span>',
        "Intermediate": '<span class="level-badge level-intermediate">🔥 Intermediate</span>',
        "Advanced": '<span class="level-badge level-advanced">⚡ Advanced</span>'
    }
    return badges.get(level, "")

def get_current_weather() -> dict:
    return {
        "temp": 22,
        "condition": "Partly Cloudy",
        "humidity": 45,
        "wind": 8,
        "running_score": 92
    }

def render_welcome_page():
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
                <p style="font-size: 0.9rem; color: #6A6A6A;">Terrain visualization with elevation profiles</p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class="premium-card" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 16px;">🎵</div>
                <h3 style="margin-bottom: 8px;">Cadence Sync</h3>
                <p style="font-size: 0.9rem; color: #6A6A6A;">Curated music targeted to your target BPM</p>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="premium-card" style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 16px;">☕</div>
                <h3 style="margin-bottom: 8px;">Recovery Zones</h3>
                <p style="font-size: 0.9rem; color: #6A6A6A;">Handpicked venues to refuel post-run</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_center = st.columns([1, 1, 1])[1]
    with col_center:
        if st.button("Start Your Journey →", use_container_width=True):
            st.session_state.page_stage = "survey"
            st.rerun()

def render_survey_page():
    st.markdown("""
        <div style="text-align: center; margin-bottom: 40px;">
            <h1>Find Your Perfect Route</h1>
            <p style="font-size: 1.1rem; color: #6A6A6A;">Answer two quick questions to unlock personalized recommendations</p>
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
        user_pace = st.selectbox("Average pace", ["Select your pace...", "Over 7 min/km (Easy jog)", "5-6 min/km (Steady run)", "Under 5 min/km (Fast pace)"], label_visibility="collapsed")
    with col2:
        st.markdown("""
            <div class="premium-card">
                <div class="section-header">
                    <div class="section-icon">📅</div>
                    <h3 style="margin: 0;">Experience</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
        user_experience = st.selectbox("Experience", ["Select your experience...", "Less than 1 month", "1-6 months", "More than 6 months"], label_visibility="collapsed")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_center = st.columns([1, 1, 1])[1]
    with col_center:
        if st.button("Get My Recommendations →", use_container_width=True):
            if user_pace == "Select your pace..." or user_experience == "Select your experience...":
                st.error("Please complete both questions.")
            else:
                if "Over 7" in user_pace or "Less than 1" in user_experience:
                    st.session_state.user_level = "Beginner"
                elif "Under 5" in user_pace or "More than 6" in user_experience:
                    st.session_state.user_level = "Advanced"
                else:
                    st.session_state.user_level = "Intermediate"
                st.session_state.page_stage = "dashboard"
                st.rerun()
                
    if st.columns([1, 3, 1])[0].button("← Back"):
        st.session_state.page_stage = "welcome"
        st.rerun()

def render_dashboard_page(df: pd.DataFrame):
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    with header_col1:
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 16px;">
                <h1 style="margin: 0;">Your Routes</h1>
                {get_level_badge(st.session_state.user_level)}
            </div>
        """, unsafe_allow_html=True)
    with header_col2:
        new_level = st.selectbox("Switch Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.user_level), label_visibility="collapsed")
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
            <div style="margin-left: 24px; padding-left: 24px; border-left: 1px solid rgba(255,255,255,0.3);">
                <div class="weather-info">💧 {weather['humidity']}% humidity</div>
                <div class="weather-info">💨 {weather['wind']} km/h wind</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    filtered_df = df[df["Level"] == st.session_state.user_level]
    tabs = st.tabs([row['Course_Name'] for _, row in filtered_df.iterrows()])
    
    for tab_idx, (_, row) in enumerate(filtered_df.iterrows()):
        with tabs[tab_idx]:
            st.markdown(f"""
                <div style="margin-bottom: 24px;">
                    <h2 style="margin-bottom: 4px;">{row['Course_Name']}</h2>
                    <p style="color: #8A8A8A; font-size: 0.95rem;">{row['Course_Name_KR']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            m1, m2, m3, m4, m5 = st.columns(5)
            metrics = [
                (m1, "metric-accent", row['Distance_KM'], "Kilometers"),
                (m2, "", row['Estimated_Time'].split('-')[0], "Est. Minutes"),
                (m3, "", row['Calories'], "Calories"),
                (m4, "", f"{row['Elevation_Gain']}m", "Elevation"),
                (m5, "", row['Water_Fountains'], "Water Stops")
            ]
            for col, cls, val, label in metrics:
                with col:
                    st.markdown(f'<div class="metric-container {cls}"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            tags = [f"🏃 {row['Surface']} Surface", f"🌳 {row['Shade_Level']} Shade", f"🚻 {row['Restrooms']} Restrooms", f"⏰ Best: {row['Best_Time']}", f"👥 {row['Crowd_Level']} Traffic"]
            st.markdown("".join([f'<span class="tag-pill">{tag}</span>' for tag in tags]), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            pros_col, cons_col = st.columns(2)
            with pros_col:
                st.markdown(f'<div class="premium-card" style="border-left: 4px solid #22C55E;"><h3 style="color: #22C55E; margin-bottom: 12px;">✓ Highlights</h3><p style="font-size: 0.95rem;">{row["Pros"]}</p></div>', unsafe_allow_html=True)
            with cons_col:
                st.markdown(f'<div class="premium-card" style="border-left: 4px solid #F59E0B;"><h3 style="color: #F59E0B; margin-bottom: 12px;">⚠ Considerations</h3><p style="font-size: 0.95rem;">{row["Cons"]}</p></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            map_col, chart_col = st.columns([3, 2])
            
            with map_col:
                st.markdown('<div class="section-header"><div class="section-icon">🗺️</div><div><h3 style="margin: 0;">Route Map</h3></div></div>', unsafe_allow_html=True)
                m = folium.Map(location=row['Map_Center'], zoom_start=15, tiles="CartoDB positron")
                route_data = get_route_coordinates(row['Map_Center'][0], row['Map_Center'][1])
                coords, colors = route_data["coords"], route_data["colors"]
                for i in range(len(coords) - 1):
                    folium.PolyLine(locations=[coords[i], coords[i + 1]], color=colors[i], weight=6, opacity=0.9).add_to(m)
                folium.Marker(location=row['Map_Center'], popup="Start / Finish", icon=folium.Icon(color="black", icon="play", prefix="fa")).add_to(m)
                
                st.markdown('<div class="map-container">', unsafe_allow_html=True)
                st_folium(m, width=None, height=350, key=f"map_{tab_idx}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with chart_col:
                st.markdown('<div class="section-header"><div class="section-icon">📈</div><div><h3 style="margin: 0;">Elevation Profile</h3></div></div>', unsafe_allow_html=True)
                elevation_df = generate_elevation_data(row['Distance_KM'], row['Elevation_Gain'])
                
                chart = alt.Chart(elevation_df).mark_area(
                    line={'color':'#E85A3C'}, color=alt.Gradient(
                        gradient='linear', stops=[alt.GradientStop(color='#E85A3C', offset=0), alt.GradientStop(color='white', offset=1)],
                        x1=1, x2=1, y1=1, y2=0
                    )
                ).encode(
                    x=alt.X('Distance (km)', title='Distance (km)', axis=alt.Axis(grid=False)),
                    y=alt.Y('Elevation (m)', title='Elevation (m)', axis=alt.Axis(grid=True)),
                    tooltip=['Distance (km)', 'Elevation (m)']
                ).properties(height=350).configure_view(strokeWidth=0)
                
                st.altair_chart(chart, use_container_width=True)
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="section-header"><div class="section-icon">☕</div><h3 style="margin: 0;">Post-Run Refuel</h3></div>', unsafe_allow_html=True)
            spot_cols = st.columns(2)
            for spot_idx, (spot, col) in enumerate(zip(row['Spots'], spot_cols)):
                with col:
                    st.markdown(f"""
                        <div class="spot-card" style="margin-bottom: 16px;">
                            <div class="spot-name">{spot['name']}</div>
                            <div style="font-size: 0.85rem; color: #6A6A6A; margin-bottom: 8px;">{spot['name_kr']}</div>
                            <div class="spot-tags">{spot['tags']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    btn_col1, btn_col2 = st.columns(2)
                    btn_col1.link_button("📍 Maps", spot['map'], use_container_width=True)
                    btn_col2.link_button("📸 Instagram", spot['insta'], use_container_width=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 20px; color: #8A8A8A; font-size: 0.8rem;">
            <strong>Run-Step</strong> v2.0 · Built with Streamlit<br>
            Yeonhu Lee · Sungkyunkwan University · 2024314274
        </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Run-Step | Seoul Running Guide", page_icon="🏃", layout="wide", initial_sidebar_state="collapsed")
    load_css()
    init_session_state()
    df = load_course_data()
    
    if st.session_state.page_stage == "welcome":
        render_welcome_page()
    elif st.session_state.page_stage == "survey":
        render_survey_page()
    else:
        render_dashboard_page(df)

if __name__ == "__main__":
    main()

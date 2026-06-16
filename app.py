import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import sqlite3
import hashlib
from datetime import datetime
import random
import math

# ============================================================
# 1. PAGE CONFIGURATION & CSS
# ============================================================
st.set_page_config(
    page_title="Run-Step Pro | Advanced Running Hub",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp { background: #F8F9FA; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #111827 !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
    .metric-card {
        background: white; border-radius: 16px; padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #E5E7EB;
        transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
    .weather-score-high { color: #10B981; font-weight: 800; font-size: 2.2rem; }
    .weather-score-med { color: #F59E0B; font-weight: 800; font-size: 2.2rem; }
    .weather-score-low { color: #EF4444; font-weight: 800; font-size: 2.2rem; }
    .yt-container { border-radius: 12px; overflow: hidden; margin-top: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. DATABASE MANAGER (OOP & Robust Error Handling)
# ============================================================
class DatabaseManager:
    def __init__(self, db_file='runstep_pro.db'):
        self.db_file = db_file
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_file)

    def _init_db(self):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS users 
                         (username TEXT PRIMARY KEY, password TEXT, level TEXT, weight REAL, join_date TEXT)''')
            c.execute('''CREATE TABLE IF NOT EXISTS run_history 
                         (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, course_name TEXT, 
                          distance REAL, calories INTEGER, run_date TEXT,
                          FOREIGN KEY(username) REFERENCES users(username))''')
            conn.commit()

    @staticmethod
    def make_hashes(password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    def check_hashes(self, password, hashed_text):
        return self.make_hashes(password) == hashed_text

    def add_user(self, username, password, level="Beginner", weight=65.0):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, level, weight, join_date) VALUES (?, ?, ?, ?, ?)",
                      (username, self.make_hashes(password), level, weight, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

    def login_user(self, username, password):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username = ?", (username,))
            data = c.fetchone()
            if data:
                return self.check_hashes(password, data[0])
            return False

    def get_user_data(self, username):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT level, weight, join_date FROM users WHERE username = ?", (username,))
            return c.fetchone()

    def add_run_history(self, username, course_name, distance, calories):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO run_history (username, course_name, distance, calories, run_date) VALUES (?, ?, ?, ?, ?)",
                      (username, course_name, distance, calories, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()

    def get_run_history(self, username):
        with self._get_conn() as conn:
            # Fixed query with explicit parameters to prevent pandas DatabaseError
            query = "SELECT course_name, distance, calories, run_date FROM run_history WHERE username = ? ORDER BY run_date DESC"
            df = pd.read_sql_query(query, conn, params=(username,))
            return df

db = DatabaseManager()

# ============================================================
# 3. EXTERNAL DATA & BUSINESS LOGIC
# ============================================================

def get_weather_data(lat, lon):
    # Simulated Advanced Environmental API Model
    base_temp = 20 + random.uniform(-4, 4)
    humidity = 45 + random.randint(-15, 20)
    pm10 = random.randint(10, 70)
    
    score = 100
    if base_temp > 26: score -= (base_temp - 26) * 2.5
    elif base_temp < 4: score -= (4 - base_temp) * 2.5
    if humidity > 75: score -= (humidity - 75) * 0.6
    if pm10 > 45: score -= (pm10 - 45) * 1.2
    
    score = max(0, min(100, int(score)))
    msg = "Optimal running conditions!" if score >= 80 else "Good conditions. Stay hydrated." if score >= 60 else "Tough conditions today. Pace yourself."
    
    return {"score": score, "temp": round(base_temp, 1), "humidity": round(humidity, 1), "pm10": round(pm10, 1), "msg": msg}

def calculate_calories(distance_km, user_level, user_weight):
    # METs (Metabolic Equivalent of Task) Calculation
    # Beginner (slower): ~8 METs, Advanced (faster): ~11 METs
    met = 8.0 if user_level == "Beginner" else 9.5 if user_level == "Intermediate" else 11.0
    # Estimated time in hours = distance / speed(km/h)
    speed = 8.0 if user_level == "Beginner" else 10.0 if user_level == "Intermediate" else 13.0
    time_hours = distance_km / speed
    calories = int(met * user_weight * time_hours)
    return calories

# ============================================================
# 4. DATA MODEL: DIVERSE COURSES & YOUTUBE EMBEDS
# ============================================================
@st.cache_data
def load_course_data():
    data = {
        "Course_ID": ["C001", "C002", "C003", "C004", "C005", "C006"],
        "Course_Name": [
            "Yeouido Hangang Track (Flat)", 
            "Namsan Summit Challenge (Steep)", 
            "Yangjaecheon Eco Trail (Mixed)",
            "Seoul Forest Loop (Beginner Friendly)",
            "Olympic Park Circuit (Hills)",
            "Banpo Bridge Night Run (Flat/View)"
        ],
        "Level": ["Beginner", "Advanced", "Intermediate", "Beginner", "Intermediate", "Beginner"],
        "Distance_KM": [5.0, 7.5, 10.0, 3.5, 6.0, 8.0],
        "Elevation_Type": ["Flat", "Mountain", "Rolling", "Flat", "Rolling", "Flat"],
        "Map_Center": [
            [37.5289, 126.9331], # Yeouido
            [37.5509, 126.9909], # Namsan
            [37.4934, 127.0601], # Yangjaecheon
            [37.5443, 127.0374], # Seoul Forest
            [37.5206, 127.1214], # Olympic Park
            [37.5111, 126.9972]  # Banpo
        ],
        # YouTube Running Playlists / POV Running Videos
        "YT_Video_ID": [
            "1y6smkh6c-0", # 120 BPM Running mix
            "DP7eH2E8fN4", # High Intensity / Motivation
            "jfKfPfyJRdk", # Lofi Eco run
            "5qap5aO4i9A", # Chill beginner pace
            "v7AYKMP6rOE", # 150 BPM energetic
            "1ZX_x4PntP0"  # Night run synthwave
        ]
    }
    return pd.DataFrame(data)

def get_youtube_embed(video_id):
    return f'''
    <div class="yt-container">
        <iframe width="100%" height="280" src="https://www.youtube.com/embed/{video_id}?autoplay=0&rel=0" 
        frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen></iframe>
    </div>
    '''

def get_geojson_route(course_id, center, elev_type):
    lat, lon = center
    coords = []
    steps = 40
    for i in range(steps):
        angle = (i / steps) * math.pi * 2
        # Create varied shapes based on elevation type
        r_mod = 0.015 if elev_type == "Flat" else 0.02 if elev_type == "Rolling" else 0.01
        coords.append([lat + math.sin(angle)*r_mod, lon + math.cos(angle)*r_mod*1.5])
    coords.append(coords[0])
    return coords

def plot_advanced_elevation(course_id, dist, elev_type):
    points = int(dist * 10)
    distances = [x * 0.1 for x in range(points)]
    
    if elev_type == "Flat":
        elevations = [10 + math.sin(x)*2 for x in distances]
    elif elev_type == "Mountain":
        elevations = [50 + (x * 25) if x < dist/2 else 50 + ((dist-x) * 25) for x in distances]
        elevations = [e + random.uniform(-5,5) for e in elevations]
    else: # Rolling
        elevations = [30 + math.sin(x/1.5)*20 + random.uniform(-2,2) for x in distances]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=distances, y=elevations, fill='tozeroy', mode='lines',
        line=dict(color='#3B82F6', width=3, shape='spline'),
        fillcolor='rgba(59, 130, 246, 0.15)',
        hovertemplate='Distance: %{x:.1f}km<br>Elevation: %{y:.0f}m<extra></extra>'
    ))
    fig.update_layout(
        title="Dynamic Elevation Profile", xaxis_title="Distance (km)", yaxis_title="Elevation (m)",
        height=280, margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#F3F4F6'), yaxis=dict(showgrid=True, gridcolor='#F3F4F6')
    )
    return fig

# ============================================================
# 5. APP ROUTING & MAIN INTERFACE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- SIDEBAR ---
with st.sidebar:
    st.title("Run-Step Pro ⚡")
    st.markdown("Data-driven running intelligence.")
    
    if not st.session_state.logged_in:
        menu = st.radio("Access Portal", ["Login", "Sign Up"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if menu == "Sign Up":
            level = st.selectbox("Running Level", ["Beginner", "Intermediate", "Advanced"])
            weight = st.number_input("Weight (kg) - For Calories", min_value=30.0, max_value=150.0, value=65.0)
            if st.button("Create Account", use_container_width=True):
                if username and password:
                    try:
                        db.add_user(username, password, level, weight)
                        st.success("Account created! Please switch to Login.")
                    except sqlite3.IntegrityError:
                        st.error("Username already taken.")
                else:
                    st.error("Please fill all fields.")
                    
        elif menu == "Login":
            if st.button("Authenticate", use_container_width=True):
                if db.login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    else:
        st.success(f"Logged in as **{st.session_state.username}**")
        app_mode = st.radio("Navigation", ["Dashboard", "Explore Routes"])
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

# --- MAIN WORKSPACE ---
if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; padding: 120px 20px;">
            <h1 style="font-size: 4rem; color: #111827;">Master Your Pace.</h1>
            <p style="font-size: 1.25rem; color: #6B7280; max-width: 600px; margin: 20px auto;">
                Authenticate via the sidebar to access dynamically generated courses, physiological metrics, and spatial routing.
            </p>
        </div>
    """, unsafe_allow_html=True)

else:
    user_data = db.get_user_data(st.session_state.username)
    user_level = user_data[0]
    user_weight = user_data[1]
    
    if app_mode == "Dashboard":
        st.header("Analytics Dashboard")
        
        history_df = db.get_run_history(st.session_state.username)
        total_dist = history_df['distance'].sum() if not history_df.empty else 0.0
        total_cal = history_df['calories'].sum() if not history_df.empty else 0
        
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><p style="color:#6B7280; margin:0;">Total Distance</p><h2 style="margin:5px 0; color:#3B82F6;">{total_dist:.1f} km</h2></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><p style="color:#6B7280; margin:0;">Total Calories</p><h2 style="margin:5px 0; color:#10B981;">{total_cal:,} kcal</h2></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><p style="color:#6B7280; margin:0;">Recorded Runs</p><h2 style="margin:5px 0;">{len(history_df)}</h2></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><p style="color:#6B7280; margin:0;">Current Profile</p><h2 style="margin:5px 0;">{user_level}</h2></div>', unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Training Ledger")
        if history_df.empty:
            st.info("No logs found. Head to 'Explore Routes' to record your first session.")
        else:
            # Display clean dataframe
            st.dataframe(history_df.style.format({"distance": "{:.1f} km", "calories": "{:,} kcal"}), use_container_width=True)

    elif app_mode == "Explore Routes":
        st.header("Route Intelligence")
        df = load_course_data()
        
        # Course Filtering
        c_filter1, c_filter2 = st.columns([1, 2])
        with c_filter1:
            level_filter = st.selectbox("Filter by Difficulty", ["All", "Beginner", "Intermediate", "Advanced"], index=["All", "Beginner", "Intermediate", "Advanced"].index("All"))
        
        filtered_df = df if level_filter == "All" else df[df['Level'] == level_filter]
        
        with c_filter2:
            if filtered_df.empty:
                st.warning("No courses match this difficulty. Showing all.")
                filtered_df = df
            selected_course_name = st.selectbox("Select Target Course", filtered_df['Course_Name'].tolist())
            
        course = filtered_df[filtered_df['Course_Name'] == selected_course_name].iloc[0]
        
        # --- 1. Real-time Environment Analysis ---
        st.subheader("Live Environment Matrix")
        weather = get_weather_data(course['Map_Center'][0], course['Map_Center'][1])
        score_class = "weather-score-high" if weather['score'] >= 80 else "weather-score-med" if weather['score'] >= 60 else "weather-score-low"
        
        w1, w2, w3, w4 = st.columns(4)
        w1.markdown(f'<div class="metric-card" style="text-align:center;"><p style="margin:0;color:#6B7280;">Condition Score</p><div class="{score_class}">{weather["score"]}</div></div>', unsafe_allow_html=True)
        w2.metric("Temperature", f"{weather['temp']} °C")
        w3.metric("Humidity", f"{weather['humidity']} %")
        w4.metric("PM10 (Dust)", f"{weather['pm10']} µg/m³")
        st.caption(f"💡 AI Insight: {weather['msg']}")
        
        st.markdown("<hr style='border-top: 1px solid #E5E7EB; margin: 30px 0;'>", unsafe_allow_html=True)
        
        # --- 2. Spatial & Audiovisual Integration ---
        col_map, col_chart = st.columns([1.3, 1])
        
        with col_map:
            st.subheader("Spatial Route")
            m = folium.Map(location=course['Map_Center'], zoom_start=14, tiles="CartoDB positron")
            coords = get_geojson_route(course['Course_ID'], course['Map_Center'], course['Elevation_Type'])
            folium.PolyLine(coords, color="#3B82F6", weight=6, opacity=0.8).add_to(m)
            
            # Start/End Marker
            folium.Marker(course['Map_Center'], tooltip="Start/End Point", icon=folium.Icon(color="green", icon="play")).add_to(m)
            st_folium(m, width=None, height=350)
            
        with col_chart:
            st.subheader("Terrain & Energy")
            # Calculate dynamic calories based on user weight and level
            est_cal = calculate_calories(course['Distance_KM'], user_level, user_weight)
            
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                    <div><strong>Distance:</strong> {course['Distance_KM']} km</div>
                    <div><strong>Est. Burn:</strong> <span style="color:#10B981; font-weight:bold;">{est_cal} kcal</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            st.plotly_chart(plot_advanced_elevation(course['Course_ID'], course['Distance_KM'], course['Elevation_Type']), use_container_width=True)
            
            st.subheader("Audio/Pace Guide")
            st.markdown(get_youtube_embed(course['YT_Video_ID']), unsafe_allow_html=True)
            
        # --- 3. Execution Action ---
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✓ Record this Session to Ledger", type="primary", use_container_width=True):
            db.add_run_history(st.session_state.username, course['Course_Name'], course['Distance_KM'], est_cal)
            st.success(f"Successfully logged {course['Distance_KM']}km ({est_cal} kcal). Check your Dashboard!")

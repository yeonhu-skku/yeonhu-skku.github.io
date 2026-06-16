import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import requests
import sqlite3
import hashlib
from datetime import datetime
import json
import random

# ============================================================
# 1. PAGE CONFIGURATION & CSS
# ============================================================
st.set_page_config(
    page_title="Run-Step Pro | Professional Running Guide",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp {
        background: #F8F9FA;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3 {
        color: #111827 !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
    }
    .weather-score-high { color: #10B981; font-weight: 800; font-size: 2rem; }
    .weather-score-med { color: #F59E0B; font-weight: 800; font-size: 2rem; }
    .weather-score-low { color: #EF4444; font-weight: 800; font-size: 2rem; }
    .spotify-container {
        border-radius: 12px;
        overflow: hidden;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. DATABASE CONFIGURATION (SQLite)
# ============================================================
DB_FILE = 'runstep_users.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            level TEXT,
            target_distance REAL,
            join_date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS run_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            course_name TEXT,
            distance REAL,
            run_date TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

def add_user(username, password, level="Beginner", target_distance=10.0):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, level, target_distance, join_date) VALUES (?, ?, ?, ?, ?)",
              (username, make_hashes(password), level, target_distance, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    conn.close()
    if data:
        return check_hashes(password, data[0])
    return False

def get_user_data(username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT level, target_distance, join_date FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    conn.close()
    return data

def add_run_history(username, course_name, distance):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO run_history (username, course_name, distance, run_date) VALUES (?, ?, ?, ?)",
              (username, course_name, distance, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_run_history(username):
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT course_name, distance, run_date FROM run_history WHERE username = ? ORDER BY run_date DESC", conn)
    conn.close()
    return df

init_db()

# ============================================================
# 3. EXTERNAL API INTEGRATIONS
# ============================================================

# OpenWeather API (Requires your API Key)
OPENWEATHER_API_KEY = "YOUR_OPENWEATHER_API_KEY" # Replace with actual key

def get_weather_data(lat, lon):
    # If API key is not set, return simulated dynamic data
    if OPENWEATHER_API_KEY == "YOUR_OPENWEATHER_API_KEY":
        base_temp = 20 + random.uniform(-5, 5)
        humidity = 50 + random.randint(-10, 20)
        pm10 = random.randint(15, 80)
        return calculate_running_score(base_temp, humidity, pm10)
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()
        temp = res['main']['temp']
        humidity = res['main']['humidity']
        # Note: Proper PM10 requires OpenWeather Air Pollution API endpoint, simulating here for structure
        pm10 = random.randint(20, 60) 
        return calculate_running_score(temp, humidity, pm10)
    except Exception as e:
        return {"score": 75, "temp": 22, "humidity": 45, "pm10": 30, "msg": "API Error"}

def calculate_running_score(temp, humidity, pm10):
    score = 100
    # Temperature penalty (Ideal: 10-18C)
    if temp > 25: score -= (temp - 25) * 2
    elif temp < 5: score -= (5 - temp) * 2
    
    # Humidity penalty
    if humidity > 70: score -= (humidity - 70) * 0.5
    
    # Air quality penalty
    if pm10 > 50: score -= (pm10 - 50) * 0.8
    
    score = max(0, min(100, int(score)))
    
    if score >= 80: msg = "Optimal running conditions!"
    elif score >= 60: msg = "Good conditions, stay hydrated."
    else: msg = "Tough conditions. Pace yourself."
        
    return {"score": score, "temp": round(temp, 1), "humidity": round(humidity, 1), "pm10": round(pm10, 1), "msg": msg}

# Spotify API (Requires Client ID and Secret to fetch playlists dynamically)
# For Streamlit UX, embedding an iframe is cleaner than redirecting to the app.
def get_spotify_embed(playlist_id):
    html = f"""
    <div class="spotify-container">
        <iframe src="https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator" 
        width="100%" height="352" frameBorder="0" allowfullscreen="" 
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>
    </div>
    """
    return html

# ============================================================
# 4. DATA MODEL & MOCK GEOJSON DATA
# ============================================================

def load_course_data():
    data = {
        "Course_ID": ["C001", "C002", "C003"],
        "Course_Name": ["Yeouido Hangang Track", "Namsan Summit Challenge", "Yangjaecheon Eco Trail"],
        "Level": ["Beginner", "Advanced", "Intermediate"],
        "Distance_KM": [5.0, 7.5, 10.0],
        "Map_Center": [[37.5289, 126.9331], [37.5509, 126.9909], [37.4934, 127.0601]],
        "Spotify_Playlist": ["37i9dQZF1DXaXB8fQg7sif", "37i9dQZF1DX76t638V6CU8", "37i9dQZF1DXcBWIGoYBM5M"] # Actual Spotify Playlist IDs (Dance, Workout, Pop)
    }
    return pd.DataFrame(data)

def get_elevation_profile(course_id):
    # Simulated high-resolution elevation data for Plotly
    if course_id == "C001": # Flat
        distances = [x * 0.1 for x in range(51)]
        elevations = [5 + random.uniform(-1, 1) for _ in distances]
    elif course_id == "C002": # Mountain
        distances = [x * 0.1 for x in range(76)]
        elevations = [100 + (x * 3) + random.uniform(-5, 5) if x < 40 else 220 - ((x-40) * 2.5) for x in range(76)]
    else: # Rolling hills
        distances = [x * 0.1 for x in range(101)]
        import math
        elevations = [20 + math.sin(x/5)*15 + random.uniform(-2, 2) for x in range(101)]
        
    return distances, elevations

def get_geojson_route(course_id, center):
    # Simulating a parsed GeoJSON coordinate array
    lat, lon = center
    coords = []
    steps = 50
    import math
    for i in range(steps):
        angle = (i / steps) * math.pi * 2
        radius = 0.01 if course_id == "C001" else 0.02
        coords.append([lat + math.sin(angle)*radius, lon + math.cos(angle)*radius])
    coords.append(coords[0]) # close loop
    return coords

# ============================================================
# 5. UI COMPONENTS (PLOTLY CHARTS)
# ============================================================

def plot_elevation_chart(distances, elevations):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=distances, 
        y=elevations,
        fill='tozeroy',
        mode='lines',
        line=dict(color='#10B981', width=3),
        fillcolor='rgba(16, 185, 129, 0.2)'
    ))
    fig.update_layout(
        title="Elevation Profile (m)",
        xaxis_title="Distance (km)",
        yaxis_title="Elevation (m)",
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#F3F4F6'),
        yaxis=dict(showgrid=True, gridcolor='#F3F4F6')
    )
    return fig

# ============================================================
# 6. APP ROUTING & MAIN LOGIC
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# SIDEBAR (Auth & Navigation)
with st.sidebar:
    st.title("Run-Step Pro")
    
    if not st.session_state.logged_in:
        menu = st.radio("Navigation", ["Login", "Sign Up"])
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if menu == "Sign Up":
            level = st.selectbox("Current Level", ["Beginner", "Intermediate", "Advanced"])
            if st.button("Create Account"):
                if username and password:
                    try:
                        add_user(username, password, level)
                        st.success("Account created! Please log in.")
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")
                else:
                    st.error("Please fill all fields.")
                    
        elif menu == "Login":
            if st.button("Login"):
                if login_user(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
    else:
        st.success(f"Welcome, {st.session_state.username}!")
        app_mode = st.radio("Go to", ["Dashboard", "Find Route"])
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

# MAIN AREA
if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; padding: 100px 20px;">
            <h1 style="font-size: 3.5rem;">Data-Driven Running.</h1>
            <p style="font-size: 1.2rem; color: #6B7280; max-width: 600px; margin: 0 auto;">
                Sign in to access personalized routes, environmental analytics, and save your running history.
            </p>
        </div>
    """, unsafe_allow_html=True)

else:
    user_data = get_user_data(st.session_state.username)
    user_level = user_data[0]
    
    if app_mode == "Dashboard":
        st.header("My Dashboard")
        
        history_df = get_run_history(st.session_state.username)
        total_dist = history_df['distance'].sum() if not history_df.empty else 0.0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">Total Distance</p>
                    <h2 style="margin: 5px 0;">{total_dist:.1f} km</h2>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">Total Runs</p>
                    <h2 style="margin: 5px 0;">{len(history_df)}</h2>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color: #6B7280; font-size: 0.9rem; margin: 0;">Runner Level</p>
                    <h2 style="margin: 5px 0;">{user_level}</h2>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Recent Runs")
        if history_df.empty:
            st.info("No runs recorded yet. Go to 'Find Route' to start exploring!")
        else:
            st.dataframe(history_df, use_container_width=True)

    elif app_mode == "Find Route":
        st.header("Explore Routes")
        
        df = load_course_data()
        
        # Determine suggested course based on level
        suggested = df[df['Level'] == user_level]
        if not suggested.empty:
            selected_course = st.selectbox("Select a Course", df['Course_Name'].tolist(), index=df[df['Course_Name']==suggested.iloc[0]['Course_Name']].index[0])
        else:
            selected_course = st.selectbox("Select a Course", df['Course_Name'].tolist())
            
        course_info = df[df['Course_Name'] == selected_course].iloc[0]
        
        # 1. Environmental Data Setup
        st.subheader("Current Environment")
        weather = get_weather_data(course_info['Map_Center'][0], course_info['Map_Center'][1])
        
        score_class = "weather-score-high" if weather['score'] >= 80 else "weather-score-med" if weather['score'] >= 60 else "weather-score-low"
        
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        w_col1.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <p style="margin:0; font-size:0.9rem; color:#6B7280;">Run Score</p>
                <div class="{score_class}">{weather['score']}</div>
            </div>
        """, unsafe_allow_html=True)
        w_col2.metric("Temperature", f"{weather['temp']} °C")
        w_col3.metric("Humidity", f"{weather['humidity']} %")
        w_col4.metric("PM10 (Air Quality)", f"{weather['pm10']} µg/m³")
        
        st.info(weather['msg'])
        
        st.markdown("<hr style='border-top: 1px solid #E5E7EB; margin: 30px 0;'>", unsafe_allow_html=True)
        
        # 2. Map & Elevation Setup
        col_map, col_chart = st.columns([1.2, 1])
        
        with col_map:
            st.subheader("Route Map")
            m = folium.Map(location=course_info['Map_Center'], zoom_start=14, tiles="CartoDB positron")
            coords = get_geojson_route(course_info['Course_ID'], course_info['Map_Center'])
            folium.PolyLine(coords, color="#3B82F6", weight=5, opacity=0.8).add_to(m)
            folium.Marker(course_info['Map_Center'], icon=folium.Icon(color="red", icon="info-sign")).add_to(m)
            st_folium(m, width=None, height=400)
            
        with col_chart:
            st.subheader("Terrain Analysis")
            dist_data, elev_data = get_elevation_profile(course_info['Course_ID'])
            st.plotly_chart(plot_elevation_chart(dist_data, elev_data), use_container_width=True)
            
            st.subheader("Pacing Playlist")
            st.markdown(get_spotify_embed(course_info['Spotify_Playlist']), unsafe_allow_html=True)
            
        # 3. Save Action
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Complete this Run & Save to Dashboard", type="primary"):
            add_run_history(st.session_state.username, course_info['Course_Name'], course_info['Distance_KM'])
            st.success("Run saved successfully! Check your dashboard.")

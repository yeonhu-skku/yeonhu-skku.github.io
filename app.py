"""
Running Course Analyzer — app.py
=================================
A Streamlit web application that analyzes running courses based on terrain,
mock weather conditions, and calculated difficulty levels.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import random

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be the first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Running Course Analyzer",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# MOCK DATA — COURSES
# ─────────────────────────────────────────────
@st.cache_data
def load_course_data() -> pd.DataFrame:
    """
    Returns a DataFrame of predefined running courses with metadata.
    Uses @st.cache_data so it is computed only once per session.
    """
    courses = [
        {
            "name": "Han River Riverside Path",
            "location": "Seoul, Yeouido",
            "distance_km": 7.2,
            "elevation_gain_m": 18,
            "surface": "Asphalt / Cycle Path",
            "difficulty": "Beginner",
            "avg_time_min": 43,
            "description": (
                "A flat, scenic loop along the Han River. "
                "Perfect for beginners or easy recovery runs. "
                "Well-lit and open year-round."
            ),
        },
        {
            "name": "Bukhansan Forest Trail",
            "location": "Seoul, Dobonggu",
            "distance_km": 12.5,
            "elevation_gain_m": 680,
            "surface": "Dirt Trail / Rock",
            "difficulty": "Advanced",
            "avg_time_min": 110,
            "description": (
                "A challenging mountain trail inside Bukhansan National Park. "
                "Technical rocky sections demand trail shoes and careful footing."
            ),
        },
        {
            "name": "Namsan Circular Loop",
            "location": "Seoul, Yongsan",
            "distance_km": 5.8,
            "elevation_gain_m": 195,
            "surface": "Paved Road / Dirt",
            "difficulty": "Intermediate",
            "avg_time_min": 52,
            "description": (
                "A popular loop circumnavigating Namsan (N Seoul Tower). "
                "Moderate climb with panoramic city views at the summit."
            ),
        },
        {
            "name": "Olympic Park Track",
            "location": "Seoul, Songpa",
            "distance_km": 3.0,
            "elevation_gain_m": 5,
            "surface": "Urethane Track",
            "difficulty": "Beginner",
            "avg_time_min": 18,
            "description": (
                "A smooth 400 m urethane track inside Olympic Park. "
                "Ideal for interval training and easy on the joints."
            ),
        },
        {
            "name": "Achasan Ridge Run",
            "location": "Seoul, Gwangjin",
            "distance_km": 8.9,
            "elevation_gain_m": 320,
            "surface": "Dirt Trail / Wooden Boardwalk",
            "difficulty": "Intermediate",
            "avg_time_min": 75,
            "description": (
                "A scenic ridge trail in eastern Seoul with city skyline views. "
                "Wooden boardwalks on steeper sections keep the descent manageable."
            ),
        },
        {
            "name": "Cheonggyecheon Streamside Path",
            "location": "Seoul, Jongno",
            "distance_km": 5.4,
            "elevation_gain_m": 8,
            "surface": "Concrete / Stone",
            "difficulty": "Beginner",
            "avg_time_min": 32,
            "description": (
                "A cool, shaded urban run along the restored Cheonggyecheon Stream. "
                "Flat and refreshing — ideal for hot summer days."
            ),
        },
        {
            "name": "Dobongsan Summit Push",
            "location": "Seoul, Dobong",
            "distance_km": 15.3,
            "elevation_gain_m": 890,
            "surface": "Rock / Dirt Trail",
            "difficulty": "Advanced",
            "avg_time_min": 145,
            "description": (
                "One of the toughest routes in Seoul, ascending to Dobongsan's "
                "granite peaks. Serious scrambling required near the top."
            ),
        },
    ]
    return pd.DataFrame(courses)


# ─────────────────────────────────────────────
# MOCK DATA — ELEVATION PROFILES
# ─────────────────────────────────────────────
@st.cache_data
def generate_elevation_profile(course_name: str, distance_km: float, elevation_gain_m: int) -> pd.DataFrame:
    """
    Generates a plausible synthetic elevation profile for a given course.

    Args:
        course_name:     Used as the random seed so the profile is reproducible.
        distance_km:     Total course distance (determines number of data points).
        elevation_gain_m: Peak elevation gain drives the amplitude of the curve.

    Returns:
        A DataFrame with columns ['distance_km', 'elevation_m'].
    """
    # Seed with a hash of the name so each course gets a unique but stable profile
    seed = abs(hash(course_name)) % (2**31)
    rng = np.random.default_rng(seed)

    n_points = max(30, int(distance_km * 10))  # ~10 points per km
    x = np.linspace(0, distance_km, n_points)

    # Build a smooth elevation curve: sine wave + noise, normalised to target gain
    raw = (
        np.sin(np.linspace(0, 3 * np.pi, n_points)) * 0.6
        + np.sin(np.linspace(0, 7 * np.pi, n_points)) * 0.25
        + rng.normal(0, 0.1, n_points)
    )
    raw -= raw.min()
    if raw.max() > 0:
        raw = raw / raw.max()

    base_elevation = 30  # metres above sea level (approximate Seoul floor)
    elevation = base_elevation + raw * elevation_gain_m

    return pd.DataFrame({"distance_km": x, "elevation_m": elevation})


# ─────────────────────────────────────────────
# MOCK DATA — WEATHER
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)  # Refresh weather every 5 minutes to simulate live data
def get_mock_weather(location: str) -> dict:
    """
    Returns mock current weather for a given location.
    In a production app, replace this with a real API call
    (e.g., OpenWeatherMap: https://openweathermap.org/api).

    Args:
        location: Location string used as seed for reproducible mock data.

    Returns:
        A dict with temperature, humidity, wind_speed, condition, and icon.
    """
    seed = abs(hash(location + str(pd.Timestamp.now().hour))) % (2**31)
    rng = np.random.default_rng(seed)

    conditions = [
        ("☀️ Clear", "Clear"),
        ("🌤️ Partly Cloudy", "Partly Cloudy"),
        ("☁️ Overcast", "Overcast"),
        ("🌧️ Light Rain", "Light Rain"),
        ("⛈️ Thunderstorm", "Thunderstorm"),
        ("🌫️ Foggy", "Foggy"),
    ]
    condition_label, condition_key = conditions[rng.integers(0, len(conditions))]

    return {
        "temperature_c": round(float(rng.uniform(12, 33)), 1),
        "humidity_pct": int(rng.integers(35, 92)),
        "wind_speed_kph": round(float(rng.uniform(2, 28)), 1),
        "condition_label": condition_label,
        "condition_key": condition_key,
    }


# ─────────────────────────────────────────────
# BUSINESS LOGIC — WEATHER SUITABILITY
# ─────────────────────────────────────────────
def evaluate_weather(weather: dict, difficulty: str) -> tuple[str, str, int]:
    """
    Produces a runability score (0–100) and human-readable recommendation
    based on weather conditions and course difficulty.

    Args:
        weather:    Dict returned by get_mock_weather().
        difficulty: 'Beginner', 'Intermediate', or 'Advanced'.

    Returns:
        (status_emoji, recommendation_text, runability_score)
    """
    score = 100
    notes = []

    temp = weather["temperature_c"]
    humidity = weather["humidity_pct"]
    wind = weather["wind_speed_kph"]
    condition = weather["condition_key"]

    # ── Temperature penalties ──
    if temp > 30:
        penalty = int((temp - 30) * 5)
        score -= penalty
        notes.append(f"High heat ({temp}°C) — hydrate frequently and consider early-morning start.")
    elif temp > 26:
        score -= 10
        notes.append(f"Warm conditions ({temp}°C) — carry extra water.")
    elif temp < 5:
        score -= 15
        notes.append(f"Cold temperature ({temp}°C) — layer up and warm up thoroughly.")

    # ── Humidity penalties ──
    if humidity > 80:
        score -= 15
        notes.append(f"High humidity ({humidity}%) increases perceived effort.")
    elif humidity > 70:
        score -= 5

    # ── Wind penalties ──
    if wind > 20:
        score -= 20
        notes.append(f"Strong wind ({wind} km/h) — exposed ridge trails not advised.")
    elif wind > 12:
        score -= 8
        notes.append(f"Moderate wind ({wind} km/h) — minor impact on pace.")

    # ── Condition penalties ──
    if condition == "Light Rain":
        score -= 15
        notes.append("Light rain — trails may be slippery; stick to paved surfaces.")
    elif condition == "Thunderstorm":
        score -= 60
        notes.append("⚠️ Thunderstorm active — outdoor running strongly discouraged.")
    elif condition == "Foggy":
        score -= 10
        notes.append("Fog reduces visibility on trails — run familiar, well-marked routes only.")

    # ── Extra difficulty penalty on bad weather ──
    if difficulty == "Advanced" and score < 70:
        score -= 10
        notes.append("Advanced terrain amplifies weather risks — consider rescheduling.")

    score = max(0, min(100, score))

    if score >= 80:
        status = "✅ Great conditions"
    elif score >= 55:
        status = "⚠️ Runnable with caution"
    else:
        status = "❌ Not recommended"

    recommendation = " ".join(notes) if notes else "Conditions look excellent — enjoy your run!"
    return status, recommendation, score


# ─────────────────────────────────────────────
# HELPER — COLOUR BY DIFFICULTY
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# EXTERNAL LINKS — per course
# ─────────────────────────────────────────────
COURSE_LINKS = {
    "Han River Riverside Path": {
        "google_maps": "https://maps.app.goo.gl/hanriver",
        "instagram":   "https://www.instagram.com/explore/tags/한강러닝/",
        "playlist":    "https://open.spotify.com/playlist/37i9dQZF1DX3Ogo9pFvBkY",
    },
    "Bukhansan Forest Trail": {
        "google_maps": "https://maps.app.goo.gl/bukhansan",
        "instagram":   "https://www.instagram.com/explore/tags/북한산트레일/",
        "playlist":    "https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn",
    },
    "Namsan Circular Loop": {
        "google_maps": "https://maps.app.goo.gl/namsan",
        "instagram":   "https://www.instagram.com/explore/tags/남산러닝/",
        "playlist":    "https://open.spotify.com/playlist/37i9dQZF1DX1s9knjP51Oa",
    },
    "Olympic Park Track": {
        "google_maps": "https://maps.app.goo.gl/olympicpark",
        "instagram":   "https://www.instagram.com/explore/tags/올림픽공원러닝/",
        "playlist":    "https://open.spotify.com/playlist/37i9dQZF1DWUvHZA1zLcjW",
    },
    "Achasan Ridge Run": {
        "google_maps": "https://maps.app.goo.gl/achasan",
        "instagram":   "https://www.instagram.com/explore/tags/아차산러닝/",
        "playlist":    "https://open.spotify.com/playlist/37i9dQZF1DX2RxBh64BHjQ",
    },
    "Cheonggyecheon Streamside Path": {
        "google_maps": "https://maps.app.goo.gl/cheonggyecheon",
        "instagram":   "https://www.instagram.com/explore/tags/청계천러닝/",
        "playlist":    "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0",
    },
    "Dobongsan Summit Push": {
        "google_maps": "https://maps.app.goo.gl/dobongsan",
        "instagram":   "https://www.instagram.com/explore/tags/도봉산트레일/",
        "playlist":    "https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn",
    },
}

DIFFICULTY_COLOURS = {
    "Beginner": "#22c55e",      # green
    "Intermediate": "#f59e0b",  # amber
    "Advanced": "#ef4444",      # red
}

SURFACE_ICONS = {
    "Asphalt": "🛣️",
    "Cycle Path": "🚴",
    "Dirt Trail": "🌿",
    "Rock": "🪨",
    "Paved Road": "🛤️",
    "Urethane Track": "🏟️",
    "Wooden Boardwalk": "🪵",
    "Concrete": "🏙️",
    "Stone": "🪨",
}


def surface_icon(surface_str: str) -> str:
    """Returns an emoji icon for the dominant surface type."""
    for key, icon in SURFACE_ICONS.items():
        if key.lower() in surface_str.lower():
            return icon
    return "👟"


# ─────────────────────────────────────────────
# CUSTOM CSS  (minimal, purposeful)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Card-style containers */
    .course-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
        color: #f1f5f9;
    }
    .course-card h4 { margin: 0 0 0.3rem 0; font-size: 1.05rem; }
    .course-card p  { margin: 0; font-size: 0.88rem; color: #94a3b8; line-height: 1.5; }

    /* Difficulty badge */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        margin-bottom: 0.5rem;
    }

    /* Runability bar */
    .run-bar-outer {
        background: #1e293b;
        border-radius: 8px;
        height: 14px;
        width: 100%;
        margin-top: 6px;
    }
    .run-bar-inner {
        height: 14px;
        border-radius: 8px;
        transition: width 0.4s ease;
    }

    /* Tweak sidebar padding */
    section[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
def main():
    # ── Load data ──────────────────────────────────────────────────────────────
    df_courses = load_course_data()

    # ─────────────────────────────────────────
    # SIDEBAR
    # ─────────────────────────────────────────
    with st.sidebar:
        st.image(
            "https://img.icons8.com/fluency/96/running.png",
            width=56,
        )
        st.title("Course Filters")
        st.divider()

        # Difficulty filter
        selected_difficulties = st.multiselect(
            "Difficulty Level",
            options=["Beginner", "Intermediate", "Advanced"],
            default=["Beginner", "Intermediate", "Advanced"],
            help="Filter courses by difficulty before selecting.",
        )

        # Apply filter to available courses
        filtered_df = df_courses[df_courses["difficulty"].isin(selected_difficulties)]

        if filtered_df.empty:
            st.warning("No courses match the selected difficulty levels.")
            st.stop()

        # Course selector
        selected_course_name = st.selectbox(
            "Select a Course",
            options=filtered_df["name"].tolist(),
        )

        st.divider()

    # ── Retrieve selected course row ───────────────────────────────────────────
    course = filtered_df[filtered_df["name"] == selected_course_name].iloc[0]

    # ─────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────
    col_title, col_badge = st.columns([5, 1])
    with col_title:
        st.title("🏃 Running Course Analyzer")
        st.markdown(
            "Explore Seoul's best routes — terrain breakdowns, live-style weather "
            "suitability checks, and elevation profiles at a glance."
        )
    with col_badge:
        diff_colour = DIFFICULTY_COLOURS[course["difficulty"]]
        st.markdown(
            f"""
            <div style='text-align:right; padding-top:1.2rem;'>
                <span class='badge' style='background:{diff_colour}22;
                      color:{diff_colour}; border:1px solid {diff_colour}55;'>
                    {course['difficulty'].upper()}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ─────────────────────────────────────────
    # COURSE DESCRIPTION CARD
    # ─────────────────────────────────────────
    surface_em = surface_icon(course["surface"])
    st.markdown(
        f"""
        <div class='course-card'>
            <h4>{surface_em} {course['name']}</h4>
            <p>📍 {course['location']} &nbsp;|&nbsp; 🛤️ {course['surface']}</p>
            <p style='margin-top:0.5rem;'>{course['description']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ─────────────────────────────────────────
    # KEY METRICS
    # ─────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📏 Distance", f"{course['distance_km']} km")
    m2.metric("⛰️ Elevation Gain", f"{course['elevation_gain_m']} m")
    m3.metric("⏱️ Est. Time", f"{course['avg_time_min']} min")

    # Pace derived from distance and estimated time
    pace_min_km = course["avg_time_min"] / course["distance_km"]
    pace_str = f"{int(pace_min_km)}:{int((pace_min_km % 1) * 60):02d} /km"
    m4.metric("🏃 Avg Pace", pace_str)

    st.divider()

    # ─────────────────────────────────────────
    # TWO-COLUMN LAYOUT: Elevation + Weather
    # ─────────────────────────────────────────
    col_chart, col_weather = st.columns([3, 2], gap="large")

    # ── Elevation Profile ──────────────────────────────────────────────────────
    with col_chart:
        st.subheader("📈 Elevation Profile")

        elev_df = generate_elevation_profile(
            course["name"], course["distance_km"], course["elevation_gain_m"]
        )

        # Build a filled area chart with Plotly for better aesthetics than st.line_chart
        fig = go.Figure()

        # Shaded area under the curve
        fig.add_trace(
            go.Scatter(
                x=elev_df["distance_km"],
                y=elev_df["elevation_m"],
                mode="lines",
                fill="tozeroy",
                line=dict(color="#38bdf8", width=2.5),
                fillcolor="rgba(56,189,248,0.15)",
                name="Elevation",
                hovertemplate="<b>Distance:</b> %{x:.2f} km<br><b>Elevation:</b> %{y:.0f} m<extra></extra>",
            )
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=280,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title="Distance (km)",
                showgrid=True,
                gridcolor="#1e293b",
                color="#94a3b8",
            ),
            yaxis=dict(
                title="Elevation (m)",
                showgrid=True,
                gridcolor="#1e293b",
                color="#94a3b8",
            ),
            showlegend=False,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Mini terrain stats below the chart
        t1, t2, t3 = st.columns(3)
        t1.markdown(f"**Min Elev.** {elev_df['elevation_m'].min():.0f} m")
        t2.markdown(f"**Max Elev.** {elev_df['elevation_m'].max():.0f} m")
        t3.markdown(
            f"**Gain** {course['elevation_gain_m']} m "
            f"({course['elevation_gain_m'] / course['distance_km']:.0f} m/km)"
        )

    # ── Weather Panel ──────────────────────────────────────────────────────────
    with col_weather:
        st.subheader("🌤️ Current Weather")

        weather = get_mock_weather(course["location"])
        status, recommendation, run_score = evaluate_weather(weather, course["difficulty"])

        # Weather stats
        w1, w2 = st.columns(2)
        w1.metric("🌡️ Temperature", f"{weather['temperature_c']}°C")
        w2.metric("💧 Humidity", f"{weather['humidity_pct']}%")
        w3, w4 = st.columns(2)
        w3.metric("💨 Wind", f"{weather['wind_speed_kph']} km/h")
        w4.metric("Sky", weather["condition_label"])

        st.divider()

        # Runability score with colour-coded bar
        if run_score >= 80:
            bar_color = "#22c55e"
        elif run_score >= 55:
            bar_color = "#f59e0b"
        else:
            bar_color = "#ef4444"

        st.markdown(f"**Runability Score** — {status}")
        st.markdown(
            f"""
            <div class='run-bar-outer'>
                <div class='run-bar-inner'
                     style='width:{run_score}%; background:{bar_color};'></div>
            </div>
            <p style='font-size:0.78rem; color:#94a3b8; margin-top:4px;'>{run_score}/100</p>
            """,
            unsafe_allow_html=True,
        )

        # Recommendation note
        with st.expander("💬 Detailed Recommendation", expanded=run_score < 80):
            st.write(recommendation)

    st.divider()

    # ─────────────────────────────────────────
    # EXTERNAL LINKS
    # ─────────────────────────────────────────
    st.subheader("🔗 Explore This Course")
    links = COURSE_LINKS.get(course["name"], {})
    if links:
        lc1, lc2, lc3 = st.columns(3)
        lc1.markdown(
            f"""
            <a href="{links['google_maps']}" target="_blank"
               style="display:block; text-align:center; padding:0.7rem 0;
                      background:#1e293b; border-radius:10px; border:1px solid #334155;
                      color:#f1f5f9; text-decoration:none; font-size:0.92rem;">
               🗺️ <strong>Google Maps</strong><br>
               <span style="font-size:0.78rem; color:#94a3b8;">Open route in Maps</span>
            </a>
            """,
            unsafe_allow_html=True,
        )
        lc2.markdown(
            f"""
            <a href="{links['instagram']}" target="_blank"
               style="display:block; text-align:center; padding:0.7rem 0;
                      background:#1e293b; border-radius:10px; border:1px solid #334155;
                      color:#f1f5f9; text-decoration:none; font-size:0.92rem;">
               📸 <strong>Instagram</strong><br>
               <span style="font-size:0.78rem; color:#94a3b8;">See runner photos</span>
            </a>
            """,
            unsafe_allow_html=True,
        )
        lc3.markdown(
            f"""
            <a href="{links['playlist']}" target="_blank"
               style="display:block; text-align:center; padding:0.7rem 0;
                      background:#1e293b; border-radius:10px; border:1px solid #334155;
                      color:#f1f5f9; text-decoration:none; font-size:0.92rem;">
               🎵 <strong>Run Playlist</strong><br>
               <span style="font-size:0.78rem; color:#94a3b8;">Spotify running mix</span>
            </a>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ─────────────────────────────────────────
    # COURSE COMPARISON TABLE
    # ─────────────────────────────────────────
    with st.expander("📊 Compare All Courses", expanded=False):
        st.markdown("All courses in the current difficulty filter, sorted by distance.")

        display_df = filtered_df[
            ["name", "difficulty", "distance_km", "elevation_gain_m", "surface", "avg_time_min"]
        ].copy()
        display_df.columns = ["Course", "Difficulty", "Distance (km)", "Elevation Gain (m)", "Surface", "Time (min)"]
        display_df = display_df.sort_values("Distance (km)").reset_index(drop=True)

        # Colour the difficulty column via a pandas Styler
        def colour_difficulty(val):
            colour = DIFFICULTY_COLOURS.get(val, "#888")
            return f"color: {colour}; font-weight: 700;"

        styled = display_df.style.map(colour_difficulty, subset=["Difficulty"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # ─────────────────────────────────────────
    # ELEVATION COMPARISON (all filtered courses)
    # ─────────────────────────────────────────
    with st.expander("⛰️ Elevation Gain Comparison", expanded=False):
        st.markdown("Stacked bar comparing distance vs. elevation gain across filtered courses.")

        bar_df = filtered_df[["name", "distance_km", "elevation_gain_m"]].copy()
        bar_df["name_short"] = bar_df["name"].apply(lambda x: x.split(" ")[0:3])
        bar_df["name_short"] = bar_df["name_short"].apply(lambda x: " ".join(x))

        fig2 = go.Figure()
        fig2.add_trace(
            go.Bar(
                x=bar_df["name_short"],
                y=bar_df["distance_km"],
                name="Distance (km)",
                marker_color="#38bdf8",
            )
        )
        fig2.add_trace(
            go.Bar(
                x=bar_df["name_short"],
                y=bar_df["elevation_gain_m"] / 100,  # Scale to km for visual comparison
                name="Elevation Gain (×100 m)",
                marker_color="#f59e0b",
            )
        )
        fig2.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(color="#94a3b8"),
            yaxis=dict(color="#94a3b8", gridcolor="#1e293b"),
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ─────────────────────────────────────────
    # FOOTER
    # ─────────────────────────────────────────
    st.markdown(
        "<p style='text-align:center; color:#475569; font-size:0.8rem; margin-top:2rem;'>"
        "Running Course Analyzer · Built with Streamlit · Data is illustrative only"
        "</p>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()

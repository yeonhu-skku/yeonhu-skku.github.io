import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="STRIDEMAP · Running Data Analysis",
    page_icon="🏃",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0a0a0f; }
    h1 { color: #ff4d5a; }
    .metric-container { background: #1e1e28; border-radius: 10px; padding: 16px; }
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    data = {
        "title":        ["Han River Morning", "Bukhansan Trail", "Gangnam Loop",
                         "Olympic Park Sunrise", "Cheonggyecheon Stream", "Mapo Valentine Run",
                         "Yeouido Cherry Prep", "Namsan Night Climb", "Han River Spring",
                         "Songpa Riverside", "Bukhan Spring Trail", "Night City Sprint"],
        "date":         ["2024-01-15","2024-01-18","2024-01-22","2024-02-02","2024-02-08",
                         "2024-02-14","2024-02-20","2024-03-05","2024-03-15","2024-03-22",
                         "2024-04-05","2024-04-18"],
        "distance_km":  [8.4, 12.1, 6.2, 9.8, 7.6, 10.5, 5.0, 11.2, 15.3, 13.7, 14.8, 4.5],
        "duration_min": [52, 89, 38, 61, 46, 65, 31, 78, 95, 84, 108, 26],
        "avg_pace_sec": [371, 441, 368, 373, 362, 371, 372, 418, 372, 368, 437, 347],
        "avg_hr":       [148, 162, 142, 151, 145, 155, 138, 168, 152, 149, 165, 168],
        "max_hr":       [172, 185, 162, 175, 168, 178, 158, 188, 172, 170, 190, 188],
        "calories":     [610, 980, 445, 720, 548, 775, 358, 892, 1102, 985, 1220, 342],
        "elevation_m":  [12, 420, 8, 45, 5, 62, 4, 265, 18, 22, 510, 10],
        "weather":      ["Clear","Cloudy","Sunny","Clear","Foggy","Clear","Windy","Clear",
                         "Sunny","Partly Cloudy","Clear","Clear"],
        "temp_c":       [3, 1, 6, -2, 4, 8, 10, 12, 18, 15, 14, 17],
        "mood":         [5, 4, 5, 5, 3, 5, 4, 5, 5, 4, 5, 5],
    }
    df = pd.DataFrame(data)
    df["date"]      = pd.to_datetime(df["date"])
    df["month"]     = df["date"].dt.strftime("%Y-%m")
    df["pace_min"]  = df["avg_pace_sec"] / 60
    df["pace_str"]  = df["avg_pace_sec"].apply(
        lambda s: f"{int(s//60)}:{int(s%60):02d}"
    )
    return df

df = load_data()

# ── Header ───────────────────────────────────────────────
st.title("🏃 STRIDEMAP")
st.markdown("**Art & Big Data** · Seoul Running Course Analysis 2024")
st.divider()

# ── Summary metrics ──────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Runs",      f"{len(df)}")
col2.metric("Total Distance",  f"{df['distance_km'].sum():.1f} km")
col3.metric("Total Calories",  f"{df['calories'].sum():,} kcal")
col4.metric("Total Elevation", f"{df['elevation_m'].sum()} m")
col5.metric("Avg Pace",        f"{int(df['avg_pace_sec'].mean()//60)}:{int(df['avg_pace_sec'].mean()%60):02d} /km")

st.divider()

# ── Sidebar filters ──────────────────────────────────────
st.sidebar.header("🔍 Filters")
selected_weather = st.sidebar.multiselect(
    "Weather Condition",
    options=df["weather"].unique(),
    default=df["weather"].unique()
)
min_dist, max_dist = st.sidebar.slider(
    "Distance Range (km)",
    float(df["distance_km"].min()),
    float(df["distance_km"].max()),
    (float(df["distance_km"].min()), float(df["distance_km"].max()))
)
mood_filter = st.sidebar.multiselect(
    "Mood Score",
    options=sorted(df["mood"].unique()),
    default=sorted(df["mood"].unique()),
    format_func=lambda x: "⭐" * x
)

filtered = df[
    df["weather"].isin(selected_weather) &
    df["distance_km"].between(min_dist, max_dist) &
    df["mood"].isin(mood_filter)
]

st.sidebar.markdown(f"Showing **{len(filtered)}** runs")

# ── Tabs ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Performance", "❤️ Heart Rate", "🌤 Weather & Condition", "📋 Data Table"])

# ════════════════════════════════════════════════
# TAB 1 — Performance
# ════════════════════════════════════════════════
with tab1:
    col_a, col_b = st.columns(2)

    # Distance + Pace timeline
    with col_a:
        st.subheader("Distance & Pace Timeline")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(
            x=filtered["title"], y=filtered["distance_km"],
            name="Distance (km)", marker_color="rgba(0,229,255,0.6)",
            marker_line_color="#00e5ff", marker_line_width=1
        ), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=filtered["title"], y=filtered["pace_min"],
            name="Pace (min/km)", mode="lines+markers",
            line=dict(color="#ff4d5a", width=2),
            marker=dict(size=7, color="#ff4d5a")
        ), secondary_y=True)
        fig.update_layout(
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", legend=dict(bgcolor="#1e1e28"),
            margin=dict(t=10, b=80)
        )
        fig.update_xaxes(tickangle=30, tickfont_size=10)
        fig.update_yaxes(title_text="Distance (km)", secondary_y=False, gridcolor="#2a2a38")
        fig.update_yaxes(title_text="Pace (min/km)", secondary_y=True,  gridcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # Monthly distance
    with col_b:
        st.subheader("Monthly Distance Volume")
        monthly = filtered.groupby("month")["distance_km"].sum().reset_index()
        fig2 = px.bar(
            monthly, x="month", y="distance_km",
            labels={"month": "Month", "distance_km": "Distance (km)"},
            color="month",
            color_discrete_sequence=["#00e5ff", "#9b5de5", "#ff4d5a", "#ffd166"]
        )
        fig2.update_layout(
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", showlegend=False, margin=dict(t=10)
        )
        fig2.update_yaxes(gridcolor="#2a2a38")
        st.plotly_chart(fig2, use_container_width=True)

    # Distance vs Calories scatter
    st.subheader("Distance vs Calories (colored by Elevation Gain)")
    fig3 = px.scatter(
        filtered, x="distance_km", y="calories",
        size="elevation_m", color="elevation_m",
        hover_name="title",
        hover_data={"distance_km": True, "calories": True, "elevation_m": True, "pace_str": True},
        labels={"distance_km": "Distance (km)", "calories": "Calories (kcal)",
                "elevation_m": "Elevation (m)", "pace_str": "Pace"},
        color_continuous_scale=["#06d6a0", "#9b5de5", "#ffd166"],
        size_max=40
    )
    fig3.update_layout(
        paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
        font_color="#8888a0", margin=dict(t=10)
    )
    fig3.update_xaxes(gridcolor="#2a2a38")
    fig3.update_yaxes(gridcolor="#2a2a38")
    st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════
# TAB 2 — Heart Rate
# ════════════════════════════════════════════════
with tab2:
    col_a, col_b = st.columns(2)

    # HR zone donut
    with col_a:
        st.subheader("Heart Rate Zone Distribution")
        all_hr = filtered["avg_hr"].values
        zones = {
            "Z1 Recovery (<120)":      int(np.sum(all_hr < 120)),
            "Z2 Fat Burn (120–140)":   int(np.sum((all_hr >= 120) & (all_hr < 140))),
            "Z3 Aerobic (140–160)":    int(np.sum((all_hr >= 140) & (all_hr < 160))),
            "Z4 Threshold (160–175)":  int(np.sum((all_hr >= 160) & (all_hr < 175))),
            "Z5 Maximum (175+)":       int(np.sum(all_hr >= 175)),
        }
        fig4 = px.pie(
            values=list(zones.values()), names=list(zones.keys()),
            hole=0.55,
            color_discrete_sequence=["#4a4a60","#00e5ff","#9b5de5","#ff4d5a","#ffd166"]
        )
        fig4.update_layout(
            paper_bgcolor="#1e1e28", font_color="#8888a0",
            legend=dict(bgcolor="#1e1e28"), margin=dict(t=10)
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Avg vs Max HR
    with col_b:
        st.subheader("Average vs Max Heart Rate")
        fig5 = go.Figure()
        fig5.add_trace(go.Bar(
            x=filtered["title"], y=filtered["avg_hr"],
            name="Avg HR", marker_color="rgba(0,229,255,0.6)"
        ))
        fig5.add_trace(go.Bar(
            x=filtered["title"], y=filtered["max_hr"],
            name="Max HR", marker_color="rgba(255,77,90,0.6)"
        ))
        fig5.update_layout(
            barmode="group",
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", legend=dict(bgcolor="#1e1e28"),
            margin=dict(t=10, b=80)
        )
        fig5.update_xaxes(tickangle=30, tickfont_size=10)
        fig5.update_yaxes(gridcolor="#2a2a38", title="bpm")
        st.plotly_chart(fig5, use_container_width=True)

    # HR vs Pace scatter with trendline
    st.subheader("Heart Rate vs Pace (with Trendline)")
    fig6 = px.scatter(
        filtered, x="avg_hr", y="pace_min",
        color="distance_km", size="distance_km",
        hover_name="title",
        labels={"avg_hr": "Avg Heart Rate (bpm)", "pace_min": "Pace (min/km)",
                "distance_km": "Distance (km)"},
        color_continuous_scale=["#06d6a0", "#00e5ff", "#9b5de5", "#ff4d5a"],
        trendline="ols"
    )
    fig6.update_layout(
        paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
        font_color="#8888a0", margin=dict(t=10)
    )
    fig6.update_xaxes(gridcolor="#2a2a38")
    fig6.update_yaxes(gridcolor="#2a2a38")
    st.plotly_chart(fig6, use_container_width=True)

# ════════════════════════════════════════════════
# TAB 3 — Weather & Condition
# ════════════════════════════════════════════════
with tab3:
    col_a, col_b = st.columns(2)

    # Avg pace by weather
    with col_a:
        st.subheader("Average Pace by Weather")
        weather_perf = filtered.groupby("weather").agg(
            avg_pace=("pace_min", "mean"),
            count=("title", "count")
        ).reset_index()
        fig7 = px.bar(
            weather_perf, x="weather", y="avg_pace",
            color="avg_pace", text="count",
            labels={"weather": "Weather", "avg_pace": "Avg Pace (min/km)", "count": "Runs"},
            color_continuous_scale=["#06d6a0", "#ffd166", "#ff4d5a"]
        )
        fig7.update_traces(texttemplate="%{text} runs", textposition="outside")
        fig7.update_layout(
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", showlegend=False, margin=dict(t=10)
        )
        fig7.update_yaxes(gridcolor="#2a2a38")
        st.plotly_chart(fig7, use_container_width=True)

    # Temperature vs Pace
    with col_b:
        st.subheader("Temperature vs Pace")
        fig8 = px.scatter(
            filtered, x="temp_c", y="pace_min",
            color="mood", size="distance_km",
            hover_name="title",
            labels={"temp_c": "Temperature (°C)", "pace_min": "Pace (min/km)", "mood": "Mood"},
            color_continuous_scale=["#4a4a60", "#00e5ff", "#ffd166"],
            trendline="ols"
        )
        fig8.update_layout(
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", margin=dict(t=10)
        )
        fig8.update_xaxes(gridcolor="#2a2a38")
        fig8.update_yaxes(gridcolor="#2a2a38")
        st.plotly_chart(fig8, use_container_width=True)

    # Mood vs Performance radar
    st.subheader("Mood Score vs Performance (Radar)")
    mood_perf = filtered.groupby("mood").agg(
        avg_distance=("distance_km", "mean"),
        avg_pace=("pace_min", "mean"),
        avg_hr=("avg_hr", "mean"),
        avg_elevation=("elevation_m", "mean"),
        avg_calories=("calories", "mean"),
    ).reset_index()

    categories   = ["Distance", "Speed", "Heart Rate", "Elevation", "Calories"]
    colors_mood  = {3: "#4a4a60", 4: "#00e5ff", 5: "#ff4d5a"}

    fig9 = go.Figure()
    for _, row in mood_perf.iterrows():
        mood = int(row["mood"])
        vals = [
            row["avg_distance"]  / df["distance_km"].max(),
            1 - (row["avg_pace"] / df["pace_min"].max()),
            row["avg_hr"]        / df["avg_hr"].max(),
            row["avg_elevation"] / df["elevation_m"].max(),
            row["avg_calories"]  / df["calories"].max(),
        ]
        vals_pct = [v * 100 for v in vals]
        color = colors_mood.get(mood, "#888")
        fig9.add_trace(go.Scatterpolar(
            r=vals_pct + [vals_pct[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=f"Mood {'⭐'*mood}",
            line_color=color,
            fillcolor=color + "22"
        ))
    fig9.update_layout(
        polar=dict(
            bgcolor="#1e1e28",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#2a2a38", tickcolor="#4a4a60"),
            angularaxis=dict(gridcolor="#2a2a38")
        ),
        paper_bgcolor="#1e1e28", font_color="#8888a0",
        legend=dict(bgcolor="#1e1e28"), margin=dict(t=20)
    )
    st.plotly_chart(fig9, use_container_width=True)

# ════════════════════════════════════════════════
# TAB 4 — Data Table
# ════════════════════════════════════════════════
with tab4:
    st.subheader("Full Running Log")

    display_df = filtered[[
        "date", "title", "distance_km", "duration_min",
        "pace_str", "avg_hr", "max_hr", "calories", "elevation_m", "weather", "temp_c", "mood"
    ]].copy()
    display_df.columns = [
        "Date", "Run", "Distance (km)", "Duration (min)",
        "Pace", "Avg HR", "Max HR", "Calories", "Elevation (m)", "Weather", "Temp (°C)", "Mood"
    ]
    display_df["Mood"] = display_df["Mood"].apply(lambda x: "⭐" * x)
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")

    st.dataframe(display_df, use_container_width=True, height=420)

    # Descriptive statistics
    st.subheader("Descriptive Statistics")
    stats_df = filtered[["distance_km","duration_min","pace_min","avg_hr","calories","elevation_m"]].describe().round(2)
    stats_df.index  = ["Count","Mean","Std Dev","Min","25%","Median","75%","Max"]
    stats_df.columns = ["Distance (km)","Duration (min)","Pace (min/km)","Avg HR","Calories","Elevation (m)"]
    st.dataframe(stats_df, use_container_width=True)

# ── Footer ───────────────────────────────────────────────
st.divider()
st.caption("STRIDEMAP · Art & Big Data · Seoul Running Course Analysis 2024")

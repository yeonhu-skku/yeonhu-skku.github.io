import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="STRIDEMAP · Running Course Analysis",
    page_icon="🏃",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0a0a0f; }
    h1 { color: #ff4d5a; }
</style>
""", unsafe_allow_html=True)

# ── Data ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    data = {
        "title":         ["Han River Morning", "Bukhansan Trail", "Gangnam Loop",
                          "Olympic Park Sunrise", "Cheonggyecheon Stream", "Mapo Valentine Run",
                          "Yeouido Cherry Prep", "Namsan Night Climb", "Han River Spring",
                          "Songpa Riverside", "Bukhan Spring Trail", "Night City Sprint"],
        "date":          ["2024-01-15","2024-01-18","2024-01-22","2024-02-02","2024-02-08",
                          "2024-02-14","2024-02-20","2024-03-05","2024-03-15","2024-03-22",
                          "2024-04-05","2024-04-18"],
        "terrain_type":  ["Riverside","Mountain","Urban","Park","Urban",
                          "Urban","Riverside","Mountain","Riverside","Riverside","Mountain","Urban"],
        "distance_km":   [8.4, 12.1, 6.2, 9.8, 7.6, 10.5, 5.0, 11.2, 15.3, 13.7, 14.8, 4.5],
        "duration_min":  [52, 89, 38, 61, 46, 65, 31, 78, 95, 84, 108, 26],
        "avg_pace_sec":  [371, 441, 368, 373, 362, 371, 372, 418, 372, 368, 437, 347],
        "avg_hr":        [148, 162, 142, 151, 145, 155, 138, 168, 152, 149, 165, 168],
        "max_hr":        [172, 185, 162, 175, 168, 178, 158, 188, 172, 170, 190, 188],
        "calories":      [610, 980, 445, 720, 548, 775, 358, 892, 1102, 985, 1220, 342],
        "elevation_m":   [12, 420, 8, 45, 5, 62, 4, 265, 18, 22, 510, 10],
        "max_slope_pct": [3, 28, 2, 8, 1, 12, 1, 22, 4, 5, 32, 3],
        "surface":       ["Asphalt","Trail","Asphalt","Mixed","Asphalt",
                          "Asphalt","Asphalt","Trail","Asphalt","Asphalt","Trail","Asphalt"],
        "weather":       ["Clear","Cloudy","Sunny","Clear","Foggy","Clear",
                          "Windy","Clear","Sunny","Partly Cloudy","Clear","Clear"],
        "wind_speed_ms": [2, 5, 3, 1, 2, 3, 8, 1, 4, 3, 2, 1],
        "temp_c":        [3, 1, 6, -2, 4, 8, 10, 12, 18, 15, 14, 17],
        "mood":          [5, 4, 5, 5, 3, 5, 4, 5, 5, 4, 5, 5],
        # Elevation series (normalized to 20 points each)
        "elev_series":   [
            [8,9,10,11,12,12,11,10,9,9,10,11,12,11,10,9,8,8,9,8],
            [80,120,165,210,255,295,335,370,398,415,420,418,410,395,375,350,318,280,235,185],
            [25,26,27,28,28,27,26,25,25,26,27,28,27,26,25,25,25,26,25,25],
            [15,18,22,28,35,42,45,44,40,35,30,25,22,20,18,17,16,15,16,15],
            [12,12,11,11,10,10,10,11,11,12,12,11,11,10,10,10,10,11,10,10],
            [20,25,32,40,48,55,60,62,62,60,58,55,50,45,40,35,30,25,22,20],
            [5,5,6,6,6,5,5,4,4,4,5,5,6,5,4,4,5,5,4,4],
            [60,88,118,148,178,205,228,248,262,265,262,255,242,228,210,188,165,138,110,82],
            [8,9,10,11,12,13,14,15,16,18,17,16,15,14,13,12,11,10,9,8],
            [12,14,16,18,20,22,22,21,20,18,16,15,14,13,12,12,13,14,13,12],
            [85,135,188,242,295,345,390,428,460,485,505,510,505,492,475,455,432,405,372,338],
            [18,20,22,24,25,25,24,22,20,18,19,20,22,23,24,23,21,20,19,18],
        ],
    }
    df = pd.DataFrame(data)
    df["date"]     = pd.to_datetime(df["date"])
    df["month"]    = df["date"].dt.strftime("%Y-%m")
    df["pace_min"] = df["avg_pace_sec"] / 60
    df["pace_str"] = df["avg_pace_sec"].apply(lambda s: f"{int(s//60)}:{int(s%60):02d}")

    # Difficulty score: weighted combo of elevation, slope, distance
    elev_n  = df["elevation_m"]   / df["elevation_m"].max()
    slope_n = df["max_slope_pct"] / df["max_slope_pct"].max()
    dist_n  = df["distance_km"]   / df["distance_km"].max()
    df["difficulty_score"] = (elev_n * 0.45 + slope_n * 0.35 + dist_n * 0.20) * 100
    df["difficulty"] = pd.cut(
        df["difficulty_score"],
        bins=[0, 20, 50, 101],
        labels=["Easy", "Moderate", "Hard"]
    )

    # Weather impact score: wind + fog penalty on pace vs avg
    avg_pace = df["avg_pace_sec"].mean()
    df["weather_impact"] = ((df["avg_pace_sec"] - avg_pace) / avg_pace * 100).round(1)

    return df

df = load_data()

# ── Header ───────────────────────────────────────────────
st.title("🏃 STRIDEMAP")
st.markdown("**Art & Big Data** · Seoul Running Course Terrain Analysis 2024")
st.divider()

# ── Summary metrics ──────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Runs",       f"{len(df)}")
c2.metric("Total Distance",   f"{df['distance_km'].sum():.1f} km")
c3.metric("Total Elevation",  f"{df['elevation_m'].sum()} m")
c4.metric("Hardest Course",   df[df["difficulty_score"]==df["difficulty_score"].max()]["title"].values[0])
c5.metric("Easiest Course",   df[df["difficulty_score"]==df["difficulty_score"].min()]["title"].values[0])
st.divider()

# ── Sidebar filters ──────────────────────────────────────
st.sidebar.header("🔍 Filters")
terrain_filter = st.sidebar.multiselect(
    "Terrain Type",
    options=df["terrain_type"].unique(),
    default=df["terrain_type"].unique()
)
difficulty_filter = st.sidebar.multiselect(
    "Difficulty",
    options=["Easy", "Moderate", "Hard"],
    default=["Easy", "Moderate", "Hard"]
)
surface_filter = st.sidebar.multiselect(
    "Surface",
    options=df["surface"].unique(),
    default=df["surface"].unique()
)

filtered = df[
    df["terrain_type"].isin(terrain_filter) &
    df["difficulty"].isin(difficulty_filter) &
    df["surface"].isin(surface_filter)
]
st.sidebar.markdown(f"Showing **{len(filtered)}** runs")

# ── Tabs ─────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🏔 Elevation Profile",
    "📊 Difficulty Analysis",
    "🌤 Weather Impact",
    "📋 Data Table"
])

# ════════════════════════════════════════════════
# TAB 1 — Elevation Profile
# ════════════════════════════════════════════════
with tab1:
    st.subheader("Elevation Profile by Course")

    # Course selector
    selected_courses = st.multiselect(
        "Select courses to compare",
        options=filtered["title"].tolist(),
        default=filtered["title"].tolist()[:4]
    )

    if selected_courses:
        fig_elev = go.Figure()
        colors = ["#00e5ff","#ff4d5a","#ffd166","#9b5de5","#06d6a0",
                  "#ff9f1c","#e71d36","#2ec4b6","#cbf3f0","#ffbf69","#ffffff","#a8dadc"]

        for i, title in enumerate(selected_courses):
            row    = filtered[filtered["title"] == title].iloc[0]
            series = row["elev_series"]
            x_pct  = [round(j / (len(series)-1) * 100, 1) for j in range(len(series))]

            fig_elev.add_trace(go.Scatter(
                x=x_pct, y=series,
                mode="lines",
                name=f"{title} ({row['elevation_m']}m gain)",
                line=dict(color=colors[i % len(colors)], width=2.5),
                fill="tozeroy",
                fillcolor=colors[i % len(colors)].replace("#","rgba(").rstrip(")") + ",0.06)"
                    if colors[i % len(colors)].startswith("#") else colors[i % len(colors)],
                hovertemplate=f"<b>{title}</b><br>Progress: %{{x}}%<br>Elevation: %{{y}}m<extra></extra>"
            ))

        fig_elev.update_layout(
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", legend=dict(bgcolor="#1e1e28"),
            xaxis_title="Course Progress (%)",
            yaxis_title="Elevation (m)",
            hovermode="x unified",
            margin=dict(t=10)
        )
        fig_elev.update_xaxes(gridcolor="#2a2a38")
        fig_elev.update_yaxes(gridcolor="#2a2a38")
        st.plotly_chart(fig_elev, use_container_width=True)
    else:
        st.info("Select at least one course above.")

    # Elevation gain comparison bar
    st.subheader("Elevation Gain per Course")
    elev_sorted = filtered.sort_values("elevation_m", ascending=True)
    fig_bar = px.bar(
        elev_sorted, x="elevation_m", y="title",
        orientation="h",
        color="elevation_m",
        color_continuous_scale=["#06d6a0","#9b5de5","#ffd166","#ff4d5a"],
        labels={"elevation_m": "Elevation Gain (m)", "title": ""},
        text="elevation_m"
    )
    fig_bar.update_traces(texttemplate="%{text}m", textposition="outside")
    fig_bar.update_layout(
        paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
        font_color="#8888a0", showlegend=False,
        coloraxis_showscale=False, margin=dict(t=10)
    )
    fig_bar.update_xaxes(gridcolor="#2a2a38")
    st.plotly_chart(fig_bar, use_container_width=True)

# ════════════════════════════════════════════════
# TAB 2 — Difficulty Analysis
# ════════════════════════════════════════════════
with tab2:
    col_a, col_b = st.columns(2)

    # Difficulty classification
    with col_a:
        st.subheader("Course Difficulty Classification")
        diff_counts = filtered["difficulty"].value_counts().reset_index()
        diff_counts.columns = ["Difficulty", "Count"]
        fig_diff = px.pie(
            diff_counts, values="Count", names="Difficulty",
            hole=0.55,
            color="Difficulty",
            color_discrete_map={"Easy":"#06d6a0","Moderate":"#ffd166","Hard":"#ff4d5a"}
        )
        fig_diff.update_layout(
            paper_bgcolor="#1e1e28", font_color="#8888a0",
            legend=dict(bgcolor="#1e1e28"), margin=dict(t=10)
        )
        st.plotly_chart(fig_diff, use_container_width=True)

    # Terrain type vs avg difficulty
    with col_b:
        st.subheader("Avg Difficulty Score by Terrain")
        terrain_diff = filtered.groupby("terrain_type").agg(
            avg_difficulty=("difficulty_score","mean"),
            avg_elevation=("elevation_m","mean"),
            count=("title","count")
        ).reset_index()
        fig_td = px.bar(
            terrain_diff, x="terrain_type", y="avg_difficulty",
            color="terrain_type",
            text="count",
            labels={"terrain_type":"Terrain","avg_difficulty":"Avg Difficulty Score (0–100)"},
            color_discrete_map={"Mountain":"#ff4d5a","Riverside":"#00e5ff",
                                "Urban":"#9b5de5","Park":"#06d6a0"}
        )
        fig_td.update_traces(texttemplate="%{text} runs", textposition="outside")
        fig_td.update_layout(
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", showlegend=False, margin=dict(t=10)
        )
        fig_td.update_yaxes(gridcolor="#2a2a38")
        st.plotly_chart(fig_td, use_container_width=True)

    # Difficulty score vs Pace scatter — manual trendline (no scipy needed)
    st.subheader("Difficulty Score vs Pace")
    x_vals = filtered["difficulty_score"].values
    y_vals = filtered["pace_min"].values

    # Manual linear regression
    if len(x_vals) > 1:
        m, b   = np.polyfit(x_vals, y_vals, 1)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
        y_line = m * x_line + b
    else:
        x_line, y_line = [], []

    diff_colors = {"Easy":"#06d6a0","Moderate":"#ffd166","Hard":"#ff4d5a"}
    fig_dp = go.Figure()

    for diff_label, color in diff_colors.items():
        sub = filtered[filtered["difficulty"] == diff_label]
        fig_dp.add_trace(go.Scatter(
            x=sub["difficulty_score"], y=sub["pace_min"],
            mode="markers",
            name=diff_label,
            marker=dict(color=color, size=12, line=dict(color="#1e1e28", width=1)),
            text=sub["title"],
            hovertemplate="<b>%{text}</b><br>Difficulty: %{x:.1f}<br>Pace: %{y:.2f} min/km<extra></extra>"
        ))

    if len(x_line):
        fig_dp.add_trace(go.Scatter(
            x=x_line, y=y_line,
            mode="lines", name="Trend",
            line=dict(color="rgba(255,255,255,0.25)", width=1.5, dash="dot")
        ))

    fig_dp.update_layout(
        paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
        font_color="#8888a0", legend=dict(bgcolor="#1e1e28"),
        xaxis_title="Difficulty Score (0–100)",
        yaxis_title="Avg Pace (min/km)",
        margin=dict(t=10)
    )
    fig_dp.update_xaxes(gridcolor="#2a2a38")
    fig_dp.update_yaxes(gridcolor="#2a2a38")
    st.plotly_chart(fig_dp, use_container_width=True)

    # Course difficulty scorecard
    st.subheader("Course Difficulty Scorecard")
    scorecard = filtered[["title","terrain_type","surface","distance_km",
                           "elevation_m","max_slope_pct","difficulty_score","difficulty"]].copy()
    scorecard.columns = ["Course","Terrain","Surface","Distance (km)",
                         "Elevation (m)","Max Slope (%)","Difficulty Score","Level"]
    scorecard["Difficulty Score"] = scorecard["Difficulty Score"].round(1)
    scorecard = scorecard.sort_values("Difficulty Score", ascending=False)
    st.dataframe(scorecard, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
# TAB 3 — Weather Impact
# ════════════════════════════════════════════════
with tab3:
    st.subheader("How Much Does Weather Affect Each Course?")
    st.caption("Weather Impact = % deviation from average pace. Positive = slower than average.")

    col_a, col_b = st.columns(2)

    # Weather impact per course
    with col_a:
        impact_sorted = filtered.sort_values("weather_impact", ascending=True)
        fig_wi = px.bar(
            impact_sorted, x="weather_impact", y="title",
            orientation="h",
            color="weather_impact",
            color_continuous_scale=["#06d6a0","#ffd166","#ff4d5a"],
            labels={"weather_impact": "Pace Deviation from Avg (%)", "title": ""},
            text="weather"
        )
        fig_wi.update_traces(textposition="outside")
        fig_wi.update_layout(
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", showlegend=False,
            coloraxis_showscale=False, margin=dict(t=10)
        )
        fig_wi.update_xaxes(gridcolor="#2a2a38", zeroline=True, zerolinecolor="#4a4a60")
        st.plotly_chart(fig_wi, use_container_width=True)

    # Wind speed vs pace deviation
    with col_b:
        st.subheader("Wind Speed vs Pace Impact")
        fig_wind = go.Figure()
        terrain_colors = {"Mountain":"#ff4d5a","Riverside":"#00e5ff",
                          "Urban":"#9b5de5","Park":"#06d6a0"}
        for terrain, color in terrain_colors.items():
            sub = filtered[filtered["terrain_type"] == terrain]
            if sub.empty:
                continue
            fig_wind.add_trace(go.Scatter(
                x=sub["wind_speed_ms"], y=sub["weather_impact"],
                mode="markers",
                name=terrain,
                marker=dict(color=color, size=11, line=dict(color="#1e1e28",width=1)),
                text=sub["title"],
                hovertemplate="<b>%{text}</b><br>Wind: %{x} m/s<br>Pace impact: %{y}%<extra></extra>"
            ))

        # Manual trendline
        wx = filtered["wind_speed_ms"].values
        wy = filtered["weather_impact"].values
        if len(wx) > 1:
            mw, bw   = np.polyfit(wx, wy, 1)
            xl = np.linspace(wx.min(), wx.max(), 100)
            fig_wind.add_trace(go.Scatter(
                x=xl, y=mw*xl+bw,
                mode="lines", name="Trend",
                line=dict(color="rgba(255,255,255,0.2)", width=1.5, dash="dot")
            ))

        fig_wind.update_layout(
            paper_bgcolor="#1e1e28", plot_bgcolor="#1e1e28",
            font_color="#8888a0", legend=dict(bgcolor="#1e1e28"),
            xaxis_title="Wind Speed (m/s)",
            yaxis_title="Pace Deviation (%)",
            margin=dict(t=10)
        )
        fig_wind.update_xaxes(gridcolor="#2a2a38")
        fig_wind.update_yaxes(gridcolor="#2a2a38", zeroline=True, zerolinecolor="#4a4a60")
        st.plotly_chart(fig_wind, use_container_width=True)

    # Weather condition summary table
    st.subheader("Weather Condition Summary")
    weather_summary = filtered.groupby("weather").agg(
        runs=("title","count"),
        avg_pace=("pace_min","mean"),
        avg_wind=("wind_speed_ms","mean"),
        avg_temp=("temp_c","mean"),
        avg_impact=("weather_impact","mean")
    ).reset_index()
    weather_summary.columns = ["Weather","Runs","Avg Pace (min/km)","Avg Wind (m/s)","Avg Temp (°C)","Avg Pace Impact (%)"]
    weather_summary = weather_summary.round(2)
    st.dataframe(weather_summary, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════
# TAB 4 — Data Table
# ════════════════════════════════════════════════
with tab4:
    st.subheader("Full Running Log")
    display_df = filtered[[
        "date","title","terrain_type","surface","distance_km","duration_min",
        "pace_str","avg_hr","calories","elevation_m","max_slope_pct","difficulty","weather","temp_c"
    ]].copy()
    display_df.columns = [
        "Date","Course","Terrain","Surface","Distance (km)","Duration (min)",
        "Pace","Avg HR","Calories","Elevation (m)","Max Slope (%)","Difficulty","Weather","Temp (°C)"
    ]
    display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(display_df, use_container_width=True, hide_index=True, height=440)

    st.subheader("Descriptive Statistics")
    stats_df = filtered[["distance_km","pace_min","avg_hr","elevation_m","max_slope_pct","difficulty_score"]].describe().round(2)
    stats_df.index   = ["Count","Mean","Std Dev","Min","25%","Median","75%","Max"]
    stats_df.columns = ["Distance (km)","Pace (min/km)","Avg HR","Elevation (m)","Max Slope (%)","Difficulty Score"]
    st.dataframe(stats_df, use_container_width=True)

# ── Footer ───────────────────────────────────────────────
st.divider()
st.caption("STRIDEMAP · Art & Big Data · Seoul Running Course Analysis 2024")

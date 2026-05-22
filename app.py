import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# 1. Page Configuration (Ivory theme tone)
st.set_page_config(
    page_title="Run-Step: Running Course Recommendation",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Custom CSS for Ivory Background & Clean Design
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
    </style>
""", unsafe_allow_html=True)

# 2. Initialize Session State for Multi-step Navigation
if "diagnosed" not in st.session_state:
    st.session_state.diagnosed = False
if "user_level" not in st.session_state:
    st.session_state.user_level = "Beginner"

# 3. Dataset Setup with Geographic Coordinates for Interactive Maps
@st.cache_data
def load_course_data():
    # Coordinated simulation pathways for mapping routes
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["Han River Park Flat Trail", "Seokchon Lake Loop", "Neighborhood Green Park Trail", 
                       "Namsan Perimeter Trail", "Yangjaecheon-Tancheon Link", "North Seoul Dream Forest Uphill", 
                       "Mt. Inwangsan Trail Run", "Half Marathon Challenge Course", "The 10-Beat Hell Hill"],
        "Distance_KM": [3.0, 2.5, 2.0, 7.0, 8.5, 5.0, 12.0, 21.0, 15.0],
        "Elevation_Desc": ["Flat (Very Low)", "Flat (Low)", "Flat (Low)", "Sloped (Medium)", "Moderate (Medium)", "Steep (Medium-High)", "Rugged (High)", "Varied (High)", "Very Steep (Extreme)"],
        "Pros": ["Flat terrain with plenty of convenience stores and restrooms.", "Easy to maintain a steady pace with a beautiful night view.", "Highly accessible, safe, and well-lit for night running.",
                 "Abundant tree shades with great seasonal scenery.", "Perfect layout and distance for long-distance endurance training.", "Excellent for cardiovascular conditioning and stamina.",
                 "Immersive nature inside the city; never gets boring.", "Highly replicates actual marathon course conditions.", "Ultimate terrain for testing physical limits and leg strength."],
        "Cons": ["High volume of bicycles; runners must stay alert.", "Crowded with pedestrians; overtaking can be difficult.", "Short loop; can become repetitive and boring.",
                 "Frequent steep sections require careful pace distribution.", "Lack of shade; can get very hot during summer days.", "Initial steep uphill can be daunting for some runners.",
                 "High risk of injury; technical trail running shoes required.", "Energy supply points must be calculated in advance.", "Strictly prohibited for beginners; high impact on joints."],
        "Intensity": [2, 1, 1, 5, 4, 6, 8, 9, 10],
        # Start coordinates for maps [Latitude, Longitude]
        "Map_Center": [
            [37.5289, 126.9331], [37.5074, 127.1031], [37.5145, 127.0607],
            [37.5509, 126.9909], [37.4934, 127.0601], [37.6257, 127.0371],
            [37.5758, 126.9583], [37.5408, 127.0717], [37.5921, 126.9423]
        ]
    }
    return pd.DataFrame(data)

df = load_course_data()

# Simulated track segment generator to create continuous color-coded tracks
def get_simulated_route(center_lat, center_lng, num_points=20):
    points = []
    # Generates a continuous box/loop formation path
    for i in range(num_points):
        if i < 5:
            lat = center_lat + (i * 0.001)
            lng = center_lng
        elif i < 10:
            lat = center_lat + (5 * 0.001)
            lng = center_lng + ((i - 5) * 0.0015)
        elif i < 15:
            lat = center_lat + ((15 - i) * 0.001)
            lng = center_lng + (5 * 0.0015)
        else:
            lat = center_lat
            lng = center_lng + ((20 - i) * 0.0015)
        
        # Color segment assignment: alternates to mimic elevation variations
        # Green = Flat/Easy, Yellow = Moderate, Red = Steep Incline
        if i in [3, 4, 11, 12, 13]:
            color = "#E25B3C" # Red-orange for steep sections
        elif i in [2, 5, 10, 14]:
            color = "#FFD166" # Yellow for moderate slope
        else:
            color = "#06D6A0" # Green for flat paths
            
        points.append({"coord": [lat, lng], "color": color})
    return points

# --- STEP 1: WELCOME & DIAGNOSTIC PAGE ---
if not st.session_state.diagnosed:
    st.title("🏃‍♂️ Run-Step Datahub")
    st.subheader("Find the perfect running course tailored to your physical fitness.")
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
            
            st.session_state.diagnosed = True
            st.rerun()

# --- STEP 2: CUSTOM RECOMMENDATION DASHBOARD ---
else:
    if st.button("↩️ Re-take Diagnostic Test"):
        st.session_state.diagnosed = False
        st.rerun()
        
    st.title("🏃‍♂️ Your Custom Run-Step Dashboard")
    st.markdown(f"Analysis results show you are best suited for **{st.session_state.user_level}** level courses.")
    
    filtered_df = df[df["Level"] == st.session_state.user_level].reset_index(drop=True)
    st.markdown("---")
    
    st.write("### 📍 Top 3 Recommended Course Maps")
    st.write("Explore the interactive geographic dashboard. Move your mouse over charts and click route points to inspect terrain variants.")
    
    tab1, tab2, tab3 = st.tabs([
        f"1️⃣ {filtered_df.loc[0, 'Course_Name']}",
        f"2️⃣ {filtered_df.loc[1, 'Course_Name']}",
        f"3️⃣ {filtered_df.loc[2, 'Course_Name']}"
    ])
    
    # Helper layout rendering function containing map integration
    def render_course_tab(course_row):
        col_text, col_map = st.columns([1, 1.2])
        
        with col_text:
            st.markdown(f"#### 🏷️ {course_row['Course_Name']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("📏 Total Distance", f"{course_row['Distance_KM']} km")
            c2.metric("⛰️ Elevation Type", course_row['Elevation_Desc'])
            c3.metric("🔥 Intensity Score", f"{course_row['Intensity']} / 10")
            st.success(f"**👍 PROS:** {course_row['Pros']}")
            st.warning(f"**👎 CONS / CAUTIONS:** {course_row['Cons']}")
            
        with col_map:
            st.markdown("**🗺️ Route Elevation Visualizer**")
            st.caption("🟢 Green: Flat Terrain | 🟡 Yellow: Moderate Incline | 🔴 Red: Steep Incline")
            
            # Map initializing via folium
            m = folium.Map(location=course_row['Map_Center'], zoom_start=15, tiles="CartoDB positron")
            
            # Draw segment lines dynamically based on simulated elevation data
            route_points = get_simulated_route(course_row['Map_Center'][0], course_row['Map_Center'][1])
            for idx in range(len(route_points) - 1):
                p1 = route_points[idx]["coord"]
                p2 = route_points[idx+1]["coord"]
                color_code = route_points[idx]["color"]
                
                folium.PolyLine(
                    locations=[p1, p2],
                    color=color_code,
                    width=6,
                    opacity=0.9
                ).add_to(m)
            
            # Display marker for Start location
            folium.Marker(
                location=course_row['Map_Center'],
                popup="Start Point",
                icon=folium.Icon(color="black", icon="play", prefix="fa")
            ).add_to(m)
            
            # Render map component cleanly inside Streamlit layout
            st_folium(m, width=650, height=350, key=course_row['Course_Name'])

    with tab1:
        render_course_tab(filtered_df.iloc[0])
    with tab2:
        render_course_tab(filtered_df.iloc[1])
    with tab3:
        render_course_tab(filtered_df.iloc[2])
        
    st.markdown("---")
    
    # Bottom Summary Chart Section
    st.write("### 📊 Overall Recommended Course Overview")
    fig = px.bar(
        filtered_df, 
        x="Course_Name", 
        y="Intensity", 
        text="Distance_KM",
        labels={"Course_Name": "Course Name", "Intensity": "Intensity Score (1-10)"},
        color="Intensity",
        color_continuous_scale=px.colors.sequential.Sunsetdark
    )
    fig.update_traces(textposition='inside', texttemplate='%{text} km')
    fig.update_layout(
        plot_bgcolor="#FDFBF7",
        paper_bgcolor="#FDFBF7",
        xaxis_title="",
        uniformtext_mode='hide'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("Run-Step Dashboard v3.0 | Developed by Yeonhu Lee (SKKU Student ID: 2024314274)")

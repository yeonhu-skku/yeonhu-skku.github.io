import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Ivory theme tone and clean layout)
st.set_page_config(
    page_title="Run-Step: Running Course Recommendation",
    page_icon="🏃‍♂️",
    layout="wide"
)

# Custom CSS for Ivory Background & Clean Typography
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

# 3. Dataset Setup with Numeric Metrics for Visualization
@st.cache_data
def load_course_data():
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["Han River Park Flat Trail", "Seokchon Lake Loop", "Neighborhood Green Park Trail", 
                       "Namsan Perimeter Trail", "Yangjaecheon-Tancheon Link", "North Seoul Dream Forest Uphill", 
                       "Mt. Inwangsan Trail Run", "Half Marathon Challenge Course", "The 10-Beat Hell Hill"],
        "Distance_KM": [3.0, 2.5, 2.0, 7.0, 8.5, 5.0, 12.0, 21.0, 15.0],
        "Elevation_Score": [1, 2, 1, 5, 4, 6, 8, 7, 10],  # 1 (Flat/Green) to 10 (Steep/Red)
        "Elevation_Desc": ["Flat (Very Low)", "Flat (Low)", "Flat (Low)", "Sloped (Medium)", "Moderate (Medium)", "Steep (Medium-High)", "Rugged (High)", "Varied (High)", "Very Steep (Extreme)"],
        "Pros": ["Flat terrain with plenty of convenience stores and restrooms.", "Easy to maintain a steady pace with a beautiful night view.", "Highly accessible, safe, and well-lit for night running.",
                 "Abundant tree shades with great seasonal scenery.", "Perfect layout and distance for long-distance endurance training.", "Excellent for cardiovascular conditioning and stamina.",
                 "Immersive nature inside the city; never gets boring.", "Highly replicates actual marathon course conditions.", "Ultimate terrain for testing physical limits and leg strength."],
        "Cons": ["High volume of bicycles; runners must stay alert.", "Crowded with pedestrians; overtaking can be difficult.", "Short loop; can become repetitive and boring.",
                 "Frequent steep sections require careful pace distribution.", "Lack of shade; can get very hot during summer days.", "Initial steep uphill can be daunting for some runners.",
                 "High risk of injury; technical trail running shoes required.", "Energy supply points must be calculated in advance.", "Strictly prohibited for beginners; high impact on joints."],
        "Intensity": [2, 1, 1, 5, 4, 6, 8, 9, 10]
    }
    return pd.DataFrame(data)

df = load_course_data()

# --- STEP 1: WELCOME & DIAGNOSTIC PAGE ---
if not st.session_state.diagnosed:
    st.title("🏃‍♂️ Run-Step Datahub")
    st.subheader("Find the perfect running course tailored to your physical fitness.")
    st.write("Please answer two simple questions to unlock your custom running tracks.")
    st.markdown("---")
    
    # Clean, centered question layouts
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
    
    # Submit button to trigger result state
    if st.button("✨ Find My Custom Courses"):
        if user_pace == "Select your pace...":
            st.error("Please select your running pace to proceed!")
        else:
            # Diagnostic Logic
            if user_pace == "Over 7 minutes (Slow jog / walk-run)" or user_experience == "Less than 1 month (Beginner)":
                st.session_state.user_level = "Beginner"
            elif user_pace == "Under 4 minutes (Fast pace / competitive racing)" or user_experience == "More than 6 months (Advanced)":
                st.session_state.user_level = "Advanced"
            else:
                st.session_state.user_level = "Intermediate"
            
            st.session_state.diagnosed = True
            st.rerun()

# --- STEP 2: CUSTOM RECOMENDATION DASHBOARD ---
else:
    # Top navigation to go back or test again
    if st.button("↩️ Re-take Diagnostic Test"):
        st.session_state.diagnosed = False
        st.rerun()
        
    st.title("🏃‍♂️ Your Custom Run-Step Dashboard")
    st.markdown(f"Analysis results show you are best suited for **{st.session_state.user_level}** level courses.")
    
    # Filter dataset
    filtered_df = df[df["Level"] == st.session_state.user_level].reset_index(drop=True)
    
    st.markdown("---")
    
    # Interactive Tabs for Course Details
    st.write("### 📍 Top 3 Recommended Courses")
    
    tab1, tab2, tab3 = st.tabs([
        f"1️⃣ {filtered_df.loc[0, 'Course_Name']}",
        f"2️⃣ {filtered_df.loc[1, 'Course_Name']}",
        f"3️⃣ {filtered_df.loc[2, 'Course_Name']}"
    ])
    
    with tab1:
        st.markdown(f"#### 🏷️ {filtered_df.loc[0, 'Course_Name']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("📏 Total Distance", f"{filtered_df.loc[0, 'Distance_KM']} km")
        col2.metric("⛰️ Elevation Type", filtered_df.loc[0, 'Elevation_Desc'])
        col3.metric("🔥 Intensity Score", f"{filtered_df.loc[0, 'Intensity']} / 10")
        st.success(f"**👍 PROS:** {filtered_df.loc[0, 'Pros']}")
        st.warning(f"**👎 CONS / CAUTIONS:** {filtered_df.loc[0, 'Cons']}")
        
    with tab2:
        st.markdown(f"#### 🏷️ {filtered_df.loc[1, 'Course_Name']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("📏 Total Distance", f"{filtered_df.loc[1, 'Distance_KM']} km")
        col2.metric("⛰️ Elevation Type", filtered_df.loc[1, 'Elevation_Desc'])
        col3.metric("🔥 Intensity Score", f"{filtered_df.loc[1, 'Intensity']} / 10")
        st.success(f"**👍 PROS:** {filtered_df.loc[1, 'Pros']}")
        st.warning(f"**👎 CONS / CAUTIONS:** {filtered_df.loc[1, 'Cons']}")
        
    with tab3:
        st.markdown(f"#### 🏷️ {filtered_df.loc[2, 'Course_Name']}")
        col1, col2, col3 = st.columns(3)
        col1.metric("📏 Total Distance", f"{filtered_df.loc[2, 'Distance_KM']} km")
        col2.metric("⛰️ Elevation Type", filtered_df.loc[2, 'Elevation_Desc'])
        col3.metric("🔥 Intensity Score", f"{filtered_df.loc[2, 'Intensity']} / 10")
        st.success(f"**👍 PROS:** {filtered_df.loc[2, 'Pros']}")
        st.warning(f"**👎 CONS / CAUTIONS:** {filtered_df.loc[2, 'Cons']}")
        
    st.markdown("---")
    
    # 6. Nike-style Interactive Scatter Chart (Course Mapping)
    st.write("### 📊 NRC Style Course Mapping")
    st.write("Hover over the points to see interactive details. Green indicates flat, while Red indicates steep hills.")
    
    # Plotly interactive scatter chart with smooth hover animations
    fig = px.scatter(
        filtered_df,
        x="Distance_KM",
        y="Elevation_Score",
        size="Intensity",
        color="Elevation_Score",
        text="Course_Name",
        labels={"Distance_KM": "Course Distance (km)", "Elevation_Score": "Incline/Elevation Level"},
        color_continuous_scale="RdYlGn_r",  # Red-Yellow-Green reversed (Red=High, Green=Low)
        hover_data={"Distance_KM": True, "Elevation_Score": False, "Elevation_Desc": True, "Intensity": True, "Course_Name": False}
    )
    
    # Polishing chart visuals to match the Ivory theme
    fig.update_traces(textposition='top center', marker=dict(opacity=0.85, line=dict(width=1, color='DarkSlateGrey')))
    fig.update_layout(
        plot_bgcolor="#FDFBF7",
        paper_bgcolor="#FDFBF7",
        yaxis=dict(range=[0, 11], tickvals=[2, 5, 8, 10], ticktext=["Flat", "Moderate", "Steep", "Extreme"]),
        coloraxis_showscale=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Footer
    st.caption("Run-Step Dashboard v2.0 | Developed by Yeonhu Lee (SKKU Student ID: 2024314274)")

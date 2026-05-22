import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Run-Step: Running Course Recommendation",
    page_icon="🏃‍♂️",
    layout="wide"
)

# 2. Dataset Setup (Categorized by Skill Levels)
@st.cache_data
def load_course_data():
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["Han River Park Flat Trail", "Seokchon Lake Loop", "Neighborhood Green Park Trail", 
                       "Namsan Perimeter Trail", "Yangjaecheon-Tancheon Link", "North Seoul Dream Forest Uphill", 
                       "Mt. Inwangsan Trail Run", "Half Marathon Challenge Course", "The 10-Beat Hell Hill"],
        "Distance": ["3km", "2.5km", "2km", "7km", "8.5km", "5km", "12km", "21km", "15km"],
        "Elevation": ["Flat (Very Low)", "Flat (Low)", "Flat (Low)", "Sloped (Medium)", "Moderate (Medium)", "Steep (Medium-High)", "Rugged (High)", "Varied (High)", "Very Steep (Extreme)"],
        "Pros": ["Flat terrain with plenty of convenience stores and restrooms.", "Easy to maintain a steady pace with a beautiful night view.", "Highly accessible, safe, and well-lit for night running.",
                 "Abundant tree shades with great seasonal scenery.", "Perfect layout and distance for long-distance endurance training.", "Excellent for cardiovascular conditioning and stamina.",
                 "Immersive nature inside the city; never gets boring.", "Highly replicates actual marathon course conditions.", "Ultimate terrain for testing physical limits and leg strength."],
        "Cons": ["High volume of bicycles; runners must stay alert.", "Crowded with pedestrians; overtaking can be difficult.", "Short loop; can become repetitive and boring.",
                 "Frequent steep sections require careful pace distribution.", "Lack of shade; can get very hot during summer days.", "Initial steep uphill can be daunting for some runners.",
                 "High risk of injury; technical trail running shoes required.", "Energy supply points must be calculated in advance.", "Strictly prohibited for beginners; high impact on joints."],
        "Intensity": [2, 1, 1, 5, 4, 6, 8, 9, 10]  # Intensity metrics (1-10)
    }
    return pd.DataFrame(data)

df = load_course_data()

# 3. Sidebar - Skill-Level Diagnostic Assessment
st.sidebar.header("📋 Check Your Running Level")
st.sidebar.write("Answer the questions below to find your tailored running courses.")

# User inputs for diagnostic logic
user_pace = st.sidebar.selectbox(
    "What is your average pace per 1km?", 
    ["Not Selected", "Over 7 minutes (Slow jog / walk-run)", "5 to 6 minutes (Steady, continuous running)", "Under 4 minutes (Fast pace / competitive racing)"]
)
user_experience = st.sidebar.radio(
    "What is your running experience?", 
    ["Less than 1 month (Beginner)", "1 to 6 months (Consistent Runner)", "More than 6 months (Advanced)"]
)

# Logic for automatic level diagnosis
if user_pace == "Over 7 minutes (Slow jog / walk-run)" or user_experience == "Less than 1 month (Beginner)":
    default_level = "Beginner"
elif user_pace == "Under 4 minutes (Fast pace / competitive racing)" or user_experience == "More than 6 months (Advanced)":
    default_level = "Advanced"
else:
    default_level = "Intermediate"

st.sidebar.markdown("---")

# Let users manually override or select the level
selected_level = st.sidebar.selectbox(
    "Select the course difficulty to explore:", 
    ["Beginner", "Intermediate", "Advanced"], 
    index=["Beginner", "Intermediate", "Advanced"].index(default_level)
)

# 4. Main Header Section
st.title("🏃‍♂️ Run-Step Datahub")
st.subheader("Skill-Level Based Running Course Recommendation Dashboard")
st.markdown(f"Displaying the top 3 recommended courses optimized for **{selected_level}** runners.")

# Filter dataset based on selection
filtered_df = df[df["Level"] == selected_level].reset_index(drop=True)

st.markdown("---")

# 5. Interactive Tabs for Course Details (Click to Switch)
st.write("### 📍 Recommended Courses (Click on the tabs below to view Pros & Cons)")

tab1, tab2, tab3 = st.tabs([
    f"1️⃣ {filtered_df.loc[0, 'Course_Name']}",
    f"2️⃣ {filtered_df.loc[1, 'Course_Name']}",
    f"3️⃣ {filtered_df.loc[2, 'Course_Name']}"
])

with tab1:
    st.markdown(f"#### 🏷️ {filtered_df.loc[0, 'Course_Name']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("📏 Total Distance", filtered_df.loc[0, 'Distance'])
    col2.metric("⛰️ Elevation / Terrain", filtered_df.loc[0, 'Elevation'])
    col3.metric("🔥 Intensity Score", f"{filtered_df.loc[0, 'Intensity']} / 10")
    
    st.success(f"**👍 PROS:** {filtered_df.loc[0, 'Pros']}")
    st.warning(f"**👎 CONS / CAUTIONS:** {filtered_df.loc[0, 'Cons']}")

with tab2:
    st.markdown(f"#### 🏷️ {filtered_df.loc[1, 'Course_Name']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("📏 Total Distance", filtered_df.loc[1, 'Distance'])
    col2.metric("⛰️ Elevation / Terrain", filtered_df.loc[1, 'Elevation'])
    col3.metric("🔥 Intensity Score", f"{filtered_df.loc[1, 'Intensity']} / 10")
    
    st.success(f"**👍 PROS:** {filtered_df.loc[1, 'Pros']}")
    st.warning(f"**👎 CONS / CAUTIONS:** {filtered_df.loc[1, 'Cons']}")

with tab3:
    st.markdown(f"#### 🏷️ {filtered_df.loc[2, 'Course_Name']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("📏 Total Distance", filtered_df.loc[2, 'Distance'])
    col2.metric("⛰️ Elevation / Terrain", filtered_df.loc[2, 'Elevation'])
    col3.metric("🔥 Intensity Score", f"{filtered_df.loc[2, 'Intensity']} / 10")
    
    st.success(f"**👍 PROS:** {filtered_df.loc[2, 'Pros']}")
    st.warning(f"**👎 CONS / CAUTIONS:** {filtered_df.loc[2, 'Cons']}")

st.markdown("---")

# 6. Data Visualization Section (Plotly Chart)
st.write("### 📊 Intensity Level Comparison")
st.write("Higher scores indicate courses requiring greater cardiovascular stamina and physical strength.")

fig = px.bar(
    filtered_df, 
    x="Course_Name", 
    y="Intensity", 
    text="Distance",
    labels={"Course_Name": "Course Name", "Intensity": "Intensity Score (1-10)"},
    color="Intensity",
    color_continuous_scale=px.colors.sequential.Sunsetdark
)

fig.update_traces(textposition='inside')
fig.update_layout(xaxis_title="", uniformtext_mode='hide')

st.plotly_chart(fig, use_container_width=True)

# 7. Professional Academic Footer
st.caption("Run-Step Dashboard v1.0 | Developed by Yeonhu Lee (SKKU Student ID: 2024314274)")

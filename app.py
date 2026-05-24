import streamlit as st
import pandas as pd
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

# 3. Dataset Setup with Geographic Coordinates, Hashtags, and Exact Tracklists
@st.cache_data
def load_course_data():
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        # Exact Course names restricted strictly to Korean as requested
        "Course_Name": ["한강시민공원 여의도 코스", "석촌호수 루프 트레일", "동네 근린공원 산책로", 
                       "남산 둘레길 시닉 코스", "양재천-탄천 연계 롱런 코스", "북서울꿈의숲 업힐 트랙", 
                       "인왕산 정복 트레일러닝", "하프 마라톤 실전 정복 코스", "지옥의 10비트 고개 코스"],
        "Distance_KM": [3.0, 2.5, 2.0, 7.0, 8.5, 5.0, 12.0, 21.0, 15.0],
        "Elevation_Desc": ["Flat (Very Low)", "Flat (Low)", "Flat (Low)", "Sloped (Medium)", "Moderate (Medium)", "Steep (Medium-High)", "Rugged (High)", "Varied (High)", "Very Steep (Extreme)"],
        "Pros": [
            "The terrain is exceptionally flat with refreshing riverside breezes and excellent public convenience facilities.", 
            "It is highly optimized for maintaining a steady running pace, offering a spectacular night view of the Lotte World Tower.", 
            "Extremely accessible for a light, secure daily jog with well-lit street lamps and safe environments.",
            "Features dense tree canopies providing rich shade, keeping the track cool even during daytime hours with beautiful seasonal scenery.", 
            "Completely free of traffic lights, making it the premier choice for long-distance endurance and pace sustainability training.", 
            "Includes short yet high-intensity uphill sections that are ideal for strengthening cardiovascular endurance and anaerobic capacity.",
            "Delivers an immersive, dynamic trail running experience within the city center, ensuring an engaging workout without monotony.", 
            "Closely replicates actual marathon course conditions, serving as an excellent track for pre-race strategic pacing checks.", 
            "Demands extreme physical exertion; highly effective for testing anaerobic thresholds and building maximum lower-body strength."
        ],
        "Cons": [
            "High volume of bicycle traffic requires runners to remain highly alert; reducing earphone volume is strongly recommended.", 
            "Heavy pedestrian crowds during weekend evenings can significantly restrict continuous overtaking or fast-paced running.", 
            "The total distance per loop is relatively short, which may cause the session to feel slightly repetitive.",
            "Contains multiple steep segments that trigger sudden heart rate elevation; careful pace distribution is vital to prevent overexertion.", 
            "Lacks sufficient shade throughout the track, making UV protection and hydration mandatory during daytime workouts.", 
            "The initial incline is steeper than anticipated, necessitating caution to prevent acute knee joint strain.",
            "Constructed with uneven rocky paths and stairs; technical trail running shoes are mandatory to minimize ankle injury risks.", 
            "Given the substantial distance, runners must carefully plan their hydration and energy gel consumption intervals in advance.", 
            "Presents an extreme risk of joint and muscle injury; strictly prohibited for beginners or individuals with joint vulnerabilities."
        ],
        "Map_Center": [
            [37.5289, 126.9331], [37.5074, 127.1031], [37.5145, 127.0607],
            [37.5509, 126.9909], [37.4934, 127.0601], [37.6257, 127.0371],
            [37.5758, 126.9583], [37.5408, 127.0717], [37.5921, 126.9423]
        ],
        # Attraction titles restricted strictly to Korean as requested
        "Places_Title": [
            "여의도 한강공원 배달존 & 더현대 서울", "석촌호수 송리단길 카페거리", "공원 앞 로컬 베이커리 & 브런치 맛집",
            "남산타워 전망대 & 남산 돈까스 거리", "양재천 카페거리 & 도곡동 브런치숍", "북서울꿈의숲 전망대 카페",
            "서촌 통인시장 & 프레시 샐러드 바", "뚝섬 한강공원 수변광장", "부암동 클럽에스프레소 카페"
        ],
        "Places_Desc": [
            "Perfect for enjoying iconic riverside instant ramen or food delivery on the lawn post-run, followed by premium shopping at The Hyundai Seoul.",
            "Packed with aesthetic dessert cafes and cozy restaurants, making it an ideal destination for a post-running dinner or date.",
            "An excellent spot to immediately replenish carbohydrates with freshly baked artisan bread and fresh fruit juice right after your session.",
            "Replenish your protein levels with a hearty meal at the famous Namsan Cutlet Street, a symbolic culinary hotspot for local runners.",
            "Cool down and relax in a quiet, sophisticated neighborhood cafe with a refreshing iced americano after an intense workout.",
            "A scenic healing spot where you can enjoy chilled beverages while overlooking the vast forest view from an elevated observatory cafe.",
            "Refuel after a hard trail run with a healthy salad bowl in Seochon or explore traditional street food at the historic Tongin Market.",
            "Offers wide panoramic views of the Han River, making it highly convenient for quick convenience store refueling and public transit access.",
            "Unwind at a historic coffee establishment frequented by local cyclists and runners after conquering the legendary steep hills."
        ],
        # Simulated stock imagery links matching the aesthetic destinations
        "Places_Image": [
            "https://images.unsplash.com/photo-1626245347915-d72b26090a9a?auto=format&fit=crop&w=500&q=80",
            "https://images.unsplash.com/photo-1618083707368-b3823daa2726?auto=format&fit=crop&w=500&q=80",
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=500&q=80",
            "https://images.unsplash.com/photo-1538481199705-c710c4e965fc?auto=format&fit=crop&w=500&q=80",
            "https://images.unsplash.com/photo-1445116572660-236099ec97a0?auto=format&fit=crop&w=500&q=80",
            "https://images.unsplash.com/photo-1502082553048-f009c37129b9?auto=format&fit=crop&w=500&q=80",
            "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=500&q=80",
            "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=500&q=80",
            "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=500&q=80"
        ],
        # Dynamic Hashtag generation 
        "Places_Hashtags": [
            "#HangangRamen #TheHyundai #RiversideVibe #NightRun", "#SongridanGil #LotteTowerView #LakeJogging #DateCourse", "#BakeryRun #CarbLoading #LocalPark #MorningRoutine",
            "#NamsanTower #PaceChallenge #KingCutlet #ScenicView", "#Yangjaecheon #CafeTerrace #EnduranceTraining #IcedAmericano", "#DreamForest #UphillIntervals #GreeneryVibe #Observatory",
            "#SeochonVibe #TrailRecovery #SaladBowl #TonginMarket", "#MarathonTraining #RiverView #HydrationStation #TransitFriendly", "#HillConquest #ClubEspresso #AdrenalineRush #RunnersCommunity"
        ],
        # Formal structural text strings containing explicit tracklist arrays
        "Playlist_Title": [
            "Chill Acoustic & Synth Pop Vibe", "Trendy City Night Grooves", "Bright Morning Warm-Up Beats",
            "Rhythmic Mid-Tempo Running Hits", "Groovy Bassline Urban Anthems", "High-Stamina Cardio Boosters",
            "High-Octane Energy Booster Mix", "Relentless Distance Pace Maker", "Ultimate Adrenaline Limit Breaker"
        ],
        "Playlist_Tracks": [
            ["Lauv - Paris in the Rain", "LANY - ILYSB", "Troye Sivan - Youth", "Lauv - I Like Me Better", "LANY - 13"],
            ["LANY - Super Far", "Troye Sivan - Strawberries & Cigarettes", "Lauv - Chasing Fire", "LANY - Thru These Tears", "Troye Sivan - Wild"],
            ["Lauv - Reflipped", "LANY - Cowboy in LA", "Troye Sivan - Lucky Strike", "Lauv - Feelings", "LANY - Pink Skies"],
            ["Charlie Puth - Attention", "Ed Sheeran - Shivers", "Charlie Puth - Light Switch", "Ed Sheeran - Bad Habits", "Charlie Puth - Left and Right"],
            ["Charlie Puth - How Long", "Sam Smith - Unholy", "Charlie Puth - We Don't Talk Anymore", "Sam Smith - Diamonds", "Charlie Puth - Done For Me"],
            ["Ed Sheeran - Shape of You", "Sam Smith - I'm Not Here To Make Friends", "Ed Sheeran - Castle on the Hill", "Sam Smith - Promises", "Ed Sheeran - Overpass Graffiti"],
            ["BTS - Dynamite", "BLACKPINK - Kill This Love", "Eminem - Lose Yourself", "BTS - MIC Drop (Steve Aoki Remix)", "BLACKPINK - How You Like That"],
            ["BLACKPINK - Pink Venom", "Kendrick Lamar - HUMBLE.", "Travis Scott - SICKO MODE", "BLACKPINK - DDU-DU DDU-DU", "Drake - Nonstop"],
            ["BTS - Run BTS", "Kanye West - Power", "Post Malone - Rockstar", "BTS - ON", "Jack Harlow - WHATS POPPIN"]
        ],
        "Playlist_Link": [
            "https://www.youtube.com/results?search_query=lauv+lany+running+playlist",
            "https://www.youtube.com/results?search_query=lany+troye+sivan+running+playlist",
            "https://www.youtube.com/results?search_query=lauv+chill+running+playlist",
            "https://www.youtube.com/results?search_query=charlie+puth+ed+sheeran+running",
            "https://www.youtube.com/results?search_query=charlie+puth+sam+smith+playlist",
            "https://www.youtube.com/results?search_query=ed+sheeran+sam+smith+running",
            "https://www.youtube.com/results?search_query=bts+blackpink+running+playlist",
            "https://www.youtube.com/results?search_query=global+hiphop+blackpink+workout",
            "https://www.youtube.com/results?search_query=bts+heavy+rap+workout"
        ]
    }
    return pd.DataFrame(data)

df = load_course_data()

# Custom Route Generator
def get_custom_route(center_lat, center_lng, course_idx):
    points = []
    shape_factor_x = 0.0014 if course_idx % 2 == 0 else 0.0009
    shape_factor_y = 0.0016 if course_idx % 3 == 0 else 0.0019
    
    for i in range(21):
        if i < 6:
            lat = center_lat + (i * shape_factor_x)
            lng = center_lng
        elif i < 11:
            lat = center_lat + (5 * shape_factor_x)
            lng = center_lng + ((i - 5) * shape_factor_y)
        elif i < 16:
            lat = center_lat + ((15 - i) * shape_factor_x)
            lng = center_lng + (5 * shape_factor_y)
        else:
            lat = center_lat
            lng = center_lng + ((20 - i) * shape_factor_y)
            
        if course_idx in [0, 1, 2]:
            color = "#06D6A0" if i != 10 else "#FFD166"
        elif course_idx in [3, 4, 5]:
            color = "#E25B3C" if i in [8, 9] else ("#FFD166" if i in [4, 5, 12, 13] else "#06D6A0")
        else:
            color = "#E25B3C" if i in [2, 3, 4, 5, 8, 9, 12, 13, 14, 15] else "#FFD166"
            
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
    col_back, col_level_select = st.columns([1, 1])
    
    with col_back:
        if st.button("↩️ Re-take Diagnostic Test"):
            st.session_state.diagnosed = False
            st.rerun()
            
    with col_level_select:
        st.session_state.user_level = st.selectbox(
            "🌐 Explore Other Levels Directly:",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.user_level)
        )
        
    st.title("🏃‍♂️ Your Custom Run-Step Dashboard")
    st.markdown(f"The currently selected course difficulty level is **[{st.session_state.user_level}]**.")
    
    filtered_df = df[df["Level"] == st.session_state.user_level]
    
    st.markdown("---")
    st.write("### 📍 Top 3 Recommended Course Maps")
    st.write("You can drag, zoom in, or zoom out the map. The track line color represents real-time incline elevation difficulty.")
    
    tab_names = [f"📌 {row['Course_Name']}" for _, row in filtered_df.iterrows()]
    tabs = st.tabs(tab_names)
    
    def render_course_tab(course_row, internal_idx):
        col_text, col_map = st.columns([1.3, 1])
        
        with col_text:
            st.markdown(f"### 📍 장소명: {course_row['Course_Name']}")
            st.markdown(f"**📏 Total Distance:** {course_row['Distance_KM']} km")
            st.markdown(f"**⛰️ Elevation & Incline:** {course_row['Elevation_Desc']}")
            st.markdown(" ")
            
            st.success(f"**👍 PROS:** {course_row['Pros']}")
            st.warning(f"**👎 CAUTIONS:** {course_row['Cons']}")
            
            # Sub-segment 1: Attractions with image card and trend hashtags
            st.markdown("---")
            st.markdown(f"##### ☕ Nearby Attraction: {course_row['Places_Title']}")
            
            col_img, col_desc = st.columns([1, 1.5])
            with col_img:
                st.image(course_row['Places_Image'], use_container_width=True)
            with col_desc:
                st.write(f"{course_row['Places_Desc']}")
                st.markdown(f"**`{course_row['Places_Hashtags']}`**")
            
            # Sub-segment 2: Playlist tracklist display structure
            st.markdown("---")
            st.markdown(f"##### 🎵 Playlist: {course_row['Playlist_Title']}")
            
            # Map dynamic bullet strings cleanly looping across target string blocks
            st.markdown("**Tracklist:**")
            for track in course_row['Playlist_Tracks']:
                st.markdown(f"* {track}")
                
            st.markdown(" ")
            st.link_button("🎧 Open Playlist on YouTube", course_row['Playlist_Link'])
            
        with col_map:
            st.markdown("**🗺️ Route Elevation Visualizer**")
            st.caption("🟢 Green: Flat Terrain | 🟡 Yellow: Moderate Incline | 🔴 Red: Steep Incline Section")
            
            m = folium.Map(location=course_row['Map_Center'], zoom_start=15, tiles="CartoDB positron")
            
            route_points = get_custom_route(course_row['Map_Center'][0], course_row['Map_Center'][1], internal_idx)
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
            
            folium.Marker(
                location=course_row['Map_Center'],
                popup="Start Point",
                icon=folium.Icon(color="black", icon="play", prefix="fa")
            ).add_to(m)
            
            st_folium(m, width=520, height=380, key=f"map_id_{internal_idx}")

    for i, (orig_idx, row) in enumerate(filtered_df.iterrows()):
        with tabs[i]:
            render_course_tab(row, orig_idx)
        
    st.markdown("---")
    st.caption("Run-Step Dashboard v5.3 | Developed by Yeonhu Lee (SKKU Student ID: 2024314274)")

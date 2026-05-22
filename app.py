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

# 3. Dataset Setup with Geographic Coordinates & Nearby Places (Koreanized Content)
@st.cache_data
def load_course_data():
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["한강시민공원 여의도 코스", "석촌호수 루프 트레일", "동네 근린공원 산책로", 
                       "남산 둘레길 시닉 코스", "양재천-탄천 연계 롱런 코스", "북서울꿈의숲 업힐 트랙", 
                       "인왕산 정복 트레일러닝", "하프 마라톤 실전 정복 코스", "지옥의 10비트 고개 코스"],
        "Distance_KM": [3.0, 2.5, 2.0, 7.0, 8.5, 5.0, 12.0, 21.0, 15.0],
        "Elevation_Desc": ["평지 (최하)", "평지 (하)", "평지 (하)", "경사 있음 (중)", "완만함 (중)", "가파름 (중상)", "험난함 (상)", "다양함 (상)", "매우 가파름 (최상)"],
        "Pros": ["길이 매우 평탄하고 밤에 한강 바람이 시원하며 편의시설이 많습니다.", "페이스 유지가 아주 쉽고 롯데타워 야경이 예쁩니다.", "집 근처에서 안전하고 가볍게 달리기 좋으며 가로등이 밝습니다.",
                 "나무 그늘이 울창해 낮에도 시원하며 사계절 풍경이 아름답습니다.", "신호등이 없어 장거리 지속주 연습에 최적화된 코스입니다.", "짧고 강렬한 오르막 구간이 있어 심폐지구력 강화에 좋습니다.",
                 "도심 속 역동적인 자연을 느끼며 지루할 틈 없이 달릴 수 있습니다.", "실제 마라톤 주로와 유사하여 대회 전 페이스 점검에 좋습니다.", "경사가 매우 가파르고 한계 테스트 및 하체 근력 강화에 최고입니다."],
        "Cons": ["자전거 이용자가 아주 많으므로 이어폰 볼륨을 줄이고 주의해야 합니다.", "보행자가 많아 주말 저녁 시간대에는 추월이 다소 어렵습니다.", "코스 길이가 짧아 반복해서 돌면 약간 지루할 수 있습니다.",
                 "중간중간 숨이 차는 언덕이 포함되어 오버페이스를 조심해야 합니다.", "그늘이 다소 부족하여 낮 시간대 러닝 시 자외선 차단이 필수입니다.", "초반 진입 오르막이 생각보다 가파르니 무릎 부상에 주의하세요.",
                 "돌길과 계단이 많아 발목 부상 위험이 크므로 트레일화가 필수입니다.", "장거리인 만큼 급수 및 에너지 보급 계획을 미리 세워야 합니다.", "초보자는 무릎과 관절에 큰 무리가 갈 수 있으니 절대 금지합니다."],
        "Map_Center": [
            [37.5289, 126.9331], [37.5074, 127.1031], [37.5145, 127.0607],
            [37.5509, 126.9909], [37.4934, 127.0601], [37.6257, 127.0371],
            [37.5758, 126.9583], [37.5408, 127.0717], [37.5921, 126.9423]
        ],
        "Places_Title": [
            "여의도 한강공원 배달존 & 더현대 서울", "석촌호수 송리단길 카페거리", "공원 앞 로컬 베이커리 & 브런치 맛집",
            "남산타워 전망대 & 남산 돈까스 거리", "양재천 카페거리 & 도곡동 브런치숍", "북서울꿈의숲 전망대 카페",
            "서촌 통인시장 & 프레시 샐러드 바", "뚝섬 한강공원 수변광장", "부암동 클럽에스프레소 카페"
        ],
        "Places_Desc": [
            "러닝 후 잔디밭에서 시원한 라면이나 배달 음식을 즐기거나 더현대 서울에서 쇼핑하기 좋습니다.",
            "예쁜 디저트 카페와 아기자기한 레스토랑이 많아 러닝 후 데이트 코스로 완벽합니다.",
            "러닝을 마치고 가볍게 갓 구운 빵과 신선한 주스로 탄수화물을 보충하기 좋은 스팟입니다.",
            "러닝 후 러너들의 성지인 남산 돈까스 거리에서 든든하게 단백질을 충전해 보세요.",
            "조용하고 세련된 카페거리에서 시원한 아이스 아메리카노를 마시며 땀을 식히기 좋습니다.",
            "탁 트인 전망대 카페에서 숲을 바라보며 시원한 음료를 즐길 수 있는 힐링 명소입니다.",
            "하드한 트레일러닝 후 서촌 감성의 샐러드 맛집이나 통인시장 기름떡볶이로 허기를 채워보세요.",
            "도심 속 넓은 한강 뷰를 감상하며 편의점 보급을 하거나 대중교통 연계가 매우 편리합니다.",
            "지옥의 업힐을 정복한 후, 라이더들과 러너들이 모이는 전통 있는 커피 맛집에서 휴식을 취하세요."
        ]
    }
    return pd.DataFrame(data)

df = load_course_data()

# Custom Route Generator for distinct unique tracks based on course indexes
def get_custom_route(center_lat, center_lng, course_idx):
    points = []
    # Variations in route shapes based on the index to make maps look completely different
    shape_factor_x = 0.0012 if course_idx % 2 == 0 else 0.0008
    shape_factor_y = 0.0015 if course_idx % 3 == 0 else 0.0018
    
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
            
        # Unique color elevation grading based on the specific course index
        if course_idx in [0, 1, 2]: # Beginners: Mostly flat (Greens)
            color = "#06D6A0" if i not in [7, 8] else "#FFD166"
        elif course_idx in [3, 4, 5]: # Intermediates: Moderate hills (Yellows/Greens)
            color = "#FFD166" if i in [3, 4, 11, 12] else ("#E25B3C" if i in [7, 8] else "#06D6A0")
        else: # Advanced: High steep slopes (Reds/Yellows)
            color = "#E25B3C" if i in [2, 3, 4, 10, 11, 12, 13] else "#FFD166"
            
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
        # Added feature allowing exploration of other skill levels seamlessly via top dropdown
        st.session_state.user_level = st.selectbox(
            "🌐 Explore Other Levels Directly:",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.user_level)
        )
        
    st.title("🏃‍♂️ Your Custom Run-Step Dashboard")
    st.markdown(f"현재 선택된 추천 지형 분석 레벨은 **[{st.session_state.user_level}]** 입니다.")
    
    # Extract row indexes properly based on dataframe entries
    filtered_df = df[df["Level"] == st.session_state.user_level]
    
    st.markdown("---")
    st.write("### 📍 Top 3 Recommended Course Maps")
    st.write("지도를 드래그하거나 확대해 볼 수 있습니다. 코스 선의 색상은 실시간 경사 난이도를 의미합니다.")
    
    # Dynamic list for rendering tabs based on exact names
    tab_names = [f"📌 {row['Course_Name']}" for _, row in filtered_df.iterrows()]
    tabs = st.tabs(tab_names)
    
    def render_course_tab(course_row, internal_idx):
        col_text, col_map = st.columns([1, 1.2])
        
        with col_text:
            st.markdown(f"#### 🏷️ {course_row['Course_Name']}")
            c1, c2 = st.columns(2)
            c1.metric("📏 총 거리", f"{course_row['Distance_KM']} km")
            c2.metric("⛰️ 고도 및 경사도", course_row['Elevation_Desc'])
            
            st.success(f"**👍 장점:** {course_row['Pros']}")
            st.warning(f"**👎 주의사항:** {course_row['Cons']}")
            
            # Brand new custom sub-section tab: Nearby Hotspots Recommendation
            st.markdown("---")
            st.markdown(f"##### ☕ 근처 추천 핫플레이스: **{course_row['Places_Title']}**")
            st.info(f"{course_row['Places_Desc']}")
            
        with col_map:
            st.markdown("**🗺️ 코스 상세 경로 시각화**")
            st.caption("🟢 초록색: 평탄한 구간 | 🟡 노란색: 완만한 경사 | 🔴 빨간색: 가파른 경사 구간")
            
            m = folium.Map(location=course_row['Map_Center'], zoom_start=15, tiles="CartoDB positron")
            
            # Apply dynamic route paths and color parameters depending on specific index mapping
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
            
            st_folium(m, width=650, height=380, key=f"map_id_{internal_idx}")

    # Render each row item uniquely onto designated tabs
    for i, (orig_idx, row) in enumerate(filtered_df.iterrows()):
        with tabs[i]:
            render_course_tab(row, orig_idx)
        
    st.markdown("---")
    st.caption("Run-Step Dashboard v4.0 | Developed by Yeonhu Lee (SKKU Student ID: 2024314274)")

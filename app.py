import streamlit as st
import pandas as pd
import folium
import altair as alt
import plotly.graph_objects as go
from streamlit_folium import st_folium
import math

def load_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        .stApp {
            background: linear-gradient(180deg, #FAFAF8 0%, #F5F3EE 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        h1 { font-size: 2.75rem !important; font-weight: 800 !important; letter-spacing: -0.03em !important; color: #1A1A1A !important; line-height: 1.1 !important; }
        h2 { font-size: 1.5rem !important; font-weight: 700 !important; letter-spacing: -0.02em !important; color: #1A1A1A !important; }
        h3 { font-size: 1.125rem !important; font-weight: 600 !important; color: #2D2D2D !important; }
        p, .stMarkdown { color: #4A4A4A; line-height: 1.6; }
        
        .premium-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .premium-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.04);
        }
        
        .hero-image-container {
            width: 100%;
            height: 300px;
            border-radius: 20px;
            overflow: hidden;
            margin-bottom: 24px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
            position: relative;
        }
        .hero-image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .metric-container {
            background: linear-gradient(135deg, #1A1A1A 0%, #2D2D2D 100%);
            border-radius: 16px;
            padding: 20px 24px;
            text-align: center;
            transition: transform 0.2s ease;
            height: 100%;
        }
        .metric-container:hover { transform: scale(1.02); }
        .metric-value { font-size: 2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em; margin-bottom: 4px; }
        .metric-label { font-size: 0.75rem; font-weight: 600; color: rgba(255, 255, 255, 0.6); text-transform: uppercase; letter-spacing: 0.08em; }
        
        .metric-accent { background: linear-gradient(135deg, #E85A3C 0%, #D64A2C 100%); }
        
        .tag-pill {
            display: inline-block; background: #F0EDE6; color: #5C5C5C;
            padding: 6px 14px; border-radius: 20px; font-size: 0.8rem;
            font-weight: 500; margin: 4px 4px 4px 0; transition: all 0.2s ease;
        }
        .tag-pill:hover { background: #E8E4DC; color: #3A3A3A; }
        
        .level-badge {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 8px 16px; border-radius: 24px; font-size: 0.85rem;
            font-weight: 600; letter-spacing: -0.01em;
        }
        .level-beginner { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); color: #2E7D32; }
        .level-intermediate { background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); color: #E65100; }
        .level-advanced { background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%); color: #C62828; }
        
        .stTabs [data-baseweb="tab-list"] { gap: 8px; background: transparent; padding: 4px; }
        .stTabs [data-baseweb="tab"] {
            background: #F0EDE6 !important; border-radius: 12px !important; padding: 12px 24px !important;
            font-weight: 600 !important; font-size: 0.9rem !important; color: #5C5C5C !important;
            border: none !important; transition: all 0.2s ease !important;
        }
        .stTabs [data-baseweb="tab"]:hover { background: #E8E4DC !important; color: #1A1A1A !important; }
        .stTabs [aria-selected="true"] { background: #1A1A1A !important; color: #FFFFFF !important; }
        .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none; }
        
        .custom-divider { height: 1px; background: linear-gradient(90deg, transparent, #E8E4DC, transparent); margin: 32px 0; }
        .section-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
        .section-icon { width: 40px; height: 40px; background: #F0EDE6; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    if "page_stage" not in st.session_state:
        st.session_state.page_stage = "welcome"
    if "user_level" not in st.session_state:
        st.session_state.user_level = "Beginner"

@st.cache_data
def load_course_data() -> pd.DataFrame:
    data = {
        "Level": ["Beginner", "Beginner", "Beginner", "Intermediate", "Intermediate", "Intermediate", "Advanced", "Advanced", "Advanced"],
        "Course_Name": ["Yeouido Hangang", "Seokchon Lake", "Neighborhood Park", "Namsan Dulle-gil", "Yangjaecheon", "Dream Forest", "Inwangsan Trail", "Ttukseom Hangang", "Buamdong Hills"],
        "Course_Name_KR": ["여의도 한강공원", "석촌호수", "동네 근린공원", "남산 둘레길", "양재천", "북서울꿈의숲", "인왕산", "뚝섬 한강공원", "부암동"],
        "Distance_KM": [3.0, 2.5, 2.0, 7.0, 8.5, 5.0, 12.0, 21.0, 15.0],
        "Estimated_Time": ["25 min", "20 min", "15 min", "55 min", "65 min", "45 min", "100 min", "160 min", "130 min"],
        "Calories": [180, 150, 120, 450, 550, 320, 900, 1600, 1200],
        "Elevation_Gain": [5, 3, 2, 120, 45, 85, 280, 50, 320],
        "Surface": ["Paved", "Paved", "Paved", "Mixed", "Paved", "Mixed", "Trail", "Paved", "Trail"],
        "Scenery_Score": [8, 9, 5, 9, 7, 8, 10, 8, 9],
        "Facility_Score": [10, 9, 6, 7, 8, 7, 4, 10, 5],
        "Safety_Score": [8, 9, 9, 8, 9, 8, 6, 8, 6],
        "Difficulty_Score": [2, 1, 1, 5, 4, 4, 8, 7, 10],
        "Image_URL": [
            "https://images.unsplash.com/photo-1620078028723-5e92750e41f7?q=80&w=1600&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1599839619722-39751411ea63?q=80&w=1600&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1497436072909-60f360e1d4b1?q=80&w=1600&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1517154421773-0529f29ea451?q=80&w=1600&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1506751470038-d52292150334?q=80&w=1600&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327?q=80&w=1600&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1551633550-619741b655cc?q=80&w=1600&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1613134882583-04e76d75d31d?q=80&w=1600&auto=format&fit=crop", 
            "https://images.unsplash.com/photo-1518098268026-4e89f1a2cd8e?q=80&w=1600&auto=format&fit=crop"
        ],
        "Map_Center": [
            [37.5289, 126.9331], [37.5074, 127.1031], [37.5145, 127.0607],
            [37.5509, 126.9909], [37.4934, 127.0601], [37.6257, 127.0371],
            [37.5758, 126.9583], [37.5408, 127.0717], [37.5921, 126.9423]
        ]
    }
    return pd.DataFrame(data)

def generate_elevation_data(distance: float, max_elevation: int) -> pd.DataFrame:
    points = 50
    x_vals = [i * (distance / points) for i in range(points + 1)]
    y_vals = [max(0, max_elevation * math.sin(math.pi * (i / points)) + (max_elevation * 0.1 * math.sin(3 * math.pi * (i / points)))) for i in range(points + 1)]
    return pd.DataFrame({"Distance (km)": x_vals, "Elevation (m)": y_vals})

def get_route_coordinates(center_lat: float, center_lng: float) -> dict:
    return {
        "coords": [
            [center_lat, center_lng], [center_lat + 0.002, center_lng + 0.001],
            [center_lat + 0.003, center_lng + 0.004], [center_lat + 0.001, center_lng + 0.005],
            [center_lat - 0.001, center_lng + 0.003], [center_lat, center_lng]
        ],
        "colors": ["#22C55E", "#F59E0B", "#EF4444", "#F59E0B", "#22C55E", "#22C55E"]
    }

def create_radar_chart(row):
    categories = ['Scenery', 'Facilities', 'Safety', 'Difficulty', 'Scenery']
    values = [row['Scenery_Score'], row['Facility_Score'], row['Safety_Score'], row['Difficulty_Score'], row['Scenery_Score']]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(232, 90, 60, 0.2)',
        line=dict(color='#E85A3C', width=2),
        name='Route Profile'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], gridcolor='rgba(0,0,0,0.1)'),
            angularaxis=dict(gridcolor='rgba(0,0,0,0.1)')
        ),
        showlegend=False,
        margin=dict(l=30, r=30, t=30, b=30),
        height=300
    )
    return fig

def render_dashboard_page(df: pd.DataFrame):
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    with header_col1:
        st.markdown(f'<div style="display: flex; align-items: center; gap: 16px;"><h1 style="margin: 0;">Route Intelligence</h1></div>', unsafe_allow_html=True)
    with header_col2:
        new_level = st.selectbox("Switch Level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.user_level), label_visibility="collapsed")
        if new_level != st.session_state.user_level:
            st.session_state.user_level = new_level
            st.rerun()
            
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    filtered_df = df[df["Level"] == st.session_state.user_level]
    
    overall_chart_col1, overall_chart_col2 = st.columns([1, 1])
    with overall_chart_col1:
        st.markdown('<div class="premium-card"><h3 style="margin-top:0;">Distance vs Calories</h3>', unsafe_allow_html=True)
        bar_chart = alt.Chart(filtered_df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, color='#1A1A1A').encode(
            x=alt.X('Course_Name', sort=None, title=None, axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Calories', title='Calories Burned'),
            tooltip=['Course_Name', 'Distance_KM', 'Calories']
        ).properties(height=250)
        st.altair_chart(bar_chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with overall_chart_col2:
        st.markdown('<div class="premium-card"><h3 style="margin-top:0;">Elevation Profile Comparison</h3>', unsafe_allow_html=True)
        scatter = alt.Chart(filtered_df).mark_circle(size=200, color='#E85A3C').encode(
            x=alt.X('Distance_KM', title='Total Distance (km)'),
            y=alt.Y('Elevation_Gain', title='Elevation Gain (m)'),
            tooltip=['Course_Name', 'Distance_KM', 'Elevation_Gain']
        ).properties(height=250)
        st.altair_chart(scatter, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    tabs = st.tabs([row['Course_Name'] for _, row in filtered_df.iterrows()])
    
    for tab_idx, (_, row) in enumerate(filtered_df.iterrows()):
        with tabs[tab_idx]:
            st.markdown(f'<div class="hero-image-container"><img src="{row["Image_URL"]}" alt="Route scenery"></div>', unsafe_allow_html=True)
            
            st.markdown(f'<div style="margin-bottom: 24px;"><h2 style="margin-bottom: 4px;">{row["Course_Name"]}</h2><p style="color: #8A8A8A;">{row["Course_Name_KR"]}</p></div>', unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            metrics = [
                (m1, "metric-accent", row['Distance_KM'], "Kilometers"),
                (m2, "", row['Estimated_Time'], "Avg. Time"),
                (m3, "", row['Calories'], "Calories"),
                (m4, "", f"{row['Elevation_Gain']}m", "Elevation")
            ]
            for col, cls, val, label in metrics:
                with col:
                    st.markdown(f'<div class="metric-container {cls}"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            chart_col, map_col = st.columns([1, 1])
            
            with chart_col:
                st.markdown('<div class="premium-card"><h3 style="margin-top:0;">Route Diagnostics</h3>', unsafe_allow_html=True)
                radar_fig = create_radar_chart(row)
                st.plotly_chart(radar_fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
            with map_col:
                st.markdown('<div class="premium-card"><h3 style="margin-top:0;">Interactive Map</h3>', unsafe_allow_html=True)
                m = folium.Map(location=row['Map_Center'], zoom_start=15, tiles="CartoDB positron")
                route_data = get_route_coordinates(row['Map_Center'][0], row['Map_Center'][1])
                coords, colors = route_data["coords"], route_data["colors"]
                for i in range(len(coords) - 1):
                    folium.PolyLine(locations=[coords[i], coords[i + 1]], color=colors[i], weight=6, opacity=0.9).add_to(m)
                st_folium(m, width=None, height=300, key=f"map_{row['Course_Name']}")
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
        <div style="text-align: center; padding: 20px; color: #8A8A8A; font-size: 0.8rem;">
            Run-Step v3.0 · Built with Streamlit<br>
            Yeonhu Lee · Sungkyunkwan University · 2024314274
        </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Run-Step | Analytics", page_icon="🏃", layout="wide")
    load_css()
    init_session_state()
    df = load_course_data()
    render_dashboard_page(df)

if __name__ == "__main__":
    main()

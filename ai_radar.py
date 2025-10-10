import json
import math
import random
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from PIL import Image
from io import BytesIO
import base64

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(120deg, #463aef 0%, #af40f0 100%);
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
        display: flex;
        flex-direction: column;
    }
    .header {
        display: flex;
        animation: fadeInDown 1.2s ease-in-out;
    }
    [data-testid="stSidebar"] {
           background: #022a87;
           box-shadow: 0 4px 24px rgba(67,198,172,0.15);
           border-radius: 16px;
           transition: all 0.3s ease;
    }
    h1, h2, h3 {
        color: #2a4d8f;
        font-weight: 900;
        letter-spacing: 2px;
        text-shadow: 0 2px 8px #43c6ac33;
    }
    .icon {
        font-size: 32px;
        margin-right: 12px;
        filter: drop-shadow(0 2px 8px #43c6ac33);
    }
    .banner-container {
        width: 100%;
        height: 200px; 
        overflow: hidden;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 0 100px rgba(67,198,172,0.15);
        animation: glowPulse 0.5s infinite alternate;
        display: flex;
    }
    .banner-container img {
        width: 100%;
        height: 100%;
        object-fit: cover; 
        animation: slideIn 2s ease-out;
    }
    .project-detail-box {
        background: linear-gradient(135deg, #022a87 0%, #463aef 100%);
        border: 3px solid #00f7ff;
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,247,255,0.4);
        animation: slideInUp 0.4s ease-out;
    }
    .project-detail-box h2 {
        color: #00f7ff !important;
        margin-bottom: 15px;
    }
    .detail-badge {
        background: rgba(0,247,255,0.2);
        border: 1px solid #00f7ff;
        border-radius: 8px;
        padding: 8px 16px;
        display: inline-block;
        margin: 5px;
        color: #00f7ff;
        font-weight: bold;
    }
    details summary {
        font-weight: bold;
        font-size: 1.1rem;
        color: #00f7ff;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    details summary:hover {
        color: #ffffff;
        text-shadow: 0 0 8px cyan;
        transform: scale(1.05);
    }
    div.stDownloadButton > button {
        background: linear-gradient(120deg, #463aef 0%, #af40f0 100%);
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6em 1.2em !important;
        font-weight: bold !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important;
        transition: all 0.3s ease-in-out;
    }
    div.stDownloadButton > button:hover {
        background: #022a87;
        transform: scale(1.05);
    }
    @keyframes glowPulse {
        from { box-shadow: 0 0 10px rgba(0,255,255,0.3); }
        to { box-shadow: 0 0 100px rgba(0,255,255,0.9); }
    }
     @keyframes slideIn {
        from { transform: translateY(-30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes slideInUp {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="AI Radar")

banner=Image.open("banner.png")
buffered = BytesIO()
banner.save(buffered, format="PNG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()
st.markdown(
    f"""
    <div class="banner-container">
        <img src="data:image/png;base64,{img_base64}" />
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="header" style="color:cyan;display:flex;align-items:center;gap:16px;"><span class="icon">🚀</span><h1 style="margin:0;">AI Radar - Project Maturity</h1></div>', unsafe_allow_html=True)
if 'selected_project' not in st.session_state:
    st.session_state.selected_project = None
if 'chart_version' not in st.session_state:
    st.session_state.chart_version = 0

uploaded_file = st.file_uploader("Upload a JSON file with project data", type=["json"], accept_multiple_files=True)
projects = []
if uploaded_file:
    for file in uploaded_file:
        projects.extend(json.load(file))
else:
    st.info("Upload a config.json file to see the radar")
    st.stop()

search_col1, = st.columns(1)
with search_col1:
    search_term = st.text_input(
        "🔍 Search Projects", 
        placeholder="Type project name...",
        key="search_input",
        help="Search projects by name - matching projects will be highlighted on the radar"
    )
st.markdown("---")

quadrants = ["New", "Emerging", "Mature", "Established"]
rings = ["Adopt", "Trial", "Assess", "Hold"]
quadrants_map = {"New":(0,90), "Emerging":(90,180), "Mature":(180,270), "Established":(270,360)}
rings_map = {"Adopt": 1, "Trial": 2, "Assess": 3, "Hold": 4}
quadrant_colors = {
    "New": "#4e79a7",
    "Emerging": "#f28e2b", 
    "Mature": "#e15759",
    "Established": "#59a14f"
}

st.sidebar.markdown('<div style="color:cyan;display:flex;align-items:center;gap:12px;"><span class="icon">🟢</span><h1 style="margin:0;">Radar Rings</h1></div>', unsafe_allow_html=True)
st.sidebar.info("💡 Click on any project blip in the radar to see its details!")
for ring in rings:
    with st.sidebar.expander(ring):
        ring_projects = [p for p in projects if p["ring"] == ring]
        if ring_projects:
            for proj in ring_projects:
                with st.expander(f"💡 {proj['name']}"):
                    st.write(proj.get("info", "No info available."))
        else:
            st.write("No projects in this ring.")

base_height = 900
if len(projects) > 20:
    chart_height = base_height + (len(projects) - 20) * 15 
    chart_height = min(chart_height, 1500) 
else:
    chart_height = base_height
text_size = 10 if len(projects) <= 30 else 8 if len(projects) <= 50 else 6

fig=go.Figure()
max_radius = len(rings_map) 
for i in range(1, max_radius + 1):
    fig.add_shape(type="circle",
                  xref="x", yref="y",
                  x0=-i, y0=-i, x1=i, y1=i,
                  line=dict(color="#76b7b2", width=2, dash="dot"))
    fig.add_annotation(
        x=0, y=i-0.5,
        text=rings[i-1],
        showarrow=False,
        font=dict(size=12, color="#00d9ff", family="Arial Black"),
        bgcolor="rgba(15,52,96,0.8)",
        bordercolor="#00d9ff",
        borderwidth=1,
        borderpad=4
    )
for angle in [0, 90, 180, 270]:
    x = max_radius * np.cos(np.radians(angle))
    y = max_radius * np.sin(np.radians(angle))
    fig.add_shape(type="line",
                  x0=0, y0=0, x1=x, y1=y,
                  line=dict(color="#2a4d8f", width=2))

fig.add_annotation(x=max_radius*0.9, y=max_radius*0.9, text="<b>NEW</b>", 
                   showarrow=False, font=dict(size=18, color=quadrant_colors["New"], family="Arial Black"))
fig.add_annotation(x=-max_radius*0.9, y=max_radius*0.9, text="<b>EMERGING</b>", 
                   showarrow=False, font=dict(size=18, color=quadrant_colors["Emerging"], family="Arial Black"))
fig.add_annotation(x=-max_radius*0.9, y=-max_radius*0.9, text="<b>MATURE</b>", 
                   showarrow=False, font=dict(size=18, color=quadrant_colors["Mature"], family="Arial Black"))
fig.add_annotation(x=max_radius*0.9, y=-max_radius*0.9, text="<b>ESTABLISHED</b>", 
                   showarrow=False, font=dict(size=18, color=quadrant_colors["Established"], family="Arial Black"))

placement_grid = {}
for proj in projects:
    key = (proj["quadrant"], proj["ring"])
    if key not in placement_grid:
        placement_grid[key] = []
    placement_grid[key].append(proj)
for idx, proj in enumerate(projects, start=1):
    q_angle = quadrants_map.get(proj["quadrant"], (0, 90))
    ring_val = rings_map.get(proj["ring"], 4)
    key = (proj["quadrant"], proj["ring"])
    projects_in_cell = placement_grid[key]
    proj_index = projects_in_cell.index(proj)
    total_in_cell = len(projects_in_cell)
    quadrant_span = q_angle[1] - q_angle[0]
    angle_step = quadrant_span / (total_in_cell + 1)
    angle = q_angle[0] + angle_step * (proj_index + 1)
    r = ring_val - 0.5
    x = r * np.cos(np.radians(angle))
    y = r * np.sin(np.radians(angle))
    is_selected = st.session_state.selected_project and st.session_state.selected_project['name'] == proj['name']

    is_search_match = search_term and search_term.lower() in proj["name"].lower()
    has_search = bool(search_term)
    if has_search:
        marker_opacity = 1.0 if is_search_match else 0.2  
    else:
        marker_opacity = 0.85
    fig.add_trace(go.Scatter(
        x=[x], y=[y],
        mode="markers",
        name=proj["name"],
        customdata=[proj["name"]],
        marker=dict(
            size=16 if is_selected else 12,
            opacity=marker_opacity,
            color=quadrant_colors.get(proj["quadrant"], "#ffffff"),
            line=dict(width=3 if is_selected else 2, color="#ffffff" if is_selected else "#2a4d8f")
        ),
        hovertemplate=f"<b>{proj['name']}</b><br>Quadrant: {proj['quadrant']}<br>Ring: {proj['ring']}<br><i>Click to view details</i><extra></extra>",
        hoverlabel=dict(bgcolor=quadrant_colors.get(proj["quadrant"], "#000000"), font=dict(color="white"))
    ))

fig.update_layout(
    showlegend=False,
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    title="<span style='color:cyan'>AI Radar (Quadrants = Maturity, Rings = Depth)</span>",
    height=900,
    plot_bgcolor="#f0f4fc",
    paper_bgcolor="#022a87",
    hovermode='closest'
)

chart_key = f"radar_chart_{st.session_state.get('chart_version', 0)}"
event = st.plotly_chart(fig, use_container_width=False, on_select="rerun", selection_mode="points", key=chart_key)
if event and event.selection and event.selection.points:
    clicked_point = event.selection.points[0]
    clicked_project_name = clicked_point.get('customdata', None)
    if clicked_project_name:
        clicked_project = next((p for p in projects if p["name"] == clicked_project_name), None)
        if clicked_project:
            st.session_state.selected_project = clicked_project
if st.session_state.selected_project:
    st.markdown("---")
    with st.expander(f"📋 Project Details: {st.session_state.selected_project['name']}", expanded=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"## 🎯 {st.session_state.selected_project['name']}")
        with col2:
            if st.button("✖ Close", key="close_btn", type="primary"):
                st.session_state.selected_project = None
                st.session_state.chart_version += 1
                st.rerun()    
        st.markdown("---")   
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Quadrant", st.session_state.selected_project["quadrant"])
        with col2:
            st.metric("🎯 Ring", st.session_state.selected_project["ring"])
        with col3:
            status = "✅ Active" if st.session_state.selected_project['ring'] in ["Adopt", "Trial"] else "👁️ Monitor"
            st.metric("📈 Status", status)
        st.markdown("---")
        st.markdown("### 📝 Project Information")
        info_text = st.session_state.selected_project.get("info", "No additional information available.")
        st.write(info_text)
    st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown('<span style="color:cyan;font-size:24px;font-weight:bold;">📌Quadrants & Rings</span>', unsafe_allow_html=True)
        st.write("**Quadrants:** New, Emerging, Mature, Established")
        st.write("**Rings:** " + ", ".join(rings))
with col2:
    with st.container(border=True):
        st.markdown('<span style="color:cyan;font-size:24px;font-weight:bold;">📊 Statistics</span>', unsafe_allow_html=True)
        st.metric("Total Projects", len(projects))
        cols = st.columns(4)
        for i, ring in enumerate(rings):
            with cols[i]:
                count = len([p for p in projects if p["ring"] == ring])
                st.metric(ring, count)

with st.container(border=True):
    st.markdown(
    "<h3 style='color:cyan;font-size:24px;font-weight:bold;'>📚Projects by Maturity</h3>", 
    unsafe_allow_html=True
    )
    for q in quadrants:
        q_projects = [p["name"] for p in projects if p["quadrant"] == q]
        st.markdown(f"**{q}** ({len(q_projects)}): {', '.join(q_projects) if q_projects else 'None'}")

df=pd.DataFrame(projects)
col1, col2 = st.columns(2)
with col1:
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Project Data as CSV",
        data=csv,
        file_name='ai_projects.csv',
        mime='text/csv',
        key='download-csv'
    )
with col2:
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='AI Projects')
    st.download_button(
        label="📥 Download Project Data as Excel",
        data=excel_buffer.getvalue(),
        file_name='ai_projects.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        key='download-excel'
    )

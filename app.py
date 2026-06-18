import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster, HeatMap, Draw, MousePosition, MiniMap, Fullscreen, MeasureControl
import pandas as pd

st.set_page_config(
    page_title="Інтерактивна карта Львова",
    page_icon="🗺️",
    layout="wide"
)

st.markdown("""
<style>
    .main > div { padding-top: 1rem; }
    .stSelectbox label { font-weight: 600; }
    h1 { color: #2c3e50; }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

st.title("🗺️ Інтерактивна карта Львова")
st.markdown("**Демонстрація можливостей Folium у Streamlit** | Бібліотека Folium + Фреймворк Streamlit")

# Дані
lviv_coords = [49.8397, 24.0297]

attractions = {
    "Площа Ринок": {"coords": [49.8420, 24.0316], "category": "Пам'ятка", "desc": "Центральна площа Львова, внесена до списку ЮНЕСКО. Архітектурний ансамбль XIV–XVIII ст.", "icon": "star", "color": "red"},
    "Оперний театр": {"coords": [49.8443, 24.0263], "category": "Культура", "desc": "Львівський національний академічний театр опери та балету імені Соломії Крушельницької (1900 р.)", "icon": "music", "color": "purple"},
    "Личаківський цвинтар": {"coords": [49.8290, 24.0620], "category": "Пам'ятка", "desc": "Один з найстаріших та найкрасивіших цвинтарів Європи (1786 р.), пам'ятка архітектури.", "icon": "info-sign", "color": "gray"},
    "Замок Високий": {"coords": [49.8480, 24.0420], "category": "Пам'ятка", "desc": "Залишки середньовічного замку на Замковій горі з панорамним видом на місто.", "icon": "home", "color": "orange"},
    "Парк Стрийський": {"coords": [49.8200, 24.0190], "category": "Природа", "desc": "Один з найстаріших парків Львова (1887 р.), пам'ятка садово-паркового мистецтва.", "icon": "tree-conifer", "color": "green"},
    "Собор Святого Юра": {"coords": [49.8393, 24.0188], "category": "Архітектура", "desc": "Катедральний собор УГКЦ, визначна пам'ятка українського бароко (1744–1770 рр.).", "icon": "tower", "color": "blue"},
    "Аптека-музей": {"coords": [49.8415, 24.0305], "category": "Музей", "desc": "Унікальна діюча аптека-музей, заснована в 1735 році — одна з найстаріших в Україні.", "icon": "plus-sign", "color": "darkblue"},
    "Ратуша": {"coords": [49.8418, 24.0313], "category": "Пам'ятка", "desc": "Символ Львова, вежа Ратуші висотою 65 м. Побудована у 1835 р.", "icon": "flag", "color": "darkred"},
    "Університет Франка": {"coords": [49.8424, 24.0258], "category": "Освіта", "desc": "Львівський національний університет імені Івана Франка, заснований у 1661 р.", "icon": "education", "color": "cadetblue"},
    "Площа Данила Галицького": {"coords": [49.8397, 24.0353], "category": "Площа", "desc": "Центральний транспортний вузол міста з пам'ятником Данилу Галицькому.", "icon": "map-marker", "color": "lightred"},
}

heatmap_points = [
    [49.8420, 24.0316, 0.9], [49.8443, 24.0263, 0.8], [49.8415, 24.0305, 0.7],
    [49.8418, 24.0313, 0.85], [49.8397, 24.0297, 0.6], [49.8424, 24.0258, 0.65],
    [49.8393, 24.0188, 0.5], [49.8480, 24.0420, 0.4], [49.8290, 24.0620, 0.5],
    [49.8200, 24.0190, 0.45], [49.8350, 24.0350, 0.55], [49.8370, 24.0280, 0.6],
    [49.8430, 24.0350, 0.7], [49.8410, 24.0290, 0.75], [49.8460, 24.0300, 0.5],
]

# --- Бічна панель ---
st.sidebar.header("⚙️ Налаштування карти")

# CartoDB Positron
map_tile = st.sidebar.selectbox(
    "Тип підкладки:",
    ["OpenStreetMap", "cartodbpositron", "cartodbdark_matter"],
    index=0
)

categories = list(set(v["category"] for v in attractions.values()))
selected_cats = st.sidebar.multiselect("Фільтр за категорією:", categories, default=categories)

st.sidebar.markdown("---")
st.sidebar.subheader("🔌 Шари карти")
show_cluster = st.sidebar.checkbox("Кластеризація маркерів", value=True)
show_heatmap = st.sidebar.checkbox("Теплова карта відвідуваності", value=False)
show_circle  = st.sidebar.checkbox("Зона центру (500 м)", value=True)
show_minimap = st.sidebar.checkbox("Міні-карта", value=True)

st.sidebar.markdown("---")
zoom_level = st.sidebar.slider("Початковий масштаб:", 11, 17, 14)

# --- Метрики ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("📍 Об'єктів на карті", len(attractions))
col2.metric("🏛️ Пам'яток архітектури", sum(1 for v in attractions.values() if v["category"] in ["Пам'ятка", "Архітектура"]))
col3.metric("🌿 Природних об'єктів", sum(1 for v in attractions.values() if v["category"] == "Природа"))
col4.metric("🎭 Культурних об'єктів", sum(1 for v in attractions.values() if v["category"] == "Культура"))

# Додано обов'язковий параметр attr для уникнення ValueError
m = folium.Map(
    location=lviv_coords,
    zoom_start=zoom_level,
    tiles=map_tile,
    attr="Map data &copy; OpenStreetMap contributors, CartoDB",
    prefer_canvas=True
)

# Центральний маркер
folium.Marker(
    lviv_coords,
    popup=folium.Popup("<b>Центр Львова</b><br>49.8397° N, 24.0297° E", max_width=200),
    tooltip="📌 Центр Львова",
    icon=folium.Icon(color="red", icon="map-marker", prefix="fa")
).add_to(m)

# Зона центру
if show_circle:
    folium.Circle(
        location=lviv_coords,
        radius=500,
        color="#3498db",
        fill=True,
        fill_color="#3498db",
        fill_opacity=0.1,
        popup="Зона 500 м від центру",
        tooltip="Радіус 500 м"
    ).add_to(m)

# Маркери атракцій
filtered = {k: v for k, v in attractions.items() if v["category"] in selected_cats}

if show_cluster:
    marker_layer = MarkerCluster(name="Атракції (кластер)").add_to(m)
else:
    marker_layer = folium.FeatureGroup(name="Атракції").add_to(m)

for name, data in filtered.items():
    popup_html = f"""
    <div style="font-family: Arial; min-width: 200px;">
        <h4 style="color: #2c3e50; margin: 0 0 8px 0;">{name}</h4>
        <span style="background: #3498db; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">
            {data['category']}
        </span>
        <p style="margin: 8px 0 0 0; font-size: 13px; color: #555;">{data['desc']}</p>
        <p style="margin: 6px 0 0 0; font-size: 11px; color: #999;">
            📍 {data['coords'][0]:.4f}°N, {data['coords'][1]:.4f}°E
        </p>
    </div>
    """
    folium.Marker(
        location=data["coords"],
        popup=folium.Popup(popup_html, max_width=260),
        tooltip=f"🏛️ {name}",
        icon=folium.Icon(color=data["color"], icon=data["icon"])
    ).add_to(marker_layer)

# Теплова карта
if show_heatmap:
    HeatMap(
        [[p[0], p[1], p[2]] for p in heatmap_points],
        name="Теплова карта",
        radius=25,
        blur=15,
        gradient={"0.2": "blue", "0.5": "lime", "0.8": "orange", "1.0": "red"}
    ).add_to(m)

# Плагіни
if show_minimap:
    MiniMap(toggle_display=True, tile_layer=map_tile, attr="MiniMap Attribution").add_to(m)

Fullscreen(position="topleft", title="Повноекранний режим", title_cancel="Вийти").add_to(m)
MeasureControl(position="bottomleft", primary_length_unit="meters", secondary_length_unit="kilometers").add_to(m)
Draw(export=True, position="topleft").add_to(m)
MousePosition(position="bottomright", separator=" | ", prefix="📍", lat_formatter="function(n){return L.Util.formatNum(n,5);}", lng_formatter="function(n){return L.Util.formatNum(n,5);}").add_to(m)
folium.LayerControl(collapsed=False).add_to(m)

# Відображення
map_data = st_folium(m, width="100%", height=620, returned_objects=["last_object_clicked"])

# Інформація про обраний об'єкт
if map_data and map_data.get("last_object_clicked"):
    clicked = map_data["last_object_clicked"]
    lat, lng = clicked.get("lat"), clicked.get("lng")
    if lat and lng:
        st.info(f"📍 Обраний об'єкт: широта **{lat:.5f}**, довгота **{lng:.5f}**")

# Легенда
st.markdown("---")
st.subheader("📖 Список об'єктів на карті")
df_data = [{"Назва": k, "Категорія": v["category"], "Широта": v["coords"][0], "Довгота": v["coords"][1], "Опис": v["desc"]} for k, v in attractions.items()]
df = pd.DataFrame(df_data)
st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("Дипломна робота | Аналіз засобів Streamlit та Folium для побудови інтерактивних карт")
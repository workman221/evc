import streamlit as st
import pydeck as pdk
import webbrowser
import pandas as pd

# Components
st.title("EV Charger Hotspots")
cl1, cl2, cl3, cl4 = st.columns([2, 2, 2, 1])
st_crit = cl1.selectbox("Criterium", options=["<= Less than", "= Equal to", ">= More than"], index=2)
st_number = cl2.number_input("Number of Charging Stations", min_value=0, value=1, step=1)
st_range = cl3.number_input("Distance (km)", min_value=0, value=0, step=1)
st_invert = cl4.checkbox("Invert", value=False)

# Selection Processing
plz_evc = pd.read_csv(f"plz_evc.csv", sep=',', header=0)
st_crit = st_crit.split(' ')[0]
if st_crit == "<=":
    plz_evc = plz_evc.drop(plz_evc[plz_evc.ev_count > st_number].index)
elif st_crit == "=":
    plz_evc = plz_evc.drop(plz_evc[plz_evc.ev_count != st_number].index)
else:
    plz_evc = plz_evc.drop(plz_evc[plz_evc.ev_count < st_number].index)
max_count = plz_evc['ev_count'].max()
plz_evc['show'] = plz_evc['ev_count']
if st_invert:
    plz_evc['show'] = max_count - plz_evc['show']

# Map thing
layer = pdk.Layer(
    "ColumnLayer",
    data=plz_evc,
    get_position=["long", "lat"],
    get_elevation='show',
    elevation_scale=5000,
    radius=3000,
    get_fill_color=["255", "255-show*10", "0", "140+show*10"],
    pickable=True,
    auto_highlight=True,
)
# Combined all of it and render a viewport
r = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    layers=[layer],
    initial_view_state=pdk.ViewState(
        longitude=10.4515, latitude=50.6657, zoom=5, min_zoom=3, max_zoom=20, pitch=40.5, bearing=-5.36
    ),
    tooltip={
        "html": "{name} ({plz})<br/>Known EV Chargers in Range: {ev_count}",
        "style": {"background": "black", "color": "white"}
    },
)
st.pydeck_chart(r)

# Do a web search
cl0, cl1, cl2, cl3= st.columns([3, 2, 2, 1])
st_plz = cl1.selectbox("PLZ", options=plz_evc['plz'].tolist())
st_search_dist = cl2.number_input("Search distance", min_value=0.0, value=5.0, step=0.5)
st_button = cl3.button("Search Online")
if st_button:
    plz_evc = plz_evc.drop(plz_evc[plz_evc.plz != st_plz].index)
    lat = plz_evc.iloc[0]['lat']
    long = plz_evc.iloc[0]['long']
    link = f"https://www.immobilienscout24.de/Suche/radius/wohnung-mieten?;;;;;&geocoordinates={lat};{long};{st_search_dist}&enteredFrom=result_list"
    webbrowser.open_new_tab(link)


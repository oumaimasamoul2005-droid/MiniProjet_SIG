import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.title("Application géospatiale Web")

regions = gpd.read_file("data/Regions_WGS84.shp")

provinces = gpd.read_file("data/Provinces_WGS84.shp")

communes = gpd.read_file("data/communes_WGS84.shp")
st.write(regions.crs)
st.write(provinces.crs)
st.write(communes.crs)


# Région imposée : Fès-Meknès

region_selectionnee = "Fès-Meknès"

st.write("Région choisie :", region_selectionnee)

# Récupérer le code de la région choisie

code_region = regions[
    regions["libelle_fr"] == region_selectionnee
]["code_reg"].values[0]

# Filtrer les provinces selon ce code

provinces_filtrees = provinces[
    provinces["code_reg"] == code_region
]

# Liste des provinces

liste_provinces = provinces_filtrees["libelle_fr"].unique()

# Menu des provinces

province_selectionnee = st.selectbox(
    "Choisir une province",
    liste_provinces
)

# Affichage

st.write("Province choisie :", province_selectionnee)



# =========================
# FILTRER LES COMMUNES SELON LA PROVINCE CHOISIE
# =========================

communes_filtrees = communes[
    communes["FIRST_prov"] == province_selectionnee
]

# =========================
# LISTE DES COMMUNES
# =========================

liste_communes = communes_filtrees["FIRST_com_"].unique()

# =========================
# MENU DES COMMUNES
# =========================

commune_selectionnee = st.selectbox(
    "Choisir une commune",
    liste_communes
)

# AFFICHAGE

st.write("Commune choisie :", commune_selectionnee)


# =========================
# CARTE INTERACTIVE
# =========================

# Filtrer la géométrie de la commune choisie

commune_geo = communes[
    communes["FIRST_com_"] == commune_selectionnee
]

# Créer la carte

m = folium.Map(
    location=[31.5, -7],
    zoom_start=6
)

# Ajouter le contour de la commune

folium.GeoJson(
    commune_geo,
    style_function=lambda x: {
        "color": "red",
        "weight": 3,
        "fillOpacity": 0
    }
).add_to(m)

# Centrer automatiquement la carte

bounds = commune_geo.total_bounds

m.fit_bounds([
    [bounds[1], bounds[0]],
    [bounds[3], bounds[2]]
])

# Ajouter le MNT (WMS)

folium.raster_layers.WmsTileLayer(
    url="https://ows.terrestris.de/osm/service?",
    layers="SRTM30-Colored",
    name="MNT",
    fmt="image/png",
    transparent=True,
    overlay=True,
    control=True
).add_to(m)

# Contrôle des couches

folium.LayerControl().add_to(m)

# Afficher la carte

st_folium(m, width=900, height=600)






# =========================
# DONNÉES CLIMATIQUES
# =========================

import requests

# Géométrie commune choisie

commune_geo = communes[
    communes["FIRST_com_"] == commune_selectionnee
]

# Centre géographique

centre = commune_geo.geometry.iloc[0].centroid
latitude = centre.y
longitude = centre.x

st.write("Latitude :", latitude)
st.write("Longitude :", longitude)

url = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={latitude}"
    f"&longitude={longitude}"
    "&daily=temperature_2m_max,precipitation_sum"
    "&timezone=auto"
)
st.write(url)
response = requests.get(url)

st.write(response.status_code)

# Données JSON

if response.status_code == 200:
    data = response.json()
else:
    st.error("Erreur API")
    st.stop()

# Affichage

st.subheader("Prévisions météorologiques")

st.write(data)

################################################################################
import plotly.express as px
import pandas as pd
# =========================
# VISUALISATION TEMPORELLE
# =========================

st.subheader("Visualisation temporelle")

# Récupérer les dates

dates = data["daily"]["time"]

# Récupérer températures

temperatures = data["daily"]["temperature_2m_max"]

# Récupérer précipitations

precipitations = data["daily"]["precipitation_sum"]

# Créer DataFrame

df_meteo = pd.DataFrame({
    "Date": dates,
    "Température": temperatures,
    "Précipitations": precipitations
})

# Sélecteur paramètre

parametre = st.radio(
    "Choisir le paramètre",
    ["Température", "Précipitations"]
)

# =========================
# GRAPHIQUE TEMPÉRATURE
# =========================

if parametre == "Température":

    fig = px.line(
        df_meteo,
        x="Date",
        y="Température",
        title=f"Température sur 15 jours - {commune_selectionnee}",
        markers=True
    )

    fig.update_layout(
        yaxis_title="Température (°C)",
        xaxis_title="Date"
    )

    st.plotly_chart(fig)

# =========================
# GRAPHIQUE PRÉCIPITATIONS
# =========================

else:

    fig = px.bar(
        df_meteo,
        x="Date",
        y="Précipitations",
        title=f"Précipitations sur 15 jours - {commune_selectionnee}"
    )

    fig.update_layout(
        yaxis_title="Précipitations (mm)",
        xaxis_title="Date"
    )

    st.plotly_chart(fig)
































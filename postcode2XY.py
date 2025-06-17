import streamlit as st
import requests

def postcode_to_coords(postcode):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": postcode + ", Netherlands",
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "TaxiPlanner/1.0"
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    if data:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return lat, lon
    else:
        return None

# Streamlit UI
st.title("Postcode naar Coördinaten")

postcode = st.text_input("Voer een Nederlandse postcode in", "2011AA")

if postcode:
    coords = postcode_to_coords(postcode)
    if coords:
        st.success(f"🗺️ Coördinaten voor {postcode}: {coords[0]:.5f}, {coords[1]:.5f}")
        st.map([{"lat": coords[0], "lon": coords[1]}])
    else:
        st.warning("Geen coördinaten gevonden voor deze postcode.")
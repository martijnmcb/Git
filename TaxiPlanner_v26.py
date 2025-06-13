
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

st.set_page_config(layout="wide")
st.title("🚖 Taxi Scenario Planner (v12 - dynamische blokgrootte)")

# 📌 Instelbare parameters
st.sidebar.header("🔧 Instellingen")

num_taxis = st.sidebar.slider("Aantal taxi's", 1, 30, 10)

short_passengers = st.sidebar.number_input("Aantal short-passagiers (10 min)", 0, 1000, 200, step=10)
medium_passengers = st.sidebar.number_input("Aantal medium-passagiers (20 min)", 0, 500, 50, step=5)
long_passengers = st.sidebar.number_input("Aantal long-passagiers (60 min)", 0, 500, 50, step=5)

ritdefinities = {
    "Short": {"aantal": short_passengers, "duur": 10},
    "Medium": {"aantal": medium_passengers, "duur": 20},
    "Long": {"aantal": long_passengers, "duur": 60},
}

# Genereer rittenlijst
ritten = []
for soort, gegevens in ritdefinities.items():
    totaal_minuten = gegevens["duur"] * 2  # heen en terug
    for _ in range(gegevens["aantal"] // 4):  # 4 passagiers per rit
        ritten.append((soort, totaal_minuten))

# Scenario's
scenario_order = {
    "Short first": sorted(ritten, key=lambda x: {"Short": 0, "Medium": 1, "Long": 2}[x[0]]),
    "Medium first": sorted(ritten, key=lambda x: {"Medium": 0, "Short": 1, "Long": 2}[x[0]]),
    "Long first": sorted(ritten, key=lambda x: {"Long": 0, "Medium": 1, "Short": 2}[x[0]]),
}

# Scenario selectie
scenario = st.selectbox("📋 Kies een scenario", list(scenario_order.keys()))

# Planritfunctie met minuten in plaats van blokken
def generate_scenario_df(ritvolgorde):
    beschikbaar_vanaf = {taxi: 0 for taxi in range(1, num_taxis + 1)}
    planning = []
    for rit_type, duur_minuten in ritvolgorde:
        taxi = min(beschikbaar_vanaf, key=beschikbaar_vanaf.get)
        start = beschikbaar_vanaf[taxi]
        end = start + duur_minuten
        beschikbaar_vanaf[taxi] = end
        planning.append({
            "Taxi": taxi,
            "Start": start,
            "End": end,
            "RitType": rit_type,
            "Duur": duur_minuten
        })
    return pd.DataFrame(planning)

# Gantt Chart functie (in echte minuten)

def plot_gantt(df):
    if df.empty:
        st.info("Geen ritten om weer te geven in het Gantt-schema.")
        return
    fig, ax = plt.subplots(figsize=(12, 5))
    kleuren = {"Short": "green", "Medium": "orange", "Long": "red"}
    for _, row in df.iterrows():
        ax.barh(
            y=row["Taxi"],
            width=row["End"] - row["Start"],
            left=row["Start"],
            color=kleuren.get(row["RitType"], "gray")
        )
    max_time = df["End"].max()
    for minute in range(0, int(max_time) + 10, 10):
        ax.axvline(minute, color="lightgray", linewidth=0.5, linestyle="--")
    ax.set_xlabel("Tijd (minuten)")
    ax.set_ylabel("Taxi")
    ax.set_title("Gantt-weergave van ritplanning (met 10-minuut raster)")
    st.pyplot(fig)

# Teken verticale lijnen voor blokgrenzen




# Genereer planning
df = generate_scenario_df(scenario_order[scenario])
if df.empty:
    st.warning("Er zijn geen ritten ingepland. Voeg passagiers toe om de planning te starten.")
    st.stop()
df = generate_scenario_df(scenario_order[scenario])

# Toon Gantt
st.subheader("🕘 Gantt-planning")
plot_gantt(df)

# Berekeningen
inzetduur = sum((row["End"] - row["Start"]) for _, row in df.iterrows())
schema_lengte = df["End"].max()

# Wachttijd per passagier
wachttijd_per_passagier = []
for _, row in df.iterrows():
    wachttijd = row["Start"]
    for _ in range(4):
        wachttijd_per_passagier.append(wachttijd)

gem_wachttijd = sum(wachttijd_per_passagier) / len(wachttijd_per_passagier) if wachttijd_per_passagier else 0

st.subheader("📊 Metrics voor huidig scenario")
st.metric("Totale inzetduur (min)", inzetduur)
st.metric("Schema lengte (min)", schema_lengte)
st.metric("Gemiddelde wachttijd (min)", round(gem_wachttijd, 1))

# Scenario vergelijking
vergelijking = []
for naam, volgorde in scenario_order.items():
    d = generate_scenario_df(volgorde)
    inzet = sum((r["End"] - r["Start"]) for _, r in d.iterrows())
    lengte = d["End"].max()
    wachttijden = [r["Start"] for _, r in d.iterrows() for _ in range(4)]
    gemiddelde = sum(wachttijden) / len(wachttijden) if wachttijden else 0
    vergelijking.append({
        "Scenario": naam,
        "Totale inzetduur (min)": inzet,
        "Schema lengte (min)": lengte,
        "Gem. wachttijd (min)": round(gemiddelde, 1)
    })
vergelijking_df = pd.DataFrame(vergelijking)

st.subheader("📈 Scenariovergelijking")
st.dataframe(vergelijking_df, use_container_width=True)
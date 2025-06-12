import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

st.set_page_config(page_title="Taxi Ritplanner", layout="wide")

st.title("🚖 Taxi Ritplanner – Scenario Simulatie")

# --- Invoerparameters ---
with st.sidebar:
    st.header("🔧 Instellingen")
    selected_scenario = st.selectbox("Kies ritvolgorde:", ["Short first", "Medium first", "Long first"])
    num_taxis = st.slider("Aantal taxi's:", 1, 20, 10)
    block_size = st.selectbox("Tijd per blok (min):", [10, 20, 30], index=1)

    st.subheader("📋 Aantal passagiers")
    short_pax = st.number_input("Korte rit (10 min)", 0, 500, 200)
    medium_pax = st.number_input("Middellange rit (20 min)", 0, 500, 50)
    long_pax = st.number_input("Lange rit (60 min)", 0, 500, 50)

# --- Ritdefinitie ---
ride_types = {
    "Short": {"duration": 10, "passengers": short_pax},
    "Medium": {"duration": 20, "passengers": medium_pax},
    "Long": {"duration": 60, "passengers": long_pax},
}

# --- Sorteervolgorde ---
scenario_order = {
    "Short first": ["Short", "Medium", "Long"],
    "Medium first": ["Medium", "Short", "Long"],
    "Long first": ["Long", "Medium", "Short"],
}

# --- Berekening ritten per scenario ---
def generate_planning(order):
    planning = []
    slots = 30
    taxi_slots = {taxi: 0 for taxi in range(1, num_taxis + 1)}  # herinitialiseer voor elk scenario

    for ride in order:
        pax = ride_types[ride]["passengers"]
        duration = ride_types[ride]["duration"]
        total_rides = -(-pax // 4)  # ceiling
        blocks_needed = (duration * 2) // block_size

        for _ in range(total_rides):
            for taxi in range(1, num_taxis + 1):
                start = taxi_slots[taxi]
                end = start + blocks_needed
                if end <= slots:
                    planning.append({
                        "Taxi": taxi,
                        "Start": start,
                        "End": end,
                        "Type": ride,
                        "Duration blocks": blocks_needed
                    })
                    taxi_slots[taxi] = end
                    break
    return pd.DataFrame(planning)

# --- Scenariovergelijkingstabel ---
st.subheader("📊 Scenariovergelijking")
comparison = []
for scenario_name, order in scenario_order.items():
    df = generate_planning(order)
    unique_blocks = set()
    for _, row in df.iterrows():
        unique_blocks.update(range(row.Start, row.End))
    total_minutes = len(unique_blocks) * block_size
    comparison.append({"Scenario": scenario_name, "Inzetduur (min)": total_minutes})

comparison_df = pd.DataFrame(comparison)
st.dataframe(comparison_df, use_container_width=True)

# --- Geselecteerd scenario tonen ---
st.subheader("📅 Gantt Planning – Scenario: {}".format(selected_scenario))
gantt_df = generate_planning(scenario_order[selected_scenario])

fig, ax = plt.subplots(figsize=(12, 6))
colors = {"Short": "lightgreen", "Medium": "gold", "Long": "salmon"}

for i, taxi in enumerate(sorted(gantt_df.Taxi.unique())):
    taxi_data = gantt_df[gantt_df.Taxi == taxi]
    for _, row in taxi_data.iterrows():
        ax.barh(y=taxi, left=row.Start, width=row.End - row.Start,
                color=colors[row.Type], edgecolor='black')

legend_elements = [Patch(facecolor=color, edgecolor='black', label=label) for label, color in colors.items()]
ax.legend(handles=legend_elements, title="Rittypes")
ax.set_xlabel("Tijdslot ({} min per slot)".format(block_size))
ax.set_ylabel("Taxi")
ax.set_yticks(range(1, num_taxis + 1))
ax.set_title("Taxi inzet per scenario")

st.pyplot(fig)

# --- Bezettingsgrafiek ---
st.subheader("📈 Bezetting per tijdslot")
slots = 30
occupancy = np.zeros(slots)
for _, row in gantt_df.iterrows():
    occupancy[row.Start:row.End] += 1

fig2, ax2 = plt.subplots()
ax2.plot(range(slots), occupancy, drawstyle='steps-post')
ax2.set_title("Aantal actieve taxi's per tijdslot")
ax2.set_xlabel("Tijdslot")
ax2.set_ylabel("Aantal taxi's")

st.pyplot(fig2)

# --- Totale inzetduur van geselecteerd scenario ---
st.subheader("🕒 Totale inzetduur voor geselecteerd scenario")
from collections import defaultdict

taxi_blocks = defaultdict(set)
for _, row in gantt_df.iterrows():
    taxi_blocks[row.Taxi].update(range(row.Start, row.End))
total_blocks = sum(len(blocks) for blocks in taxi_blocks.values())
total_minutes = total_blocks * block_size
st.metric("Totale beladen taxitijd (uniek)", f"{total_minutes} minuten")

# --- Downloadoptie ---
st.subheader("⬇️ Exporteer planning")
st.download_button("Download als CSV", gantt_df.to_csv(index=False), file_name="gantt_planning.csv")

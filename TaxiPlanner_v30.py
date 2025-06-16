import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Simuleer scenario
def generate_scenario_df(aantal_taxi=10, short=200, medium=50, long=50):
    planning = []
    taxi_slots = {taxi: 0 for taxi in range(1, aantal_taxi + 1)}
    ritten = [("Short", short, 10), ("Medium", medium, 20), ("Long", long, 60)]

    for rit_type, aantal, duur_minuten in ritten:
        for _ in range(aantal):
            taxi = min(taxi_slots, key=taxi_slots.get)
            start = taxi_slots[taxi]
            end = start + duur_minuten
            planning.append({
                "Taxi": taxi,
                "Start": start,
                "End": end,
                "RitType": rit_type,
                "Duur": duur_minuten,
                "WaitTime": start
            })
            taxi_slots[taxi] = end
    return pd.DataFrame(planning)

# Gantt plot
def plot_gantt(df):
    if df.empty:
        st.info("Geen ritten om weer te geven in het Gantt-schema.")
        return
    fig, ax = plt.subplots(figsize=(12, 5))
    kleuren = {"Short": "green", "Medium": "orange", "Long": "red"}
    for _, row in df.iterrows():
        ax.barh(y=row["Taxi"], width=row["End"] - row["Start"], left=row["Start"],
                color=kleuren.get(row["RitType"], "gray"))
    max_time = df["End"].max()
    for minute in range(0, int(max_time) + 10, 10):
        ax.axvline(minute, color="lightgray", linewidth=0.5, linestyle="--")
    ax.set_xlabel("Tijd (minuten)")
    ax.set_ylabel("Taxi")
    ax.set_title("Gantt-weergave van ritplanning (met 10-minuut raster)")
    st.pyplot(fig)

# Wachttijdgrafiek
def plot_wait_times(df):
    if df.empty or "WaitTime" not in df.columns:
        st.info("Geen wachttijdgegevens beschikbaar.")
        return
    avg_waits = df.groupby("RitType")["WaitTime"].mean().sort_index()
    fig, ax = plt.subplots()
    avg_waits.plot(kind="bar", ax=ax, color=["green", "orange", "red"])
    ax.set_title("Gemiddelde wachttijd per rittype")
    ax.set_ylabel("Wachttijd (minuten)")
    ax.set_xlabel("Rittype")
    st.pyplot(fig)

# Animatie
def animate_taxi_schedule(df, time_step=10):
    st.subheader("🎬 Tijdslijn animatie van ritplanning")
    if df.empty:
        st.info("Geen ritgegevens beschikbaar voor animatie.")
        return
    max_time = int(df["End"].max())
    t = st.slider("Tijd (minuten)", 0, max_time, 0, step=time_step)
    actief = df[(df["Start"] <= t) & (df["End"] > t)]
    fig, ax = plt.subplots(figsize=(10, 4))
    kleuren = {"Short": "green", "Medium": "orange", "Long": "red"}
    for _, row in actief.iterrows():
        ax.barh(row["Taxi"], row["End"] - row["Start"], left=row["Start"],
                color=kleuren.get(row["RitType"], "gray"))
    ax.axvline(t, color="blue", linestyle="--", label=f"Tijd: {t} min")
    ax.set_xlim(0, max_time + 10)
    ax.set_xlabel("Tijd (minuten)")
    ax.set_ylabel("Taxi")
    ax.set_title(f"Actieve ritten op tijdstip {t} min")
    st.pyplot(fig)

# Streamlit UI
st.title("🚕 Taxi Ritplanner")
aantal_taxi = st.slider("Aantal taxi's", 1, 30, 10)
short = st.slider("Aantal korte ritten (10 min)", 0, 300, 200)
medium = st.slider("Aantal middellange ritten (20 min)", 0, 150, 50)
long = st.slider("Aantal lange ritten (60 min)", 0, 150, 50)

df = generate_scenario_df(aantal_taxi, short, medium, long)

st.subheader("📈 Gantt-schema van alle ritten")
plot_gantt(df)

st.subheader("📊 Gemiddelde wachttijd per rittype")
plot_wait_times(df)

animate_taxi_schedule(df)
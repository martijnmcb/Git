import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Simuleer scenario
def generate_scenario_df(aantallen, duren, groepen, mix_mode=False):
    planning = []
    kleuren = {"Short": "green", "Medium": "orange", "Long": "red"}

    if mix_mode:
        # Alle taxi’s in één pool
        total_taxi = sum(groepen.values())
        taxi_slots = {taxi: 0 for taxi in range(1, total_taxi + 1)}
        # Sorteer ritten op willekeurige of vaste volgorde (eerste alle korte bijv.)
        ritten = []
        for rit_type in ["Short", "Medium", "Long"]:
            for _ in range(aantallen[rit_type]):
                ritten.append((rit_type, duren[rit_type]))
        for rit_type, duur in ritten:
            taxi = min(taxi_slots, key=taxi_slots.get)
            start = taxi_slots[taxi]
            end = start + duur
            planning.append({
                "Taxi": taxi,
                "Start": start,
                "End": end,
                "RitType": rit_type,
                "Duur": duur,
                "WaitTime": start,
                "Kleur": kleuren.get(rit_type, "gray")
            })
            taxi_slots[taxi] = end
    else:
        # Per groep (vaste categorieën)
        taxi_id = 1
        for rit_type in ["Short", "Medium", "Long"]:
            taxi_slots = {taxi_id + i: 0 for i in range(groepen[rit_type])}
            for _ in range(aantallen[rit_type]):
                taxi = min(taxi_slots, key=taxi_slots.get)
                start = taxi_slots[taxi]
                end = start + duren[rit_type]
                planning.append({
                    "Taxi": taxi,
                    "Start": start,
                    "End": end,
                    "RitType": rit_type,
                    "Duur": duren[rit_type],
                    "WaitTime": start,
                    "Kleur": kleuren.get(rit_type, "gray")
                })
                taxi_slots[taxi] = end
            taxi_id += groepen[rit_type]

    return pd.DataFrame(planning)

# Gantt plot
def plot_gantt(df):
    if df.empty:
        st.info("Geen ritten om weer te geven in het Gantt-schema.")
        return
    fig, ax = plt.subplots(figsize=(12, 5))
    for _, row in df.iterrows():
        ax.barh(y=row["Taxi"], width=row["End"] - row["Start"], left=row["Start"], color=row["Kleur"])
    max_time = df["End"].max()
    for minute in range(0, int(max_time) + 10, 10):
        ax.axvline(minute, color="lightgray", linewidth=0.5, linestyle="--")
    ax.set_xlabel("Tijd (minuten)")
    ax.set_ylabel("Taxi")
    ax.set_title("Gantt-weergave van ritplanning")
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
    for _, row in actief.iterrows():
        ax.barh(row["Taxi"], row["End"] - row["Start"], left=row["Start"], color=row["Kleur"])
    ax.axvline(t, color="blue", linestyle="--", label=f"Tijd: {t} min")
    ax.set_xlim(0, max_time + 10)
    ax.set_xlabel("Tijd (minuten)")
    ax.set_ylabel("Taxi")
    ax.set_title(f"Actieve ritten op tijdstip {t} min")
    st.pyplot(fig)

# Streamlit UI
st.title("🚕 Taxi Ritplanner – versie 34")

mix_mode = st.checkbox("↔️ Mix ritcategorieën tussen taxi’s (flexibele inzet)", value=False)

# Aantallen passagiers per type
short = st.slider("Aantal korte ritten", 0, 300, 200)
medium = st.slider("Aantal middellange ritten", 0, 150, 50)
long = st.slider("Aantal lange ritten", 0, 150, 50)
aantallen = {"Short": short, "Medium": medium, "Long": long}

# Duur per rittype
short_dur = st.slider("Duur korte rit (min)", 5, 30, 10)
medium_dur = st.slider("Duur middellange rit (min)", 15, 45, 20)
long_dur = st.slider("Duur lange rit (min)", 30, 120, 60)
duren = {"Short": short_dur, "Medium": medium_dur, "Long": long_dur}

# Taxi verdeling
if mix_mode:
    total_taxi = st.slider("Totaal aantal taxi's", 1, 40, 10)
    groepen = {"Short": total_taxi, "Medium": 0, "Long": 0}  # alles in 1 groep
else:
    st.markdown("### Verdeling taxi's over ritgroepen")
    taxi_short = st.slider("Aantal taxi's voor korte ritten", 0, 30, 4)
    taxi_medium = st.slider("Aantal taxi's voor middellange ritten", 0, 30, 3)
    taxi_long = st.slider("Aantal taxi's voor lange ritten", 0, 30, 3)
    groepen = {"Short": taxi_short, "Medium": taxi_medium, "Long": taxi_long}

df = generate_scenario_df(aantallen, duren, groepen, mix_mode=mix_mode)

st.subheader("📈 Gantt-schema")
plot_gantt(df)

st.subheader("📊 Gemiddelde wachttijd per rittype")
plot_wait_times(df)

animate_taxi_schedule(df)
from supabase import create_client
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

SUPABASE_URL = "https://jczbpentsmzkncakedkq.supabase.co"
SUPABASE_KEY = "sb_publishable_pncl2bBUaGXvdD0bz_vB1Q_O3NPsL8_"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Dynamo Fyzio Screening", layout="wide")

# ---------- FUNCTIONS ----------

def normalize(value, length):
    if length == 0:
        return 0
    return (value / length) * 100

def risk_score(ant, hq, addabd):

    score = 0

    if ant < 72:
        score += 30

    if hq < 0.6:
        score += 30

    if addabd < 0.8:
        score += 30

    return score

# ---------- HEADER ----------

col1,col2 = st.columns([1,6])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)

with col2:
    st.title("Dynamo Fyzio Screening")
    st.caption("SK Dynamo České Budějovice – Akademie")

tab1, tab2, tab3 = st.tabs(["Nové měření","Historie hráče","Dashboard"])

# ---------- TAB 1 ----------

with tab1:

    st.header("Nové měření")

    category = st.selectbox("Kategorie",["U15","U16","U17","U18","U19","A tým"])
    player = st.text_input("Jméno hráče")

    col1,col2 = st.columns(2)

    with col1:
        height = st.number_input("Výška (cm)", value=180)

    with col2:
        weight = st.number_input("Váha (kg)", value=75)

    st.subheader("Délka dolní končetiny")

    col1,col2 = st.columns(2)

    with col1:
        leg_r = st.number_input("Pravá DK (cm)", value=90.0)

    with col2:
        leg_l = st.number_input("Levá DK (cm)", value=90.0)

    st.subheader("Y Balance")

    col1,col2 = st.columns(2)

    with col1:
        ant_r = st.number_input("ANT pravá")
        pm_r = st.number_input("PM pravá")
        pl_r = st.number_input("PL pravá")

    with col2:
        ant_l = st.number_input("ANT levá")
        pm_l = st.number_input("PM levá")
        pl_l = st.number_input("PL levá")

    st.subheader("Síla")

    col1,col2 = st.columns(2)

    with col1:
        ham_r = st.number_input("Hamstring pravá")
        quad_r = st.number_input("Quadriceps pravá")
        add_r = st.number_input("Adduktor pravá")
        abd_r = st.number_input("Abduktor pravá")

    with col2:
        ham_l = st.number_input("Hamstring levá")
        quad_l = st.number_input("Quadriceps levá")
        add_l = st.number_input("Adduktor levá")
        abd_l = st.number_input("Abduktor levá")

    if st.button("Vyhodnotit a uložit"):

        ant_norm = normalize(ant_r, leg_r)

        hq = ham_r/quad_r if quad_r>0 else 0
        addabd = add_r/abd_r if abd_r>0 else 0

        risk = risk_score(ant_norm, hq, addabd)

        recommendation = ""

        if ant_norm < 72:
            recommendation += "Sagittální deficit – ankle mobility, split squat, step-down.\n"

        if hq < 0.6:
            recommendation += "Nízké H:Q ratio – Nordic hamstring, excentrický RDL.\n"

        if addabd < 0.8:
            recommendation += "Nízká síla adduktorů – Copenhagen plank.\n"

        # -------- RESULT --------

        st.subheader("Vyhodnocení")

        if risk < 20:
            st.success("🟢 Nízké riziko")

        elif risk < 50:
            st.warning("🟠 Střední riziko")

        else:
            st.error("🔴 Vysoké riziko")

        st.metric("Risk score", risk)

        st.subheader("Doporučení")

        if recommendation == "":
            st.success("Bez výrazných deficitů")

        else:
            st.write(recommendation)

        data = {

            "player": player,
            "category": category,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "height": height,
            "weight": weight,

            "ant_r": ant_r,
            "ant_l": ant_l,
            "pm_r": pm_r,
            "pm_l": pm_l,
            "pl_r": pl_r,
            "pl_l": pl_l,

            "ham_r": ham_r,
            "ham_l": ham_l,
            "quad_r": quad_r,
            "quad_l": quad_l,
            "add_r": add_r,
            "add_l": add_l,
            "abd_r": abd_r,
            "abd_l": abd_l,

            "recommendation": recommendation,
            "risk": risk
        }

        supabase.table("tests").insert(data).execute()

        st.success("Test uložen")

# ---------- TAB 2 ----------

with tab2:

    st.header("Historie hráče")

    response = supabase.table("tests").select("*").execute()

    df = pd.DataFrame(response.data)

    if len(df)==0:

        st.info("Zatím žádná data")

    else:

        player_select = st.selectbox("Vyber hráče", df["player"].unique())

        player_df = df[df["player"] == player_select]

        st.dataframe(player_df)

        fig = plt.figure()

        plt.plot(player_df["date"], player_df["ham_r"], label="Hamstring R")
        plt.plot(player_df["date"], player_df["ham_l"], label="Hamstring L")

        plt.legend()

        st.pyplot(fig)

# ---------- TAB 3 ----------

with tab3:

    st.header("Dashboard týmu")

    response = supabase.table("tests").select("*").execute()

    df = pd.DataFrame(response.data)

    if len(df)==0:

        st.info("Zatím žádná data")

    else:

        st.metric("Počet testů", len(df))

        st.write("Průměr hamstring R:", round(df["ham_r"].mean(),2))
        st.write("Průměr hamstring L:", round(df["ham_l"].mean(),2))

        risk_players = df[df["risk"] > 40]

        st.subheader("Rizikoví hráči")

        st.dataframe(risk_players[["player","risk","recommendation"]])

from supabase import create_client
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

SUPABASE_URL = "https://jczbpentsmzkncakedkq.supabase.co"
SUPABASE_KEY = "sb_publishable_pncl2bBUaGXvdD0bz_vB1Q_O3NPsL8_"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Dynamo Fyzio Screening", layout="wide")

# ---------- FUNCTIONS ----------

def normalize(value,length):
    if length == 0:
        return 0
    return (value/length)*100

def risk_score(ant,hq,addabd):

    score = 0

    if ant < 72:
        score += 30

    if hq < 0.6:
        score += 30

    if addabd < 0.8:
        score += 30

    return score

def color(value,limit):

    if value < limit:
        return "🔴"

    if value < limit+5:
        return "🟠"

    return "🟢"


# ---------- HEADER ----------

col1,col2 = st.columns([1,6])

with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png",width=120)

with col2:
    st.title("Dynamo Fyzio Screening")
    st.caption("SK Dynamo České Budějovice – Akademie")


tab1,tab2,tab3,tab4 = st.tabs(["Dashboard","Nové měření","Historie hráčů","Karta hráče"])


# ---------- DASHBOARD ----------

with tab1:

    st.header("Team Risk Dashboard")

    response = supabase.table("tests").select("*").execute()
    df = pd.DataFrame(response.data)

    if len(df)==0:

        st.info("Zatím žádná data")

    else:

        latest = df.sort_values("date").groupby("player").tail(1)

        st.metric("Počet hráčů",len(latest))

        risk_players = latest[latest["risk"]>40]

        st.subheader("Rizikoví hráči")

        st.dataframe(risk_players[["player","category","risk","recommendation"]])


# ---------- NEW TEST ----------

with tab2:

    st.header("Nové měření")

    category = st.selectbox("Kategorie",["U16","U17","U18","U19"])

    player = st.text_input("Jméno hráče")

    col1,col2 = st.columns(2)

    with col1:
        height = st.number_input("Výška",value=180)

    with col2:
        weight = st.number_input("Váha",value=75)

    st.subheader("Délka končetiny")

    col1,col2 = st.columns(2)

    with col1:
        leg_r = st.number_input("Pravá DK",value=90.0)

    with col2:
        leg_l = st.number_input("Levá DK",value=90.0)

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

        ant_norm = normalize(ant_r,leg_r)

        hq = ham_r/quad_r if quad_r>0 else 0
        addabd = add_r/abd_r if abd_r>0 else 0

        risk = risk_score(ant_norm,hq,addabd)

        recommendation = ""

        if ant_norm < 72:
            recommendation += "Sagittální deficit – ankle mobility, split squat\n"

        if hq < 0.6:
            recommendation += "Nízké H:Q – Nordic hamstring\n"

        if addabd < 0.8:
            recommendation += "Slabé adduktory – Copenhagen plank\n"

        st.subheader("Vyhodnocení")

        st.write("ANT:",round(ant_norm,1),color(ant_norm,72))

        st.write("H:Q:",round(hq,2),color(hq,0.6))

        st.write("Add/Abd:",round(addabd,2),color(addabd,0.8))

        st.metric("Risk score",risk)

        st.subheader("Doporučení")

        if recommendation=="":
            st.success("Bez výrazných deficitů")

        else:
            st.write(recommendation)

        data = {

            "player":player,
            "category":category,
            "date":datetime.now().strftime("%Y-%m-%d"),

            "height":height,
            "weight":weight,

            "ant_r":ant_r,
            "ant_l":ant_l,
            "pm_r":pm_r,
            "pm_l":pm_l,
            "pl_r":pl_r,
            "pl_l":pl_l,

            "ham_r":ham_r,
            "ham_l":ham_l,
            "quad_r":quad_r,
            "quad_l":quad_l,

            "add_r":add_r,
            "add_l":add_l,
            "abd_r":abd_r,
            "abd_l":abd_l,

            "risk":risk,
            "recommendation":recommendation

        }

        supabase.table("tests").insert(data).execute()

        st.success("Test uložen")


# ---------- HISTORY ----------

with tab3:

    st.header("Historie podle kategorií")

    response = supabase.table("tests").select("*").execute()
    df = pd.DataFrame(response.data)

    if len(df)==0:

        st.info("Žádná data")

    else:

        for cat in ["U16","U17","U18","U19"]:

            st.subheader(cat)

            cat_df = df[df["category"]==cat]

            if len(cat_df)==0:

                st.write("Žádná data")

                continue

            st.dataframe(cat_df)


# ---------- PLAYER CARD ----------

with tab4:

    st.header("Karta hráče")

    response = supabase.table("tests").select("*").execute()
    df = pd.DataFrame(response.data)

    if len(df)==0:

        st.info("Žádná data")

    else:

        player_select = st.selectbox("Vyber hráče",df["player"].unique())

        player_df = df[df["player"]==player_select]

        st.dataframe(player_df)

        st.subheader("Graf vývoje síly")

        fig = plt.figure()

        plt.plot(player_df["date"],player_df["ham_r"],label="Hamstring R")
        plt.plot(player_df["date"],player_df["ham_l"],label="Hamstring L")

        plt.legend()

        st.pyplot(fig)

        st.subheader("Radar graf Y Balance")

        latest = player_df.iloc[-1]

        values = [

            latest["ant_r"],
            latest["pm_r"],
            latest["pl_r"]

        ]

        labels = ["ANT","PM","PL"]

        angles = np.linspace(0,2*np.pi,len(labels),endpoint=False)

        values = np.concatenate((values,[values[0]]))
        angles = np.concatenate((angles,[angles[0]]))

        fig = plt.figure()
        ax = fig.add_subplot(111,polar=True)

        ax.plot(angles,values)
        ax.fill(angles,values,alpha=0.25)

        ax.set_thetagrids(angles[:-1]*180/np.pi,labels)

        st.pyplot(fig)

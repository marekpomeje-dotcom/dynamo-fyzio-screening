
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dynamo Fyzio Screening", layout="wide")

DATA_FILE = "data.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=[
        "Date","Category","Player","Height","Weight",
        "Leg_R","Leg_L",
        "ANT_R","ANT_L","PM_R","PM_L","PL_R","PL_L",
        "Ham_R","Ham_L","Quad_R","Quad_L",
        "Add_R","Add_L","Abd_R","Abd_L"
    ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def normalize(v,l):
    if l == 0:
        return 0
    return (v/l)*100

def asym(a,b):
    if max(a,b)==0:
        return 0
    return abs(a-b)/max(a,b)*100

col1,col2 = st.columns([1,6])
with col1:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
with col2:
    st.title("Dynamo Fyzio Screening")
    st.caption("SK Dynamo České Budějovice – Akademie")

tab1, tab2, tab3, tab4 = st.tabs(["Nové měření","Databáze hráčů","Historie hráče","Přehled týmu"])

with tab1:
    st.header("Zadání nového testu")

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

    st.subheader("Síla (Tindeq)")
    col1,col2 = st.columns(2)

    with col1:
        ham_r = st.number_input("Hamstring pravá (N/kg)")
        quad_r = st.number_input("Quadriceps pravá (N/kg)")
        add_r = st.number_input("Adduktor pravá (N/kg)")
        abd_r = st.number_input("Abduktor pravá (N/kg)")

    with col2:
        ham_l = st.number_input("Hamstring levá (N/kg)")
        quad_l = st.number_input("Quadriceps levá (N/kg)")
        add_l = st.number_input("Adduktor levá (N/kg)")
        abd_l = st.number_input("Abduktor levá (N/kg)")

    if st.button("Vyhodnotit a uložit"):
        ant_r_n = normalize(ant_r,leg_r)
        ant_l_n = normalize(ant_l,leg_l)

        comp_r = (ant_r+pm_r+pl_r)/(3*leg_r)*100 if leg_r>0 else 0
        comp_l = (ant_l+pm_l+pl_l)/(3*leg_l)*100 if leg_l>0 else 0

        hq_r = ham_r/quad_r if quad_r>0 else 0
        hq_l = ham_l/quad_l if quad_l>0 else 0

        addabd_r = add_r/abd_r if abd_r>0 else 0
        addabd_l = add_l/abd_l if abd_l>0 else 0

        st.subheader("Výsledky")
        st.write("ANT pravá:", round(ant_r_n,1))
        st.write("ANT levá:", round(ant_l_n,1))
        st.write("Kompozit pravá:", round(comp_r,1))
        st.write("Kompozit levá:", round(comp_l,1))

        st.subheader("Poměry síly")
        st.write("H:Q pravá:", round(hq_r,2))
        st.write("H:Q levá:", round(hq_l,2))
        st.write("Add/Abd pravá:", round(addabd_r,2))
        st.write("Add/Abd levá:", round(addabd_l,2))

        st.subheader("Asymetrie")
        st.write("Hamstring asymetrie %:", round(asym(ham_r,ham_l),1))
        st.write("Quadriceps asymetrie %:", round(asym(quad_r,quad_l),1))
        st.write("Adduktor asymetrie %:", round(asym(add_r,add_l),1))

        st.subheader("Automatické doporučení")
        if ant_r_n < 72 or ant_l_n < 72:
            st.warning("Deficit sagittální roviny – doporučeno: ankle mobility, split squat, step-down")
        if hq_r < 0.6 or hq_l < 0.6:
            st.warning("Nízké H:Q ratio – doporučeno: Nordic hamstring, excentrický RDL")
        if addabd_r < 0.8 or addabd_l < 0.8:
            st.warning("Nízký poměr adduktor/abduktor – doporučeno: Copenhagen plank")

        df = load_data()
        df.loc[len(df)] = [
            datetime.now().strftime("%Y-%m-%d"),
            category,player,height,weight,
            leg_r,leg_l,
            ant_r,ant_l,pm_r,pm_l,pl_r,pl_l,
            ham_r,ham_l,quad_r,quad_l,
            add_r,add_l,abd_r,abd_l
        ]
        save_data(df)
        st.success("Test uložen")

with tab2:
    st.header("Databáze hráčů")
    df = load_data()
    if len(df)==0:
        st.info("Zatím žádná data")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button("Stáhnout CSV", df.to_csv(index=False), file_name="dynamo_screening.csv")

with tab3:
    st.header("Historie hráče")
    df = load_data()
    if len(df)==0:
        st.info("Zatím žádná data")
    else:
        player = st.selectbox("Vyber hráče", sorted(df["Player"].unique().tolist()))
        p = df[df["Player"]==player]
        st.dataframe(p)
        if len(p)>1:
            fig, ax = plt.subplots()
            ax.plot(p["Date"], p["Ham_R"], label="Hamstring pravá")
            ax.plot(p["Date"], p["Ham_L"], label="Hamstring levá")
            ax.legend()
            st.pyplot(fig)

with tab4:
    st.header("Přehled týmu")
    df = load_data()
    if len(df)==0:
        st.info("Zatím žádná data")
    else:
        st.metric("Počet testů", len(df))
        st.write("Průměr hamstring pravá:", round(df["Ham_R"].mean(),2))
        st.write("Průměr hamstring levá:", round(df["Ham_L"].mean(),2))

from supabase import create_client
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

SUPABASE_URL = "https://jczbpentsmzkncakedkq.supabase.co"
SUPABASE_KEY = "sb_publishable_pncl2bBUaGXvdD0bz_vB1Q_O3NPsL8_"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Dynamo Fyzio Screening", layout="wide")

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

tab1, tab2 = st.tabs(["Nové měření","Historie hráčů"])

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

        recommendation = ""

        if ant_r_n < 72 or ant_l_n < 72:
            st.warning("Deficit sagittální roviny – ankle mobility, split squat, step-down")
            recommendation += "Sagittální deficit – ankle mobility, split squat, step-down. "

        if hq_r < 0.6 or hq_l < 0.6:
            st.warning("Nízké H:Q ratio – Nordic hamstring, excentrický RDL")
            recommendation += "Nízké H:Q – Nordic hamstring, excentrický RDL. "

        if addabd_r < 0.8 or addabd_l < 0.8:
            st.warning("Nízký poměr adduktor/abduktor – Copenhagen plank")
            recommendation += "Slabé adduktory – Copenhagen plank. "

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
            "recommendation": recommendation
        }

        supabase.table("tests").insert(data).execute()

        st.success("Test uložen do databáze")

with tab2:

    st.header("Historie hráčů")

    response = supabase.table("tests").select("*").execute()

    df = pd.DataFrame(response.data)

    if len(df)==0:
        st.info("Zatím žádná data")

    else:
        st.dataframe(df)

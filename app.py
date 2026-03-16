import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_FILE = "data.csv"

# -----------------------------
# LOAD DATA
# -----------------------------

def load_data():

    if os.path.exists(DATA_FILE):

        return pd.read_csv(DATA_FILE)

    else:

        return pd.DataFrame(columns=[
            "date","category","player",
            "ant_r","ant_l","pm_r","pm_l","pl_r","pl_l",
            "ham_r","ham_l","quad_r","quad_l",
            "add_r","add_l","abd_r","abd_l"
        ])

# -----------------------------
# SAVE DATA
# -----------------------------

def save_data(df):

    df.to_csv(DATA_FILE,index=False)

df = load_data()

# -----------------------------
# PAGE
# -----------------------------

st.set_page_config(page_title="Dynamo Fyzio Screening",layout="wide")

st.title("Dynamo Fyzio Screening")
st.caption("SK Dynamo České Budějovice – Akademie")

# -----------------------------
# CATEGORY
# -----------------------------

category = st.selectbox(
    "Kategorie",
    ["U16","U17","U18","U19"]
)

df_cat = df[df["category"]==category]

# -----------------------------
# CALCULATIONS
# -----------------------------

def evaluate(row):

    hq_r = row["ham_r"]/row["quad_r"] if row["quad_r"]>0 else 0
    hq_l = row["ham_l"]/row["quad_l"] if row["quad_l"]>0 else 0

    addabd_r = row["add_r"]/row["abd_r"] if row["abd_r"]>0 else 0
    addabd_l = row["add_l"]/row["abd_l"] if row["abd_l"]>0 else 0

    risk="LOW"
    deficit=""
    injury=""
    solution=""

    if hq_r < 0.6 or hq_l < 0.6:

        risk="HIGH"
        deficit="Hamstring strength"
        injury="Hamstring strain"
        solution="Nordic hamstring, RDL"

    elif addabd_r < 0.8 or addabd_l < 0.8:

        risk="MEDIUM"
        deficit="Groin strength"
        injury="Adductor injury"
        solution="Copenhagen plank"

    elif row["ant_r"] < 70 or row["ant_l"] < 70:

        risk="MEDIUM"
        deficit="Sagittal control"
        injury="Knee injury risk"
        solution="Split squat, step-down"

    return pd.Series([risk,deficit,injury,solution])

if len(df_cat)>0:

    df_cat[["risk","deficit","injury","solution"]] = df_cat.apply(evaluate,axis=1)

# -----------------------------
# TABS
# -----------------------------

tab1,tab2,tab3,tab4 = st.tabs([
"Dashboard",
"Karta hráče",
"Nové měření",
"Správa dat"
])

# -----------------------------
# DASHBOARD
# -----------------------------

with tab1:

    st.header("Rizikoví hráči")

    if len(df_cat)==0:

        st.info("Žádná data")

    else:

        latest = df_cat.sort_values("date").groupby("player").tail(1)

        risk_players = latest[latest["risk"]!="LOW"]

        st.dataframe(risk_players[[
            "player","risk","deficit","injury","solution"
        ]])

# -----------------------------
# PLAYER CARD
# -----------------------------

with tab2:

    st.header("Karta hráče")

    if len(df_cat)==0:

        st.info("Žádná data")

    else:

        players = sorted(df_cat["player"].unique())

        player = st.selectbox("Vyber hráče",players)

        pdata = df_cat[df_cat["player"]==player]

        st.dataframe(pdata)

# -----------------------------
# NEW TEST
# -----------------------------

with tab3:

    st.header("Nové měření")

    player = st.text_input("Jméno hráče")

    col1,col2 = st.columns(2)

    with col1:

        ant_r = st.number_input("ANT pravá")
        pm_r = st.number_input("PM pravá")
        pl_r = st.number_input("PL pravá")

    with col2:

        ant_l = st.number_input("ANT levá")
        pm_l = st.number_input("PM levá")
        pl_l = st.number_input("PL levá")

    col3,col4 = st.columns(2)

    with col3:

        ham_r = st.number_input("Hamstring pravá")
        quad_r = st.number_input("Quadriceps pravá")
        add_r = st.number_input("Adduktor pravá")
        abd_r = st.number_input("Abduktor pravá")

    with col4:

        ham_l = st.number_input("Hamstring levá")
        quad_l = st.number_input("Quadriceps levá")
        add_l = st.number_input("Adduktor levá")
        abd_l = st.number_input("Abduktor levá")

    if st.button("Uložit test"):

        new_row = pd.DataFrame([{

            "date":datetime.now().strftime("%Y-%m-%d"),
            "category":category,
            "player":player,

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
            "abd_l":abd_l

        }])

        df_new = pd.concat([df,new_row],ignore_index=True)

        save_data(df_new)

        st.success("Test uložen")

# -----------------------------
# DATA MANAGEMENT
# -----------------------------

with tab4:

    st.header("Správa dat")

    if len(df)==0:

        st.info("Žádná data")

    else:

        st.dataframe(df)

        if st.button("Export CSV"):

            st.download_button(
                "Stáhnout data",
                df.to_csv(index=False),
                "dynamo_screening.csv"
            )

import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_FILE = "data.csv"

# -------------------------
# LOAD DATA
# -------------------------

def load_data():

    if os.path.exists(DATA_FILE):

        df = pd.read_csv(DATA_FILE)

        return df

    else:

        return pd.DataFrame(columns=[
            "date","category","player",
            "ant_r","ant_l","pm_r","pm_l","pl_r","pl_l",
            "ham_r","ham_l","quad_r","quad_l",
            "add_r","add_l","abd_r","abd_l"
        ])


def save_data(df):

    df.to_csv(DATA_FILE,index=False)


df = load_data()

# -------------------------
# PAGE
# -------------------------

st.set_page_config(page_title="Dynamo Fyzio Screening",layout="wide")

st.title("Dynamo Fyzio Screening")
st.caption("SK Dynamo České Budějovice – Akademie")

# -------------------------
# CATEGORY
# -------------------------

category = st.selectbox("Kategorie",["U16","U17","U18","U19"])

df_cat = df[df["category"]==category].copy()

# -------------------------
# CALCULATIONS
# -------------------------

def evaluate(row):

    hq_r = row["ham_r"]/row["quad_r"] if row["quad_r"]>0 else 0
    hq_l = row["ham_l"]/row["quad_l"] if row["quad_l"]>0 else 0

    addabd_r = row["add_r"]/row["abd_r"] if row["abd_r"]>0 else 0
    addabd_l = row["add_l"]/row["abd_l"] if row["abd_l"]>0 else 0

    ham_asym = abs(row["ham_r"]-row["ham_l"]) / max(row["ham_r"],row["ham_l"]) *100
    quad_asym = abs(row["quad_r"]-row["quad_l"]) / max(row["quad_r"],row["quad_l"]) *100
    add_asym = abs(row["add_r"]-row["add_l"]) / max(row["add_r"],row["add_l"]) *100

    risk="LOW"
    deficit=""
    structure=""
    solution=""

    if hq_r < 0.6 or hq_l < 0.6:

        risk="HIGH"
        deficit="Hamstring strength"
        structure="Hamstring complex"
        solution="Nordic hamstring, Romanian deadlift"

    elif addabd_r < 0.8 or addabd_l < 0.8:

        risk="MEDIUM"
        deficit="Groin strength"
        structure="Adductor group"
        solution="Copenhagen plank"

    elif row["ant_r"] < 70 or row["ant_l"] < 70:

        risk="MEDIUM"
        deficit="Sagittal stability"
        structure="ACL / Knee"
        solution="Split squat, step-down"

    return pd.Series([
        hq_r,hq_l,
        addabd_r,addabd_l,
        ham_asym,quad_asym,add_asym,
        risk,deficit,structure,solution
    ])

if len(df_cat)>0:

    df_cat[[
        "hq_r","hq_l",
        "addabd_r","addabd_l",
        "ham_asym","quad_asym","add_asym",
        "risk","deficit","structure","solution"
    ]] = df_cat.apply(evaluate,axis=1)

# -------------------------
# TABS
# -------------------------

tab1,tab2,tab3,tab4 = st.tabs([
"Dashboard",
"Karta hráče",
"Nové měření",
"Správa dat"
])

# -------------------------
# DASHBOARD
# -------------------------

with tab1:

    st.header("Rizikoví hráči")

    if len(df_cat)==0:

        st.info("Žádná data")

    else:

        latest = df_cat.sort_values("date").groupby("player").tail(1)

        risk_players = latest[latest["risk"]!="LOW"]

        st.dataframe(
            risk_players[[
                "player",
                "risk",
                "deficit",
                "structure",
                "solution"
            ]],
            use_container_width=True
        )

# -------------------------
# PLAYER CARD
# -------------------------

with tab2:

    st.header("Karta hráče")

    if len(df_cat)==0:

        st.info("Žádná data")

    else:

        players = sorted(df_cat["player"].unique())

        player = st.selectbox("Vyber hráče",players)

        pdata = df_cat[df_cat["player"]==player]

        st.dataframe(
            pdata[[
                "date",
                "hq_r","hq_l",
                "addabd_r","addabd_l",
                "ham_asym","quad_asym","add_asym",
                "risk","deficit","structure","solution"
            ]],
            use_container_width=True
        )

# -------------------------
# NEW TEST
# -------------------------

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

# -------------------------
# DATA MANAGEMENT
# -------------------------

with tab4:

    st.header("Správa dat")

    if len(df)==0:

        st.info("Žádná data")

    else:

        st.dataframe(df,use_container_width=True)

        st.download_button(
            "Export CSV",
            df.to_csv(index=False),
            "dynamo_screening_export.csv"
        )

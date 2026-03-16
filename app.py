from supabase import create_client
import streamlit as st
import pandas as pd
from datetime import datetime

SUPABASE_URL = "https://jczbpentsmzkncakedkq.supabase.co"
SUPABASE_KEY = "sb_publishable_pncl2bBUaGXvdD0bz_vB1Q_O3NPsL8_"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Dynamo Fyzio Screening", layout="wide")

# ---------------- FUNCTIONS ----------------

def normalize(value,length):
    if length == 0:
        return 0
    return (value/length)*100

def asym(r,l):
    if max(r,l)==0:
        return 0
    return abs(r-l)/max(r,l)*100

def diagnose(ant,hq,addabd,ham_asym,quad_asym):

    deficit = "None"
    injury = "-"
    solution = "-"
    risk = 0

    if ant < 72:
        deficit = "Sagittal control"
        injury = "ACL risk"
        solution = "ankle mobility + split squat"
        risk += 30

    if hq < 0.6:
        deficit = "Hamstring strength"
        injury = "Hamstring strain"
        solution = "Nordic hamstring"
        risk += 30

    if addabd < 0.8:
        deficit = "Adductor strength"
        injury = "Groin injury"
        solution = "Copenhagen plank"
        risk += 30

    if ham_asym > 10:
        deficit = "Hamstring asymmetry"
        injury = "Hamstring strain"
        solution = "single leg hamstring work"
        risk += 20

    if quad_asym > 10:
        deficit = "Quadriceps asymmetry"
        injury = "Knee injury"
        solution = "single leg squat"
        risk += 20

    return deficit,injury,solution,risk


# ---------------- HEADER ----------------

st.title("Dynamo Fyzio Screening")
st.caption("SK Dynamo České Budějovice – Akademie")

tabs = st.tabs(["Dashboard","Nové měření","Karta hráčů","Team summary"])

# ---------------- DASHBOARD ----------------

with tabs[0]:

    st.header("Risk Dashboard")

    response = supabase.table("tests").select("*").execute()
    df = pd.DataFrame(response.data)

    if len(df)==0:

        st.info("Zatím žádná data")

    else:

        latest = df.sort_values("date").groupby("player").tail(1)

        st.dataframe(
            latest[[
                "player",
                "category",
                "risk",
                "deficit",
                "injury",
                "solution"
            ]]
        )

# ---------------- NEW TEST ----------------

with tabs[1]:

    st.header("Nové měření")

    category = st.selectbox("Kategorie",["U16","U17","U18","U19"])

    player = st.text_input("Jméno hráče")

    leg_r = st.number_input("Délka pravé DK",value=90.0)
    leg_l = st.number_input("Délka levé DK",value=90.0)

    st.subheader("Y Balance")

    ant_r = st.number_input("ANT pravá")
    ant_l = st.number_input("ANT levá")

    pm_r = st.number_input("PM pravá")
    pm_l = st.number_input("PM levá")

    pl_r = st.number_input("PL pravá")
    pl_l = st.number_input("PL levá")

    st.subheader("Síla")

    ham_r = st.number_input("Hamstring pravá")
    ham_l = st.number_input("Hamstring levá")

    quad_r = st.number_input("Quadriceps pravá")
    quad_l = st.number_input("Quadriceps levá")

    add_r = st.number_input("Adduktor pravá")
    add_l = st.number_input("Adduktor levá")

    abd_r = st.number_input("Abduktor pravá")
    abd_l = st.number_input("Abduktor levá")

    if st.button("Vyhodnotit"):

        ant_norm = normalize(ant_r,leg_r)

        hq = ham_r/quad_r if quad_r>0 else 0
        addabd = add_r/abd_r if abd_r>0 else 0

        ham_asym = asym(ham_r,ham_l)
        quad_asym = asym(quad_r,quad_l)

        deficit,injury,solution,risk = diagnose(
            ant_norm,
            hq,
            addabd,
            ham_asym,
            quad_asym
        )

        st.subheader("Diagnostika")

        st.write("PRIMARY DEFICIT:",deficit)
        st.write("RIZIKO:",injury)
        st.write("DOPORUČENÍ:",solution)
        st.write("RISK SCORE:",risk)

        data = {

            "player":player,
            "category":category,
            "date":datetime.now().strftime("%Y-%m-%d"),

            "risk":risk,
            "deficit":deficit,
            "injury":injury,
            "solution":solution

        }

        supabase.table("tests").insert(data).execute()

        st.success("Test uložen")

# ---------------- PLAYER CARD ----------------

with tabs[2]:

    st.header("Karta hráčů")

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

            delete_id = st.number_input(
                f"Smazat ID testu {cat}",
                step=1
            )

            if st.button(f"Smazat test {cat}"):

                supabase.table("tests").delete().eq("id",delete_id).execute()

                st.success("Test smazán")

# ---------------- TEAM SUMMARY ----------------

with tabs[3]:

    st.header("Team summary")

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

            summary = cat_df["deficit"].value_counts()

            st.write(summary)

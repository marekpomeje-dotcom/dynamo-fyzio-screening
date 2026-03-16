import streamlit as st
import pandas as pd
from supabase import create_client

# -----------------------------
# SUPABASE
# -----------------------------

SUPABASE_URL = "https://jczbpentsmzkncakedkq.supabase.co"
SUPABASE_KEY = "sb_publishable_pncl2bBUaGXvdD0bz_vB1Q_O3NPsL8_"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# PAGE
# -----------------------------

st.set_page_config(page_title="Dynamo Fyzio Screening", layout="wide")

col1,col2 = st.columns([1,6])

with col1:
    st.image("logo.png",width=120)

with col2:
    st.title("Dynamo Fyzio Screening")
    st.caption("SK Dynamo České Budějovice – Akademie")

# -----------------------------
# LOAD DATA
# -----------------------------

def load_data():

    response = supabase.table("tests").select("*").execute()

    data = response.data

    if data is None:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    df.columns = df.columns.str.lower()

    return df


df = load_data()

# -----------------------------
# CATEGORY SELECTOR
# -----------------------------

category = st.selectbox(
    "Kategorie",
    ["U16","U17","U18","U19"]
)

if len(df) > 0:
    df = df[df["category"] == category]

# -----------------------------
# SCREENING CALCULATION
# -----------------------------

if len(df) > 0:

    df["hq_r"] = df["ham_r"] / df["quad_r"]
    df["hq_l"] = df["ham_l"] / df["quad_l"]

    df["addabd_r"] = df["add_r"] / df["abd_r"]
    df["addabd_l"] = df["add_l"] / df["abd_l"]

    risk=[]
    deficit=[]
    injury=[]
    solution=[]

    for _,row in df.iterrows():

        r="LOW"
        d=""
        i=""
        s=""

        if row["hq_r"] < 0.6 or row["hq_l"] < 0.6:

            r="HIGH"
            d="Hamstring strength"
            i="Hamstring injury risk"
            s="Nordic hamstring, RDL"

        elif row["addabd_r"] < 0.8 or row["addabd_l"] < 0.8:

            r="MEDIUM"
            d="Groin strength"
            i="Adductor injury risk"
            s="Copenhagen plank"

        elif row["ant_r"] < 70 or row["ant_l"] < 70:

            r="MEDIUM"
            d="Sagittal control"
            i="Knee injury risk"
            s="Split squat, step-down"

        risk.append(r)
        deficit.append(d)
        injury.append(i)
        solution.append(s)

    df["risk"]=risk
    df["deficit"]=deficit
    df["injury"]=injury
    df["solution"]=solution

# -----------------------------
# TABS
# -----------------------------

tab1,tab2,tab3,tab4,tab5 = st.tabs(
[
"Dashboard",
"Karta hráčů",
"Týmový přehled",
"Import dat",
"Správa dat"
]
)

# -----------------------------
# DASHBOARD
# -----------------------------

with tab1:

    st.header("Rizikoví hráči")

    if len(df)==0:

        st.info("Žádná data")

    else:

        latest = df.sort_values("date").groupby("player").tail(1)

        risk_players = latest[latest["risk"]!="LOW"]

        st.dataframe(
            risk_players[
                ["player","risk","deficit","injury","solution"]
            ],
            use_container_width=True
        )

# -----------------------------
# PLAYER CARD
# -----------------------------

with tab2:

    st.header("Karta hráče")

    if len(df)==0:

        st.info("Žádná data")

    else:

        players = sorted(df["player"].dropna().unique())

        player = st.selectbox("Vyber hráče",players)

        pdata = df[df["player"]==player]

        st.dataframe(pdata,use_container_width=True)

# -----------------------------
# TEAM SUMMARY
# -----------------------------

with tab3:

    st.header("Týmový přehled")

    if len(df)==0:

        st.info("Žádná data")

    else:

        latest = df.sort_values("date").groupby("player").tail(1)

        summary = latest["deficit"].value_counts()

        st.subheader("Hlavní deficity týmu")

        st.dataframe(summary)

# -----------------------------
# IMPORT
# -----------------------------

with tab4:

    st.header("Import CSV")

    file = st.file_uploader("Nahraj CSV")

    if file is not None:

        data = pd.read_csv(file)

        st.dataframe(data)

        if st.button("Importovat"):

            for _,row in data.iterrows():

                supabase.table("tests").insert(row.to_dict()).execute()

            st.success("Import dokončen")

# -----------------------------
# DELETE TEST
# -----------------------------

with tab5:

    st.header("Správa dat")

    if len(df)==0:

        st.info("Žádná data")

    else:

        st.write("Vyber test k odstranění")

        delete_id = st.number_input("ID testu")

        if st.button("Smazat test"):

            supabase.table("tests").delete().eq("id",delete_id).execute()

            st.success("Test odstraněn")

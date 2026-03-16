import streamlit as st
import pandas as pd
from supabase import create_client
import matplotlib.pyplot as plt

# -----------------------------
# SUPABASE CONNECTION
# -----------------------------

SUPABASE_URL = "https://jczbpentsmzkncakedkq.supabase.co"
SUPABASE_KEY = "sb_publishable_pncl2bBUaGXvdD0bz_vB1Q_O3NPsL8_"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# PAGE SETUP
# -----------------------------

st.set_page_config(page_title="Dynamo Fyzio Screening", layout="wide")

col1, col2 = st.columns([1,6])

with col1:
    st.image("logo.png", width=120)

with col2:
    st.title("Dynamo Fyzio Screening")
    st.caption("SK Dynamo České Budějovice – Akademie")

# -----------------------------
# LOAD DATA
# -----------------------------

@st.cache_data
def load_data():

    response = supabase.table("tests").select("*").execute()

    df = pd.DataFrame(response.data)

    if len(df) == 0:
        return df

    # sjednotíme názvy sloupců
    df.columns = df.columns.str.lower()

    return df


df = load_data()

# -----------------------------
# TABS
# -----------------------------

tab1, tab2, tab3, tab4 = st.tabs(
[
"Dashboard",
"Karta hráčů",
"Týmový přehled",
"Import dat"
]
)

# -----------------------------
# DASHBOARD
# -----------------------------

with tab1:

    st.header("Dashboard")

    if len(df) == 0:

        st.info("Zatím nejsou v databázi žádná data.")

    else:

        latest = df.sort_values("date").groupby("player").tail(1)

        st.dataframe(
            latest[
                [
                    "player",
                    "category",
                    "ant_r",
                    "ant_l",
                    "pm_r",
                    "pm_l",
                    "pl_r",
                    "pl_l",
                    "ham_r",
                    "ham_l"
                ]
            ],
            use_container_width=True
        )

# -----------------------------
# PLAYER CARD
# -----------------------------

with tab2:

    st.header("Karta hráčů")

    if len(df) == 0:

        st.info("Žádná data")

    else:

        players = sorted(df["player"].dropna().unique())

        player = st.selectbox("Vyber hráče", players)

        player_data = df[df["player"] == player]

        st.dataframe(player_data)

# -----------------------------
# TEAM SUMMARY
# -----------------------------

with tab3:

    st.header("Přehled týmu")

    if len(df) == 0:

        st.info("Žádná data")

    else:

        st.metric("Počet testů", len(df))

        if "ham_r" in df.columns:

            st.write("Průměr hamstring pravá:", round(df["ham_r"].mean(),2))

        if "ham_l" in df.columns:

            st.write("Průměr hamstring levá:", round(df["ham_l"].mean(),2))

# -----------------------------
# IMPORT DATA
# -----------------------------

with tab4:

    st.header("Import CSV")

    file = st.file_uploader("Nahraj CSV soubor")

    if file is not None:

        data = pd.read_csv(file)

        st.write("Náhled dat")

        st.dataframe(data)

        if st.button("Importovat do databáze"):

            for _, row in data.iterrows():

                supabase.table("tests").insert(row.to_dict()).execute()

            st.success("Data byla importována")

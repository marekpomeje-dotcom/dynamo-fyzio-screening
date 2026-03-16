import streamlit as st
import pandas as pd
from supabase import create_client

# -----------------------------
# SUPABASE CONNECTION
# -----------------------------

SUPABASE_URL = "https://jczbpentsmzkncakedkq.supabase.co"
SUPABASE_KEY = "sb_publishable_pncl2bBUaGXvdD0bz_vB1Q_O3NPsL8_"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# PAGE
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

def load_data():

    try:

        response = supabase.table("tests").select("*").execute()

        data = response.data

        if data is None:
            return pd.DataFrame()

        df = pd.DataFrame(data)

        if len(df) == 0:
            return df

        df.columns = df.columns.str.lower()

        return df

    except Exception as e:

        st.error("Chyba při načítání databáze")
        st.write(e)

        return pd.DataFrame()


df = load_data()

# -----------------------------
# SCREENING EVALUATION
# -----------------------------

if len(df) > 0:

    df["hq_ratio_r"] = df["ham_r"] / df["quad_r"]
    df["hq_ratio_l"] = df["ham_l"] / df["quad_l"]

    df["addabd_ratio_r"] = df["add_r"] / df["abd_r"]
    df["addabd_ratio_l"] = df["add_l"] / df["abd_l"]

    risk_list = []
    deficit_list = []
    injury_list = []
    solution_list = []

    for _, row in df.iterrows():

        risk = "LOW"
        deficit = ""
        injury = ""
        solution = ""

        # HAMSTRING DEFICIT
        if row["hq_ratio_r"] < 0.6 or row["hq_ratio_l"] < 0.6:

            risk = "HIGH"
            deficit = "Hamstring strength"
            injury = "Hamstring strain risk"
            solution = "Nordic hamstring, Romanian deadlift"

        # GROIN DEFICIT
        elif row["addabd_ratio_r"] < 0.8 or row["addabd_ratio_l"] < 0.8:

            risk = "MEDIUM"
            deficit = "Groin strength"
            injury = "Adductor injury risk"
            solution = "Copenhagen plank"

        # Y BALANCE DEFICIT
        elif row["ant_r"] < 65 or row["ant_l"] < 65:

            risk = "MEDIUM"
            deficit = "Sagittal plane control"
            injury = "Knee injury risk"
            solution = "Split squat, step-down"

        risk_list.append(risk)
        deficit_list.append(deficit)
        injury_list.append(injury)
        solution_list.append(solution)

    df["risk"] = risk_list
    df["deficit"] = deficit_list
    df["injury"] = injury_list
    df["solution"] = solution_list

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

    st.header("Rizikoví hráči")

    if len(df) == 0:

        st.info("Zatím nejsou v databázi žádná data.")

    else:

        risk_players = df[df["risk"] != "LOW"]

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

    st.header("Týmový přehled")

    if len(df) == 0:

        st.info("Žádná data")

    else:

        st.metric("Počet testů", len(df))

        if "ham_r" in df.columns:
            st.write("Průměr Hamstring pravá:", round(df["ham_r"].mean(),2))

        if "ham_l" in df.columns:
            st.write("Průměr Hamstring levá:", round(df["ham_l"].mean(),2))

        if "hq_ratio_r" in df.columns:
            st.write("Průměr H:Q pravá:", round(df["hq_ratio_r"].mean(),2))

        if "hq_ratio_l" in df.columns:
            st.write("Průměr H:Q levá:", round(df["hq_ratio_l"].mean(),2))

# -----------------------------
# IMPORT CSV
# -----------------------------

with tab4:

    st.header("Import dat")

    file = st.file_uploader("Nahraj CSV")

    if file is not None:

        data = pd.read_csv(file)

        st.write("Náhled dat")

        st.dataframe(data)

        if st.button("Importovat"):

            for _, row in data.iterrows():

                supabase.table("tests").insert(row.to_dict()).execute()

            st.success("Data byla importována")

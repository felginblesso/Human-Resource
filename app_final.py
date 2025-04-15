
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Custom CSS ---
st.markdown("""
    <style>
        h2 {
            font-size: 18px !important;
            color: #380835 !important;
        }
        .main-title {
            font-size: 36px !important;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            color: #0D47A1;
        }
    </style>
""", unsafe_allow_html=True)

# --- Dashboard Title ---
st.markdown('<p class="main-title">Workforce Distribution Dashboard</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- State Mapping ---
state_labels = {
    2: "Himachal Pradesh", 5: "Uttarakhand", 7: "Delhi", 8: "Rajasthan", 9: "Uttar Pradesh",
    10: "Bihar", 11: "Sikkim", 12: "Arunachal Pradesh", 13: "Nagaland", 14: "Manipur",
    15: "Mizoram", 16: "Tripura", 18: "Assam", 19: "West Bengal", 20: "Jharkhand",
    21: "Odisha", 24: "Gujarat", 27: "Maharashtra", 29: "Karnataka", 30: "Goa",
    32: "Kerala", 33: "Tamil Nadu", 34: "Puducherry"
}

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("Industrial_classification.csv")
    df["State Name"] = df["State Code"].map(state_labels)
    df["Total Workers"] = df["Main Workers - Total -  Persons"] + df["Marginal Workers - Total -  Persons"]
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Data")

selected_states = st.sidebar.multiselect("Select State(s)", df["State Name"].dropna().unique())
filtered_districts = df[df["State Name"].isin(selected_states)]["District Name"].dropna().unique() if selected_states else []
selected_districts = st.sidebar.multiselect("Select District(s)", options=filtered_districts)

# ✅ Worker Type (Main/Marginal)
worker_type = st.sidebar.radio("Select Worker Type", ["Main", "Marginal"])

# ✅ Gender (with "Both" option)
gender = st.sidebar.radio("Select Gender", ["Males", "Females", "Males & Females"])

# ✅ IndustryGroup
industry_options = df["IndustryGroup"].dropna().unique()
selected_industries = st.sidebar.multiselect("Select Industry Group(s)", industry_options, default=[])

# --- Compute column(s) based on gender selection ---
if gender == "Males & Females":
    col_male = f"{worker_type} Workers - Total - Males"
    col_female = f"{worker_type} Workers - Total - Females"
    df["Combined_Workers"] = df[col_male] + df[col_female]
    col_name = "Combined_Workers"
else:
    col_name = f"{worker_type} Workers - Total - {gender}"


# --- Filtered Data ---
if selected_states and selected_districts and selected_industries:
    filtered_df = df[
        (df["State Name"].isin(selected_states)) &
        (df["District Name"].isin(selected_districts)) &
        (df["IndustryGroup"].isin(selected_industries))
    ]
else:
    filtered_df = pd.DataFrame()

# --- Visualizations ---
if not filtered_df.empty:
    st.subheader("📊 Industry-wise Worker Distribution")

    industry_chart = px.bar(
        filtered_df.groupby("IndustryGroup")[col_name].sum().reset_index(),
        x="IndustryGroup",
        y=col_name,
        color="IndustryGroup",
        title=f"Total {worker_type} Workers ({gender}) per Industry",
    )
    st.plotly_chart(industry_chart)

    # --- District-wise Summary ---
    district_summary = filtered_df.groupby("District Name")[col_name].sum().reset_index()

    if not district_summary.empty:
        st.subheader("📊 District-wise Worker Distribution")
        district_chart = px.bar(
            district_summary,
            x="District Name",
            y=col_name,
            color=col_name,
            title=f"{worker_type} Workers ({gender}) per District",
        )
        st.plotly_chart(district_chart)

    # --- Pie Chart: State-wise Summary ---
    state_summary = filtered_df.groupby("State Name")[col_name].sum().reset_index()
    if not state_summary.empty:
        st.subheader("🥧 State-wise Worker Distribution")
        pie_chart = px.pie(
            state_summary,
            names="State Name",
            values=col_name,
            title=f"Share of {worker_type} Workers ({gender}) Across States",
            hole=0.4
        )
        st.plotly_chart(pie_chart)

else:
    st.markdown("""
        <marquee style="color:red; font-size:18px;">
        ⚠️ Please select at least one State, District, and Industry Group to see the data.
        </marquee>
    """, unsafe_allow_html=True)


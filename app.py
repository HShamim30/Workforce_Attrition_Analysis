import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Palo Alto Networks Attrition Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Workforce Attrition Patterns and Risk Hotspot Analysis")
st.markdown("### Palo Alto Networks HR Analytics Dashboard")

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("data/Palo_Alto_Networks.csv")

    # Remove extra spaces from column names
    df.columns = df.columns.str.strip()

    # Convert Attrition only if needed
    if df['Attrition'].dtype == 'object':
        df['Attrition'] = (
            df['Attrition']
            .astype(str)
            .str.strip()
            .map({'Yes': 1, 'No': 0})
        )

    return df


df = load_data()

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("🔍 Filters")

department = st.sidebar.multiselect(
    "Department",
    options=df['Department'].unique(),
    default=df['Department'].unique()
)

job_role = st.sidebar.multiselect(
    "Job Role",
    options=df['JobRole'].unique(),
    default=df['JobRole'].unique()
)

overtime = st.sidebar.multiselect(
    "OverTime",
    options=df['OverTime'].unique(),
    default=df['OverTime'].unique()
)

travel = st.sidebar.multiselect(
    "Business Travel",
    options=df['BusinessTravel'].unique(),
    default=df['BusinessTravel'].unique()
)

years = st.sidebar.slider(
    "Years At Company",
    int(df['YearsAtCompany'].min()),
    int(df['YearsAtCompany'].max()),
    (
        int(df['YearsAtCompany'].min()),
        int(df['YearsAtCompany'].max())
    )
)

# ---------------------------------------------------
# FILTER DATA
# ---------------------------------------------------

filtered_df = df[
    (df['Department'].isin(department)) &
    (df['JobRole'].isin(job_role)) &
    (df['OverTime'].isin(overtime)) &
    (df['BusinessTravel'].isin(travel)) &
    (df['YearsAtCompany'].between(years[0], years[1]))
]

# ---------------------------------------------------
# KPI SECTION
# ---------------------------------------------------

total_emp = len(filtered_df)
exited = filtered_df['Attrition'].sum()
retained = total_emp - exited

attrition_rate = 0

if total_emp > 0:
    attrition_rate = (exited / total_emp) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Employees", total_emp)
col2.metric("Exited Employees", int(exited))
col3.metric("Retained Employees", int(retained))
col4.metric("Attrition Rate", f"{attrition_rate:.2f}%")

st.markdown("---")

# ---------------------------------------------------
# ATTRITION DISTRIBUTION
# ---------------------------------------------------

st.subheader("📌 Attrition Distribution")

fig = px.pie(
    names=['Retained', 'Exited'],
    values=[retained, exited],
    hole=0.5
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# DEPARTMENT ATTRITION
# ---------------------------------------------------

st.subheader("🏢 Department-wise Attrition")

dept = (
    filtered_df
    .groupby('Department')['Attrition']
    .mean()
    .reset_index()
)

dept['Attrition'] *= 100

fig = px.bar(
    dept,
    x='Department',
    y='Attrition',
    color='Attrition',
    title='Department Attrition Rate (%)'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# JOB ROLE ATTRITION
# ---------------------------------------------------

st.subheader("👨‍💻 Job Role Attrition")

role = (
    filtered_df
    .groupby('JobRole')['Attrition']
    .mean()
    .reset_index()
)

role['Attrition'] *= 100

fig = px.bar(
    role,
    x='JobRole',
    y='Attrition',
    color='Attrition'
)

fig.update_layout(xaxis_tickangle=-45)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# AGE GROUP ANALYSIS
# ---------------------------------------------------

st.subheader("👥 Age Group Analysis")

temp_df = filtered_df.copy()

bins = [18, 25, 35, 45, 55, 65]
labels = ['18-25', '26-35', '36-45', '46-55', '56-65']

temp_df['AgeGroup'] = pd.cut(
    temp_df['Age'],
    bins=bins,
    labels=labels
)

age = (
    temp_df
    .groupby('AgeGroup')['Attrition']
    .mean()
    .reset_index()
)

age['Attrition'] *= 100

fig = px.bar(
    age,
    x='AgeGroup',
    y='Attrition',
    color='Attrition'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# GENDER ANALYSIS
# ---------------------------------------------------

st.subheader("🚻 Gender Analysis")

gender = (
    filtered_df
    .groupby('Gender')['Attrition']
    .mean()
    .reset_index()
)

gender['Attrition'] *= 100

fig = px.bar(
    gender,
    x='Gender',
    y='Attrition',
    color='Attrition'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# OVERTIME IMPACT
# ---------------------------------------------------

st.subheader("⏰ Overtime Impact")

ot = (
    filtered_df
    .groupby('OverTime')['Attrition']
    .mean()
    .reset_index()
)

ot['Attrition'] *= 100

fig = px.bar(
    ot,
    x='OverTime',
    y='Attrition',
    color='Attrition'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# BUSINESS TRAVEL
# ---------------------------------------------------

st.subheader("✈️ Business Travel Impact")

travel_df = (
    filtered_df
    .groupby('BusinessTravel')['Attrition']
    .mean()
    .reset_index()
)

travel_df['Attrition'] *= 100

fig = px.bar(
    travel_df,
    x='BusinessTravel',
    y='Attrition',
    color='Attrition'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# DISTANCE FROM HOME
# ---------------------------------------------------

st.subheader("🏠 Distance From Home")

fig = px.box(
    filtered_df,
    x='Attrition',
    y='DistanceFromHome',
    color='Attrition'
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------
# HEATMAP
# ---------------------------------------------------

st.subheader("🔥 Department vs Job Role Heatmap")

heat = filtered_df.pivot_table(
    index='Department',
    columns='JobRole',
    values='Attrition',
    aggfunc='mean'
)

fig, ax = plt.subplots(figsize=(14, 6))

sns.heatmap(
    heat,
    annot=True,
    cmap='Reds',
    fmt=".2f",
    ax=ax
)

st.pyplot(fig)

# ---------------------------------------------------
# CORRELATION HEATMAP
# ---------------------------------------------------

st.subheader("📈 Correlation Heatmap")

corr = filtered_df.corr(numeric_only=True)

fig, ax = plt.subplots(figsize=(12, 8))

sns.heatmap(
    corr,
    cmap='coolwarm',
    ax=ax
)

st.pyplot(fig)

# ---------------------------------------------------
# RAW DATA
# ---------------------------------------------------

st.subheader("📄 Dataset Preview")

st.dataframe(filtered_df.head(20))

# ---------------------------------------------------
# INSIGHTS
# ---------------------------------------------------

st.subheader("💡 Key Insights")

st.markdown("""
- Identify departments with high attrition.
- Identify high-risk job roles.
- Analyze impact of overtime and business travel.
- Detect demographic attrition patterns.
- Evaluate tenure-related attrition trends.
""")
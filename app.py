import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from backend import df_analysis, risk_score

st.set_page_config(page_title="Job Analyzer", layout="wide")

st.title("💼 Job Fraud Detection & Market Insights")

# =========================
# SIDEBAR
# =========================
page = st.sidebar.radio(
    "Navigation",
    ["Fraud Checker", "Dashboard", "Data Explorer"]
)
# =========================
# FILTER PANEL
# =========================
st.sidebar.header("Filters")

selected_risk = st.sidebar.multiselect(
    "Select Risk Level",
    df_analysis['risk_level'].unique(),
    default=df_analysis['risk_level'].unique()
)

selected_group = st.sidebar.multiselect(
    "Select Job Group",
    df_analysis['job_group'].unique(),
    default=df_analysis['job_group'].unique()
)

# Apply filters
df_filtered = df_analysis[
    (df_analysis['risk_level'].isin(selected_risk)) &
    (df_analysis['job_group'].isin(selected_group))
]
col1, col2, col3 = st.columns(3)

col1.metric("Total Jobs", len(df_filtered))

col2.metric("High Risk %",
            round((df_filtered['risk_level'] == 'High Risk').mean() * 100, 2))

col3.metric("Avg Risk Score",
            round(df_filtered['risk_score'].mean(), 2))
# =========================
# PAGE 1 — FRAUD CHECKER
# =========================
if page == "Fraud Checker":

    st.header("🔍 Job Risk Analyzer")

    col1, col2 = st.columns(2)

    with col1:
        description = st.text_area("Job Description")
        requirements = st.text_area("Requirements")

    with col2:
        company = st.text_input("Company Profile")
        salary = st.text_input("Salary Range")

    if st.button("Analyze Risk"):

        row = {
            'description': description.lower(),
            'company_profile': company.lower(),
            'salary_range': salary.lower(),
            'requirements': requirements.lower()
        }

        score = risk_score(pd.Series(row))

        if score >= 6:
            st.error(f"High Risk ⚠️ (Score: {score})")
        elif score >= 3:
            st.warning(f"Moderate Risk ⚠️ (Score: {score})")
        else:
            st.success(f"Low Risk ✅ (Score: {score})")

# =========================
# PAGE 2 — DASHBOARD
# =========================
elif page == "Dashboard":

    st.header("📊 Market Insights")

    # ---------- ROW 1 ----------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Risk Distribution")

        fig, ax = plt.subplots()
        df_analysis['risk_level'].value_counts(normalize=True).plot(kind='bar', ax=ax)
        ax.set_xlabel("Risk Level")
        ax.set_ylabel("Proportion")

        st.pyplot(fig)

    with col2:
        st.subheader("Fraud Rate by Job Group")

        df_labeled = df_analysis[df_analysis['fraudulent'] != -1]
        fraud_rate = df_labeled.groupby('job_group')['fraudulent'].mean()

        fig, ax = plt.subplots()
        fraud_rate.plot(kind='bar', ax=ax)
        ax.set_ylabel("Fraud Probability")

        st.pyplot(fig)

    # ---------- ROW 2 ----------
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Description Length vs Risk")

        fig, ax = plt.subplots()
        ax.scatter(df_analysis['desc_length'], df_analysis['risk_score'], alpha=0.3)
        ax.set_xlabel("Description Length")
        ax.set_ylabel("Risk Score")

        st.pyplot(fig)

    with col4:
        st.subheader("Description Length by Risk")

        fig, ax = plt.subplots()
        sns.boxplot(x='risk_level', y='desc_length', data=df_analysis, ax=ax)

        st.pyplot(fig)

    # ---------- ROW 3 ----------
    col5, col6 = st.columns(2)

    with col5:
        st.subheader("Top Skills (%)")

        skill_pct = df_analysis['skills'].explode().value_counts(normalize=True) * 100
        skill_pct = skill_pct.head(6)

        fig, ax = plt.subplots()
        skill_pct.sort_values().plot(kind='barh', ax=ax)
        ax.set_xlabel("Percentage")

        st.pyplot(fig)

    with col6:
        st.subheader("Skill vs Risk")

        skill_df = df_analysis.explode('skills')

        skill_risk = pd.crosstab(
            skill_df['skills'],
            skill_df['risk_level'],
            normalize='index'
        )

        skill_risk = skill_risk.loc[skill_pct.index]

        fig, ax = plt.subplots()
        skill_risk.plot(kind='bar', stacked=True, ax=ax)

        st.pyplot(fig)

    # ---------- ROW 4 ----------
    col7, col8 = st.columns(2)

    with col7:
        st.subheader("Skill Risk Heatmap")

        fig, ax = plt.subplots()
        sns.heatmap(skill_risk, annot=True, fmt=".2f", ax=ax)

        st.pyplot(fig)

    with col8:
        st.subheader("Cluster Distribution")

        fig, ax = plt.subplots()
        df_analysis['cluster'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_ylabel("")

        st.pyplot(fig)

# =========================
# PAGE 3 — DATA EXPLORER
# =========================
elif page == "Data Explorer":

    st.header("📁 Data Explorer")

    risk_filter = st.selectbox(
        "Select Risk Level",
        df_analysis['risk_level'].unique()
    )

    filtered = df_analysis[df_analysis['risk_level'] == risk_filter]

    st.dataframe(filtered.head(50))
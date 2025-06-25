import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.image("UCSD-Symbol.png", width=200)  # adjust width as needed


# Load cleaned data
df = pd.read_excel("cleaned_nicu_data.xlsx")

# Sidebar navigation
st.sidebar.title("Navigation")
section = st.sidebar.radio("Go to section:", [
    "Overview",
    "Milk & Additives",
    "Growth Trajectories",
    "DOL Metrics"
])


# ================= OVERVIEW =====================
if section == "Overview":
    st.title("NICU Dashboard")
    
    st.subheader("About the Samples")

    num_subjects = df['Subject ID'].nunique()
    num_samples = len(df)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Samples", num_samples)
    with col2:
        st.metric("Unique Subjects", num_subjects)

    st.markdown("**Samples per Subject:**")
    samples_per_subject = df['Subject ID'].value_counts().sort_index()
    st.bar_chart(samples_per_subject)

    st.markdown(
        "*Note: Two entries log subject IDs (`NB00405` and `NB00406`, `NB00467` and `NB00438`) together and treated as a single subject for analysis.*",
        unsafe_allow_html=True
    )

    st.subheader("Aliquots Overview")
    total_aliquots = df['Aliquots'].sum()
    avg_aliquots = round(df['Aliquots'].mean(), 3)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Aliquots Collected", total_aliquots)
    with col2:
        st.metric("Avg Aliquots per Sample", avg_aliquots)

    min_val, max_val = float(df['Aliquots'].min()), float(df['Aliquots'].max())
    aliquot_range = st.slider("Filter by Aliquot Count", min_val, max_val, (min_val, max_val))
    filtered_df = df[df['Aliquots'].between(*aliquot_range)]

    fig = px.histogram(
        filtered_df,
        x="Aliquots",
        nbins=20,
        title="Distribution of Aliquots per Sample",
        labels={"Aliquots": "Number of Aliquots"},
        template="simple_white"
    )
    fig.update_layout(xaxis_title="Number of Aliquots", yaxis_title="Number of Samples", bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)

    aliquots_per_subject = df.groupby("Subject ID")["Aliquots"].sum().reset_index()
    aliquots_per_subject = aliquots_per_subject.sort_values(by="Aliquots", ascending=False)
    fig = px.bar(
        aliquots_per_subject,
        x="Subject ID",
        y="Aliquots",
        title="Total Number of Aliquots per Subject",
        labels={"Aliquots": "Total Aliquots"},
        template="simple_white"
    )
    fig.update_layout(xaxis_title="Subject ID", yaxis_title="Total Aliquots", xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# ================ MILK & ADDITIVES ================
# ================ MILK & ADDITIVES ================
elif section == "Milk & Additives":
    st.subheader("Milk Composition")

    milk_counts = df['Type of Milk'].value_counts().reset_index()
    milk_counts.columns = ['Type of Milk', 'Sample Count']
    fig_milk = px.pie(milk_counts, names='Type of Milk', values='Sample Count', title='Type of Milk (MBM vs. DBM)', hole=0.3)
    fig_milk.update_traces(textposition='inside', textinfo='percent+label')

    iron_counts = df['Iron'].value_counts().reset_index()
    iron_counts.columns = ['Iron', 'Sample Count']
    fig_iron = px.pie(iron_counts, names='Iron', values='Sample Count', title='Iron Supplementation', hole=0.3)
    fig_iron.update_traces(textposition='inside', textinfo='percent+label')

    hmf_counts = df['HMF'].value_counts().reset_index()
    hmf_counts.columns = ['HMF', 'Sample Count']
    fig_hmf = px.pie(hmf_counts, names='HMF', values='Sample Count', title='Human Milk Fortifier (HMF)', hole=0.3)
    fig_hmf.update_traces(textposition='inside', textinfo='percent+label')

    tpn_counts = df['TPN'].value_counts().reset_index()
    tpn_counts.columns = ['TPN', 'Sample Count']
    fig_tpn = px.pie(tpn_counts, names='TPN', values='Sample Count', title='Total Parenteral Nutrition (TPN)', hole=0.3)
    fig_tpn.update_traces(textposition='inside', textinfo='percent+label')

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.plotly_chart(fig_milk, use_container_width=True)
    with row1_col2:
        st.plotly_chart(fig_iron, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.plotly_chart(fig_hmf, use_container_width=True)
    with row2_col2:
        st.plotly_chart(fig_tpn, use_container_width=True)

    comment_counts = df['Additional Comments'].value_counts(dropna=False).reset_index()
    comment_counts.columns = ['Additional Comments', 'Sample Count']
    fig_comments = px.pie(comment_counts, names='Additional Comments', values='Sample Count', title='Sample Annotations (Additional Comments)', hole=0.3)
    fig_comments.update_traces(textposition='inside', textinfo='percent+label')
    fig_comments.update_layout(template="simple_white")
    st.plotly_chart(fig_comments, use_container_width=True)

    st.caption("**Note**: 'Additional Comments' contains inconsistent text formatting in the original dataset. Will be cleaned in future updates.")

# ================ GROWTH TRAJECTORIES ================
elif section == "Growth Trajectories":
    st.subheader("📈 Growth Trajectories")

    dol_counts = df.groupby("Subject ID")["DOL"].nunique()
    more_than_2 = (dol_counts > 2).sum()
    more_than_5 = (dol_counts > 5).sum()

    st.markdown(f"- **Subjects with >2 unique DOLs:** {more_than_2}")
    st.markdown(f"- **Subjects with >5 unique DOLs:** {more_than_5}")

    df = df.sort_values(["Subject ID", "DOL"])
    subject_counts = df.groupby("Subject ID")["DOL"].nunique()
    valid_subjects = subject_counts[subject_counts > 1].index
    df_growth = df[df["Subject ID"].isin(valid_subjects)]

    selected_subjects = st.multiselect(
        "Select Subject(s) to View Trajectories",
        options=valid_subjects,
        default=list(valid_subjects)
    )

    df_plot = df_growth[df_growth["Subject ID"].isin(selected_subjects)]

    with st.expander("📈 Weight Trajectories", expanded=True):
        fig_wt = px.line(
            df_plot,
            x="DOL",
            y="Current Weight",
            color="Subject ID",
            markers=True,
            title="Weight Trajectories by Subject (2+ Samples)",
            labels={"DOL": "Day of Life (DOL)", "Current Weight": "Weight (g)"}
        )
        fig_wt.update_layout(template="simple_white")
        st.plotly_chart(fig_wt, use_container_width=True)
        st.caption("Only included subjects with more than one sample to show weight trajectories.")

    with st.expander("📏 Height Trajectories", expanded=False):
        fig_height = px.line(
            df_plot,
            x="DOL",
            y="Current Height",
            color="Subject ID",
            markers=True,
            title="Height Trajectories by Subject (2+ Samples)",
            labels={"DOL": "Day of Life (DOL)", "Current Height": "Height (cm)"}
        )
        fig_height.update_layout(template="simple_white")
        st.plotly_chart(fig_height, use_container_width=True)
        st.caption("Only included subjects with more than one sample to show height trajectories.")

    with st.expander("🧠 Head Circumference Trajectories", expanded=False):
        fig_hc = px.line(
            df_plot,
            x="DOL",
            y="Current HC",
            color="Subject ID",
            markers=True,
            title="Head Circumference Trajectories by Subject (2+ Samples)",
            labels={"DOL": "Day of Life (DOL)", "Current HC": "Head Circumference (cm)"}
        )
        fig_hc.update_layout(template="simple_white")
        st.plotly_chart(fig_hc, use_container_width=True)
        st.caption("Only included subjects with more than one sample to show HC trajectories.")

# ================ DOL DISCREPANCY ================
elif section == "DOL Metrics":
    st.subheader("🔍 DOL per Subject")

    dol_range = df.groupby("Subject ID")["DOL"].agg(["min", "max"]).reset_index()
    dol_range["Range"] = dol_range["max"] - dol_range["min"]

    dol_points = df[["Subject ID", "DOL"]].dropna()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=dol_range["Subject ID"],
        y=dol_range["Range"],
        base=dol_range["min"],
        name="DOL Range",
        marker_color="lightblue"
    ))
    fig.add_trace(go.Scatter(
        x=dol_points["Subject ID"],
        y=dol_points["DOL"],
        mode="markers",
        name="Sample DOLs",
        marker=dict(size=6, color="darkblue", opacity=0.7),
        yaxis="y"
    ))
    fig.update_layout(
        title="Sampling Range and DOL Sample Points per Subject",
        xaxis_title="Subject ID",
        yaxis_title="Day of Life (DOL)",
        barmode="overlay",
        template="simple_white",
        xaxis_tickangle=-45,
        height=700
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption("📘 Bars represent the observed DOL range (min to max) for each subject. Dots show individual sampling days. This layout ensures bar height reflects range, and dots show actual DOLs (e.g., up to DOL 90).")

    st.caption("""
    **🗂️ DOL Category Key:**  
    - **Early Sampling**: DOL ≤ 14  
    - **Acute NICU Phase**: DOL 15–28  
    - **Extended NICU Phase**: DOL 29–60  
    - **Long-Term NICU**: DOL > 60  
    - **Unknown**: DOL missing or not categorized
    """)

    dol_counts = df.groupby(["Subject ID", "DOL Category"]).size().reset_index(name="Sample Count")
    dol_counts["Total"] = dol_counts.groupby("Subject ID")["Sample Count"].transform("sum")
    dol_counts_sorted = dol_counts.sort_values("Total", ascending=False)

    fig = px.bar(
        dol_counts_sorted,
        y="Subject ID",
        x="Sample Count",
        color="DOL Category",
        barmode="stack",
        orientation="h",
        title="Samples by DOL Category per Subject"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=800)
    st.plotly_chart(fig, use_container_width=True)

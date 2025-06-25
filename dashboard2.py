import pandas as pd
import numpy as np
import streamlit as st
import streamlit as st
import pandas as pd
import plotly.express as px


# Load cleaned data
df = pd.read_excel("cleaned_nicu_data.xlsx")  

# Page title
st.title("NICU Sample Dashboard")
st.subheader("📊 About the Samples")

# Basic Stats
num_subjects = df['Subject ID'].nunique()
num_samples = len(df)

# st.markdown(f"**Total Number of Samples:** {num_samples}")
# st.markdown(f"**Number of Unique Subjects:** {num_subjects}")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Samples", num_samples)

with col2:
    st.metric("Unique Subjects", num_subjects)


#Display samples per subject
st.markdown("**Samples per Subject:**")
samples_per_subject = df['Subject ID'].value_counts().sort_index()
st.bar_chart(samples_per_subject)

st.markdown(
    "*Note: Two entries log subject IDs (`NB00405` and `NB00406`, `NB00467` and `NB00438`) together and treated as a single subject for analysis.*",
    unsafe_allow_html=True
)


st.subheader("Aliquots Overview")

total_aliquots = df['Aliquots'].sum()
avg_aliquots = df['Aliquots'].mean()
min_aliquots = df['Aliquots'].min()
max_aliquots = df['Aliquots'].max()

avg_aliquots = round(avg_aliquots, 3)

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Aliquots Collected", total_aliquots)

with col2:
    st.metric("Average Aliquot per Sample", avg_aliquots)
    
# st.markdown(f"**Total Aliquots Collected:** {total_aliquots:.1f}")
# st.markdown(f"**Average Aliquots per Sample:** {avg_aliquots:.2f}")
# st.markdown(f"**Range per Sample:** {min_aliquots} to {max_aliquots}")


# Slider to filter by Aliquot count
min_val, max_val = float(df['Aliquots'].min()), float(df['Aliquots'].max())
aliquot_range = st.slider("Filter by Aliquot Count", min_val, max_val, (min_val, max_val))

# Filter the DataFrame
filtered_df = df[df['Aliquots'].between(*aliquot_range)]

# Plotly interactive histogram using the filtered data
fig = px.histogram(
    filtered_df,
    x="Aliquots",
    nbins=20,
    title="Distribution of Aliquots per Sample",
    labels={"Aliquots": "Number of Aliquots"},
    template="simple_white"
)

fig.update_layout(
    xaxis_title="Number of Aliquots",
    yaxis_title="Number of Samples",
    bargap=0.1
)

# Show plot
st.plotly_chart(fig, use_container_width=True)



# Group and sum aliquots per Subject ID
aliquots_per_subject = df.groupby("Subject ID")["Aliquots"].sum().reset_index()

# Sort by subject ID or total if you prefer
aliquots_per_subject = aliquots_per_subject.sort_values(by="Aliquots", ascending=False)

# Plot
fig = px.bar(
    aliquots_per_subject,
    x="Subject ID",
    y="Aliquots",
    title="Total Number of Aliquots per Subject",
    labels={"Aliquots": "Total Aliquots"},
    template="simple_white"
)

fig.update_layout(
    xaxis_title="Subject ID",
    yaxis_title="Total Aliquots",
    xaxis_tickangle=-45
)

st.plotly_chart(fig, use_container_width=True)


import plotly.express as px
import streamlit as st

st.subheader("🍼 Milk Composition & Supplementation")

# --- Pie 1: Type of Milk ---
milk_counts = df['Type of Milk'].value_counts().reset_index()
milk_counts.columns = ['Type of Milk', 'Sample Count']
fig_milk = px.pie(
    milk_counts,
    names='Type of Milk',
    values='Sample Count',
    title='Type of Milk (MBM vs. DBM)',
    hole=0.3
)
fig_milk.update_traces(textposition='inside', textinfo='percent+label')

# --- Pie 2: Iron ---
iron_counts = df['Iron'].value_counts().reset_index()
iron_counts.columns = ['Iron', 'Sample Count']
fig_iron = px.pie(
    iron_counts,
    names='Iron',
    values='Sample Count',
    title='Iron Supplementation',
    hole=0.3
)
fig_iron.update_traces(textposition='inside', textinfo='percent+label')

# --- Pie 3: HMF ---
hmf_counts = df['HMF'].value_counts().reset_index()
hmf_counts.columns = ['HMF', 'Sample Count']
fig_hmf = px.pie(
    hmf_counts,
    names='HMF',
    values='Sample Count',
    title='Human Milk Fortifier (HMF)',
    hole=0.3
)
fig_hmf.update_traces(textposition='inside', textinfo='percent+label')

# --- Pie 4: TPN ---
tpn_counts = df['TPN'].value_counts().reset_index()
tpn_counts.columns = ['TPN', 'Sample Count']
fig_tpn = px.pie(
    tpn_counts,
    names='TPN',
    values='Sample Count',
    title='Total Parenteral Nutrition (TPN)',
    hole=0.3
)
fig_tpn.update_traces(textposition='inside', textinfo='percent+label')

# --- Display as 2x2 grid ---
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
    
    
# --- Pie: Additional Comments ---
comment_counts = df['Additional Comments'].value_counts(dropna=False).reset_index()
comment_counts.columns = ['Additional Comments', 'Sample Count']

fig_comments = px.pie(
    comment_counts,
    names='Additional Comments',
    values='Sample Count',
    title='Sample Annotations (Additional Comments)',
    hole=0.3
)
fig_comments.update_traces(textposition='inside', textinfo='percent+label')
fig_comments.update_layout(template="simple_white")

st.plotly_chart(fig_comments, use_container_width=True)



st.caption("**Note**: the 'errors' in nomenclature consistency from the original dataset. Will clean for future updates.")



st.subheader("Observed Sample Collection")





import plotly.graph_objects as go

# Step 1: Get DOL min and max per subject
dol_range = df.groupby("Subject ID")["DOL"].agg(["min", "max"]).reset_index()
dol_range["Range"] = dol_range["max"] - dol_range["min"]

# Step 2: Get individual sample DOLs
dol_points = df[["Subject ID", "DOL"]].dropna()

# Step 3: Plot bars from min to max using 'base'
fig = go.Figure()

fig.add_trace(go.Bar(
    x=dol_range["Subject ID"],
    y=dol_range["Range"],            # height of bar = max - min
    base=dol_range["min"],           # start bar at min DOL
    name="DOL Range",
    marker_color="lightblue"
))

# Step 4: Overlay individual DOL dots
fig.add_trace(go.Scatter(
    x=dol_points["Subject ID"],
    y=dol_points["DOL"],
    mode="markers",
    name="Sample DOLs",
    marker=dict(size=6, color="darkblue", opacity=0.7),
    yaxis="y"
))

# Step 5: Layout
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

st.caption(
    "📘 Bars represent the observed DOL range (min to max) for each subject. Dots show individual sampling days. This layout ensures bar height reflects range, and dots show actual DOLs (e.g., up to DOL 90)."
)



st.caption("""
**🗂️ DOL Category Key:**  
- **Early Sampling**: DOL ≤ 14  
- **Acute NICU Phase**: DOL 15–28  
- **Extended NICU Phase**: DOL 29–60  
- **Long-Term NICU**: DOL > 60  
- **Unknown**: DOL missing or not categorized
""")

# Count samples per subject per DOL category
dol_counts = df.groupby(["Subject ID", "DOL Category"]).size().reset_index(name="Sample Count")

# Add total per subject to sort
dol_counts["Total"] = dol_counts.groupby("Subject ID")["Sample Count"].transform("sum")
dol_counts_sorted = dol_counts.sort_values("Total", ascending=False)

# Create horizontal grouped bar chart
fig = px.bar(
    dol_counts_sorted,
    y="Subject ID",
    x="Sample Count",
    color="DOL Category",
    barmode="stack",
    orientation="h",
    title="Samples by DOL Category per Subject"
)

fig.update_layout(
    yaxis={'categoryorder':'total ascending'},
    height=800
)

st.plotly_chart(fig, use_container_width=True)






import streamlit as st
import plotly.express as px
import pandas as pd

st.header("📈 Growth Trajectories")

# Count DOLs per subject
dol_counts = df.groupby("Subject ID")["DOL"].nunique()

# Calculate subject counts based on DOL thresholds
more_than_2 = (dol_counts > 2).sum()
more_than_5 = (dol_counts > 5).sum()

# Display metrics
st.markdown(f"- **Subjects with >2 unique DOLs:** {more_than_2}")
st.markdown(f"- **Subjects with >5 unique DOLs:** {more_than_5}")


# Sort and filter
df = df.sort_values(["Subject ID", "DOL"])
subject_counts = df.groupby("Subject ID")["DOL"].nunique()
valid_subjects = subject_counts[subject_counts > 1].index
df_growth = df[df["Subject ID"].isin(valid_subjects)]

# Subject selection (shared for all 3 plots)
selected_subjects = st.multiselect(
    "Select Subject(s) to View Trajectories",
    options=valid_subjects,
    default=list(valid_subjects)
)

df_plot = df_growth[df_growth["Subject ID"].isin(selected_subjects)]

# --- Weight ---
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

# --- Height ---
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

# --- Head Circumference ---
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


st.subheader("📊 Growth Correlations to Milk Type")
st.caption("Unable to make correlation plots due to missing data in the cleaned dataset as well as low significance. Will be added in future updates.")







import plotly.express as px
import plotly.express as px

st.subheader("📊 DOL Collection Discrepancies")
st.caption("This section visualizes discrepancies between the main DOL and the collection DOL for each sample. Discrepancies are flagged when the two values differ.")
st.markdown("**True** = _There is a discrepancy_ between the DOL recorded in the main dataset and the DOL recorded at collection.")
st.markdown("**False** = DOL matches DOL recorded at collection")

# Count True vs False in the flag
discrepancy_counts = df["DOL Collection Discrepancy Flag"].value_counts(dropna=False).reset_index()
discrepancy_counts.columns = ["Discrepancy", "Sample Count"]

# Plot pie chart
fig_discrepancy = px.pie(
    discrepancy_counts,
    names="Discrepancy",
    values="Sample Count",
    title="Proportion of Samples with DOL Discrepancies (Main vs Collection)",
    hole=0.3
)
fig_discrepancy.update_traces(textposition='inside', textinfo='percent+label')
fig_discrepancy.update_layout(template="simple_white")

st.plotly_chart(fig_discrepancy, use_container_width=True)


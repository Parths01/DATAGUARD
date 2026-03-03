from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="DataGuard", page_icon="🛡️", layout="wide")

st.title("DataGuard Overview")
st.caption("Data quality and observability platform")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Overall health", "92%", "Healthy")
with col2:
    st.metric("Monitored datasets", "8", "+2")
with col3:
    st.metric("Open incidents", "3", "2 critical")
with col4:
    st.metric("24h pass rate", "96%", "+4%")

st.subheader("Dataset health")
for dataset in ["orders", "customers", "payments", "reviews"]:
    with st.container():
        st.markdown(f"### {dataset.title()}")
        st.progress(88, text="Health score: 88%")

st.subheader("Open incidents")
st.table({
    "Severity": ["Critical", "Warning", "Warning"],
    "Dataset": ["orders", "payments", "reviews"],
    "Check": ["not_null", "accepted_values", "row_count_between"],
    "Time opened": ["10:25", "13:12", "15:49"],
})

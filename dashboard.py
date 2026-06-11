import plotly.express as px
import streamlit as st

def show_dashboard(df):

    st.title("Digital Marketing Analytics Dashboard")

    st.subheader("Campaign Data")
    st.dataframe(df)

    st.subheader("Average CTR")

    ctr = df.groupby(
        "Platform"
    )["CTR"].mean().reset_index()

    fig1 = px.bar(
        ctr,
        x="Platform",
        y="CTR"
    )

    st.plotly_chart(fig1)

    st.subheader("Average ROI")

    roi = df.groupby(
        "Platform"
    )["ROI"].mean().reset_index()

    fig2 = px.bar(
        roi,
        x="Platform",
        y="ROI"
    )

    st.plotly_chart(fig2)

    st.subheader("Conversions")

    fig3 = px.pie(
        df,
        names="Platform",
        values="Conversions"
    )

    st.plotly_chart(fig3)
    
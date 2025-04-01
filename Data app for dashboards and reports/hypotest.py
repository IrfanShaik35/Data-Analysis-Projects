import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_extras.metric_cards import style_metric_cards
from scipy import stats

def hypo(df):
    st.write(" ")
   
    st.markdown("<h1 style='text-align: center; '>HYPOTHESIS TESTING  (T-TEST AND Z-TEST)</h1>", unsafe_allow_html=True)

    st.write(" ")
    st.write(" ")
    with st.expander("Show Data overview"):
        st.subheader("Data preview")
        st.dataframe(df, use_container_width=True)
    st.write(" ")

    
    # Select numerical columns
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(num_cols) < 2:
        st.error("Dataset must contain at least two numerical columns for hypothesis testing.")
    else:
        st.sidebar.subheader("Select Groups for Hypothesis Testing")
        group1 = st.sidebar.selectbox("Select First Group", num_cols)
        group2 = st.sidebar.selectbox("Select Second Group", num_cols)
        confidence_level = st.sidebar.slider("Select Confidence Level", 0.90, 0.99, 0.95)
        
        # Perform hypothesis testing
        sample_size = min(len(df[group1].dropna()), len(df[group2].dropna()))
        sample_mean = df[[group1, group2]].mean()
        sample_std = df[[group1, group2]].std()
        alpha = 1 - confidence_level

        
        
        if sample_size < 30:
            test_type = "T-Test"
            t_stat, p_value = stats.ttest_ind(df[group1].dropna(), df[group2].dropna())
            critical_value = stats.t.ppf(1 - alpha / 2, df=sample_size - 1)
            
        else:
            test_type = "Z-Test"
            mean1, mean2 = df[group1].mean(), df[group2].mean()
            std1, std2 = df[group1].std(), df[group2].std()
            SE = np.sqrt((std1**2 / len(df[group1])) + (std2**2 / len(df[group2])))
            t_stat = (mean1 - mean2) / SE
            critical_value = stats.norm.ppf(1 - alpha / 2)
            
        # Plot distribution
        x = np.linspace(-4, 4, 1000)
        y = stats.t.pdf(x, df=sample_size - 1) if test_type == "T-Test" else stats.norm.pdf(x, 0, 1)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Probability Density'))
        fig.add_shape(type="line", x0=critical_value, y0=0, x1=critical_value, y1=max(y),
                      line=dict(color='red', width=2, dash='dash'), name='Critical Value')
        fig.add_shape(type="line", x0=t_stat, y0=0, x1=t_stat, y1=max(y),
                      line=dict(color='green', width=2), name='T-Statistic')
        fig.update_layout(title=f"{test_type} Distribution", xaxis_title='T/Z Score',
                          yaxis_title='Probability Density', showlegend=True)
        
        # Decision
        if abs(t_stat) > critical_value:
            st.success(f"✔ REJECT NULL HYPOTHESIS: The means of {group1} and {group2} are significantly different.")
        else:
            st.warning(f"⚠ FAIL TO REJECT NULL HYPOTHESIS: The means of {group1} and {group2} are not significantly different.")
        
        st.write(" ")
        a1, a2, a3 = st.columns(3)
        a1.metric("SAMPLE SIZE", f"{sample_size:,.0f}")
        a2.metric("COMPUTED VALUE", f"{t_stat:.3f}")
        a3.metric("CRITICAL VALUE", f"{critical_value:.3f}")
        style_metric_cards(
        background_color="#1a1c29",
        border_left_color="#a855f7",
        border_color="#a855f7",
        box_shadow="#a855f7"
        )

        # Display statistical results
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Sample Mean of Groups {group1} and {group2}")
            st.dataframe(sample_mean, use_container_width=True)
        with col2:
            st.write(f"Sample Standard of Dev Groups {group1} and {group2}")
            st.dataframe(sample_std, use_container_width=True)
        
        
            
        st.plotly_chart(fig, use_container_width=True)
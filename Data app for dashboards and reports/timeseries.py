import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly
import plotly.graph_objs as go
from streamlit_extras.metric_cards import style_metric_cards
import warnings
warnings.filterwarnings('ignore')


def times(df,date_cols):
    st.write(" ")
    st.markdown("<h1 style='text-align: center; '>TIME SERIES FORECASTING</h1>", unsafe_allow_html=True)

    

    st.write(" ")
    st.write(" ")
    
    st.subheader("Data preview")
    st.dataframe(df, use_container_width=True)
    st.write(" ")

    # Convert column names to lowercase for uniformity
    df.columns = [col.strip() for col in df.columns]
    date_cols = [col.strip() for col in date_cols]  # Ensure consistency

    # Select a single date column
    date_col = None
    for col in date_cols:
        if col in df.columns:
            date_col = col
            break

    # Find numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not date_col:
        st.error("⚠️ No valid date column found in dataset.")
        return

    if not numeric_cols:
        st.error("⚠️ No numeric column found for forecasting.")
        return

    st.sidebar.write(" ")
    value_col = st.sidebar.selectbox("Select Value for Forecasting", numeric_cols)
    # Convert date column safely
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df.dropna(subset=[date_col] + numeric_cols, inplace=True)

    # Rename for Prophet
    df = df.rename(columns={date_col: "ds", value_col: "y"})
    df["y"] = pd.to_numeric(df["y"], errors="coerce")  # Convert non-numeric values to NaN
    df.dropna(subset=["y"], inplace=True)  # Remove rows where 'y' is NaN

    if df.shape[0] < 2:  # Ensure enough data
        st.error("⚠️ Not enough valid data points to perform forecasting. Please check your dataset.")
        return
    # Prophet Model  
    st.sidebar.write(" ")
    st.sidebar.subheader("Forecasting Configuration")
    periods = st.sidebar.number_input("Forecast Periods", 1, 100, 10)
    freq_options = {"Day": "D", "Week": "W", "Month": "M"}
    freq = freq_options[st.sidebar.selectbox("Frequency", ["Day", "Week", "Month"], index=0)]
    if st.sidebar.button("Generate Forecast"):
        with st.spinner("Training model..."):
            model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
            model.fit(df)
            future = model.make_future_dataframe(periods=periods, freq=freq)
            forecast = model.predict(future)
            # Extract last known value & forecasted value
            last_observed = df.iloc[-1]["y"]
            predicted_value = forecast.iloc[-1]["yhat"]
            lower_bound = forecast.iloc[-1]["yhat_lower"]
            upper_bound = forecast.iloc[-1]["yhat_upper"]

            # Display key statistics
            col1, col2,col3 = st.columns([1,1,2])
            with col1:
                
                st.markdown("<h6>LAST OBSERVED VALUE</h6>", unsafe_allow_html=True)
                st.metric("Actual Value", f"{last_observed:,.2f}")
            with col2:
        
                st.markdown("<h6>FORECASTED VALUE</h6>", unsafe_allow_html=True)
                st.metric("Predicted", f"{predicted_value:,.2f}")

            with col3:
                
                st.markdown("<h6 style='text-align: center; '>CONFIDENCE INTERVAL</h6>", unsafe_allow_html=True)
                a1, a2 = st.columns(2)
                a1.metric("Lower Bound", f"{lower_bound:,.2f}")
                a2.metric("Upper Bound", f"{upper_bound:,.2f}")

            style_metric_cards(
        background_color="#1a1c29",
        border_left_color="#a855f7",
        border_color="#a855f7",
        box_shadow="#a855f7"
            )
            # Forecast Results
            st.subheader("Forecast Results")
            forecast_display = forecast.rename(columns={
            "ds": "Date",
             "yhat": "Predicted Value",
            "yhat_lower": "Lower Bound",
            "yhat_upper": "Upper Bound"
             })

            st.dataframe(forecast_display.tail(10), use_container_width=True)
            st.write(" ")
            # Forecast Visualization
            st.subheader("Forecast Visualization")
            fig = plot_plotly(model, forecast)

            # Rename x-axis labels based on selected frequency
            freq_label = {"D": "Day", "W": "Week", "M": "Month"}
            selected_freq = freq_label[freq]  # Get the full name

            fig.update_layout(
            xaxis_title=f"Date ({selected_freq})",  # Update x-axis label
            yaxis_title="Forecasted Value",
            
            )

            st.plotly_chart(fig, use_container_width=True)

            st.write(" ")
            # Forecast Components
            st.subheader("Forecast Components")
            st.plotly_chart(plot_components_plotly(model, forecast), use_container_width=True)

        

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from knnmodel import knn
from kmean import km
from hypotest import hypo
from timeseries import times


def think(df,uploaded_file):
    
   
    with st.sidebar:
        st.markdown("<h2 style='font-weight:bold;text-align: center; color:white;'>Statistics and Learning Models</h2>", unsafe_allow_html=True) 
        with st.expander("Models", expanded=True):
            selected = option_menu(
            menu_icon="\u200B",
            menu_title=None,
            options=["KNN Model", "K-Means Clustering", "Hypothesis Testing","Time Forecasting"],
            
            default_index=0,
            styles={
                "container": {"background-color": "black", "padding": "0px"},
                "icon": {"color": "white", "font-size": "18px"},
                "nav-link": {"color": "white", "font-size": "16px", "font-weight": "bold", "padding": "5px 10px"},
                "nav-link-selected": {
                    "background-color": "#1a1c29",
                    "color": "white",
                    "border-radius": "10px",
                    "border-left": "4px solid purple",
                    "padding": "5px 10px",
                },
            }
        )

    st.sidebar.subheader(' ', divider='violet')

    if "df_think" not in st.session_state:
        st.warning("⚠️ No data available! Please upload a file in the main page.")
        return

    df = st.session_state["df_think"]  # Always retrieve latest df

    # Reset date_cols if a new file is uploaded
    if "previous_file" not in st.session_state:
        st.session_state["previous_file"] = None  # Store the previous filename

    if uploaded_file and uploaded_file.name != st.session_state["previous_file"]:
        st.session_state["date_cols"] = []  # Clear old date columns
        st.session_state["previous_file"] = uploaded_file.name  # Update previous file


    # Ensure date_cols persists
    if "date_cols" not in st.session_state:
        st.session_state["date_cols"] = []


    
    if not st.session_state["date_cols"]:  # Only detect date columns if empty
        date_cols = []
        for col in df.columns:
            if df[col].dtype == 'object':  # Only check object/text columns
                converted = pd.to_datetime(df[col], errors='coerce')
                valid_ratio = converted.notna().sum() / len(df)
                if valid_ratio >= 0.1:
                    df[col] = converted  # Convert the column to datetime
                    date_cols.append(col)
        st.session_state["date_cols"] = date_cols  # Store detected dates


    date_cols = st.session_state["date_cols"] 
                            
        
    if selected == "KNN Model":
        knn(st.session_state["df_think"],st.session_state["date_cols"])

    elif selected == "K-Means Clustering":
        km(st.session_state["df_think"])

    elif selected == "Hypothesis Testing":
        hypo(st.session_state["df_think"])

    elif selected == "Time Forecasting":
        times(st.session_state["df_think"],st.session_state["date_cols"])
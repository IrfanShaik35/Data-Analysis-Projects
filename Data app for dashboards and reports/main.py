import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import hashlib
from home import home
from thinkgrid import think
from dashboard import dash
from data_report import report
from pdf import pdf



st.set_page_config(page_title="Dashly", layout="wide")

# Navigation Menu
selected = option_menu(
    menu_title=None,
    options=['Home', 'ThinkGrid', 'Dashboards', 'Data Reports'],
    icons=['house-door-fill', 'lightbulb-fill', 'bar-chart-fill', 'clipboard-data-fill'],
    orientation="horizontal",
    styles={
        "container": {"background-color": "black", "padding": "0px"},
        "icon": {"color": "white", "font-size": "18px"},
        "nav-link": {"color": "white", "font-size": "18px", "font-weight": "bold", "padding": "2px 10px", "margin": "0px 2px"},
        "nav-link-selected": {
            "background-color": "black",
            "color": "white",
            "border-radius": "10px",
            "border-bottom": "4px solid purple",
            "padding": "2px 5px",
        },
    }
)

# ---------------------------------- HOME PAGE ---------------------------------- #
if selected == "Home":

    st.markdown(f"""
    <style>
        body {{ background-color: #0f111a; color: white; font-family: Arial, sans-serif; }}
        .hero-section {{ text-align: center; margin-top: 40px; color: white; }}
        .hero-section h1 {{ font-size: 80px; font-weight: bold; }}
        .hero-section span {{ color: #a855f7; }}
        .hero-section p {{ font-size: 18px; color: white; }}
        .container {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 50px; padding: 40px; }}
        .box {{ background-color: #1a1c29; padding: 40px; border-radius: 10px; width: 100%; min-height:500px; text-align: center; }}
    </style>

    <div class="hero-section">
        <h1>Data App For Reports<br> and <span>Dashboards</span></h1>
        <p>Data Will Talk To You If You're Willing To Listen.</p>
    </div><br><br>      
    """, unsafe_allow_html=True)

    home() 





# ---------------------------------- THINKGRID ---------------------------------- #
elif selected == "ThinkGrid":
    st.markdown("""
    <style>
        body { background-color: #0f111a; color: white; font-family: Arial, sans-serif; }
        .hero-section { text-align: center; margin-top: 40px; color: white; }
        .hero-section h1 { font-size: 65px; font-weight: bold; }
        .hero-section span { color: #a855f7; }
        .hero-section p { font-size: 20px; color: white; }
    </style>

    <div class="hero-section">
        <h1>&ensp;Data Driven <span> Chronicles</span></h1>
        <p>Trends and patterns are the whispers of data—ML listens, and the Data-Driven Chronicles speak.</p>
        <br>
        <br>
    </div>
    """, unsafe_allow_html=True)
    
    def get_file_hash(file):
        """Generate a hash for the uploaded file to track changes."""
        file.seek(0)  # Ensure we're reading from the start
        return hashlib.md5(file.read()).hexdigest()

    @st.cache_data
    def load_dataset(file):
        """Load dataset from a CSV or Excel file."""
            
        file.seek(0) 
        if "uploaded_file_name" in st.session_state and st.session_state["uploaded_file_name"] == file.name:
            return st.session_state["df"] 
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None

    if "uploaded_file_think" not in st.session_state:
        st.session_state["uploaded_file_think"] = None
        st.session_state["df_think"] = None
        st.session_state["file_hash_think"] = None
        st.session_state["think_actions"] = {} 

    uploaded_file_think = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"],key="think_uploader")

    if uploaded_file_think:
        # Store the uploaded file in session state
        st.session_state["uploaded_file_think"] = uploaded_file_think
        file_hash_think = get_file_hash(uploaded_file_think)

        if st.session_state["file_hash_think"] != file_hash_think:
            df_think = load_dataset(uploaded_file_think)
            st.session_state["df_think"] = df_think
            st.session_state["file_hash_think"] = file_hash_think
            st.session_state["think_actions"] = {}

    if uploaded_file_think is None and st.session_state["uploaded_file_think"] is not None:
        st.session_state["uploaded_file_think"] = None
        st.session_state["df_think"] = None
        st.session_state["file_hash_think"] = None
        st.session_state["dashboard_think"] = {}
        st.rerun()

    
    if st.session_state["df_think"] is not None:
    
        think(st.session_state["df_think"], st.session_state["uploaded_file_think"])


        


# ---------------------------------- DASHBOARDS PAGE ---------------------------------- #
if selected == "Dashboards":
    st.markdown("""
    <style>
        body { background-color: #0f111a; color: white; font-family: Arial, sans-serif; }
        .hero-section { text-align: center; margin-top: 40px; color: white; }
        .hero-section h1 { font-size: 60px; font-weight: bold; }
        .hero-section span { color: #a855f7; }
        .hero-section p { font-size: 20px; color: white; }
    </style>

    <div class="hero-section">
        <h1>Insights at a glance,<span> decisions in an instant</span></h1>
        <p>Data tells the story—your dashboard brings it to life</p>
        <br>
        <br>
    </div>
    """, unsafe_allow_html=True)

    

    def get_file_hash(file):
        """Generate a hash for the uploaded file to track changes."""
        file.seek(0)  # Ensure we're reading from the start
        return hashlib.md5(file.read()).hexdigest()

    @st.cache_data
    def load_dataset(file):
        """Load dataset from a CSV or Excel file."""
            
        file.seek(0) 
        if "uploaded_file_name" in st.session_state and st.session_state["uploaded_file_name"] == file.name:
            return st.session_state["df"] 
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None

    if "uploaded_file_dash" not in st.session_state:
        st.session_state["uploaded_file_dash"] = None
        st.session_state["df_dash"] = None
        st.session_state["file_hash_dash"] = None
        st.session_state["dashboard_actions"] = {} 

    uploaded_file_dash = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"],key="dashboard_uploader")

    if uploaded_file_dash:
        # Store the uploaded file in session state
        st.session_state["uploaded_file_dash"] = uploaded_file_dash
        file_hash_dash = get_file_hash(uploaded_file_dash)

        if st.session_state["file_hash_dash"] != file_hash_dash:
            df_dash = load_dataset(uploaded_file_dash)
            st.session_state["df_dash"] = df_dash
            st.session_state["file_hash_dash"] = file_hash_dash
            st.session_state["dashboard_actions"] = {}

    if uploaded_file_dash is None and st.session_state["uploaded_file_dash"] is not None:
        st.session_state["uploaded_file_dash"] = None
        st.session_state["df_dash"] = None
        st.session_state["file_hash_dash"] = None
        st.session_state["dashboard_actions"] = {}
        st.rerun()

    # Display data if available
    if st.session_state["df_dash"] is not None:
    
        dash(st.session_state["df_dash"], st.session_state["uploaded_file_dash"])

            
            
# ---------------------------------- REPORTS PAGE ---------------------------------- #
elif selected == "Data Reports":
    st.markdown("""
    <style>
        body { background-color: #0f111a; color: white; font-family: Arial, sans-serif; }
        .hero-section { text-align: center; margin-top: 40px; color: white; }
        .hero-section h1 { font-size: 60px; font-weight: bold; }
        .hero-section span { color: #a855f7; }
        .hero-section p { font-size: 20px; color: white; }
    </style>

    <div class="hero-section">
        <h1>Turn data into<span> direction</span></h1>
        <p>Unlock hidden insights, make informed decisions, transform numbers into knowledge, insights into impact</p>
        <br>
        <br>
    </div>
    """, unsafe_allow_html=True)

    def get_file_hash(file):
        """Generate a hash for the uploaded file to track changes."""
        file.seek(0)  # Ensure we're reading from the start
        return hashlib.md5(file.read()).hexdigest()


    @st.cache_data
    def load_dataset(file):
        """Load dataset from a CSV or Excel file."""
            
        file.seek(0) 
        if "uploaded_file_name" in st.session_state and st.session_state["uploaded_file_name"] == file.name:
            return st.session_state["df"] 
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None

    if "uploaded_file_report" not in st.session_state:
        st.session_state["uploaded_file_report"] = None
        st.session_state["df_report"] = None
        st.session_state["file_hash_report"] = None
        st.session_state["report_actions"] = {} 

    uploaded_file_report = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xls", "xlsx"],key="reports_uploader")

    if uploaded_file_report:
        file_hash_report = get_file_hash(uploaded_file_report)
        st.session_state["uploaded_file_report"] = uploaded_file_report

        if st.session_state["file_hash_report"] != file_hash_report:
            df_report = load_dataset(uploaded_file_report)
            st.session_state["df_report"] = df_report
            st.session_state["file_hash_report"] = file_hash_report
            st.session_state["report_actions"] = {}

    if uploaded_file_report is None and st.session_state["uploaded_file_report"] is not None:
        st.session_state["uploaded_file_report"] = None
        st.session_state["df_report"] = None
        st.session_state["file_hash_report"] = None
        st.session_state["report_actions"] = {}
        st.rerun()

    # Display data if available
    if st.session_state["df_report"] is not None:
    
        report(st.session_state["df_report"])
        pdf( st.session_state["uploaded_file_report"],st.session_state["df_report"])




        
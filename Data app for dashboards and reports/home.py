import streamlit as st
import time
from PIL import Image
import requests
from io import BytesIO

def home():
    
    
    col1, col2 = st.columns([1, 2])  # Creates two equal columns

    with col1:
        st.markdown("""
    <style>
        .report-box {
            text-align: left;
            background-color: #1a1c29;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #a855f7;
            max-width: 800px;
            margin: 0 auto;
        }
        .report-box h2 {
            margin-bottom: 10px;
            text-align: center;
        }
        .report-box p {
            font-size: 18px;
            line-height: 1.6;
            text-align: justify;
            hyphens: auto;
            word-spacing: -0.5px;
        }
    </style>

    <div class="report-box">
        <h2><b>Data with Interactive Intelligence</b></h2><br>   
        <p>An intuitive interface for selecting different statistical and machine learning models. Users can perform K-Nearest Neighbors (KNN) classification or regression, K-Means Clustering for pattern detection, and Hypothesis Testing for statistical comparisons.</p>
        <p> The dashboard also presents key dataset metrics and visualizations, making complex analyses more accessible. With real-time updates and interactive components, it serves as a powerful tool for exploratory data analysis (EDA) and data-driven decision-making.</P> 
        

    </div>
""", unsafe_allow_html=True)
        
    with col2:
        st.write(" ")
        st.write(" ")
        st.write(" ")
        image_urls = ["https://i.ibb.co/hJzmkjJ1/Screenshot-2025-03-18-135717.png",
"https://i.ibb.co/4RK03rw7/Screenshot-2025-03-18-135938.png",
"https://i.ibb.co/LhnwvSw8/Screenshot-2025-03-18-140108.png",
"https://i.ibb.co/YFggPq42/Screenshot-2025-03-18-140152.png",
"https://i.ibb.co/TMsm0Trq/Screenshot-2025-03-18-140241.png"
        ]

        # Preload images in session state (only once)
        if "preloaded_images" not in st.session_state:
            st.session_state.preloaded_images = []
            for url in image_urls:
                response = requests.get(url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    st.session_state.preloaded_images.append(img)

        # Initialize image index
        if "img_index1" not in st.session_state:
            st.session_state.img_index1 = 0

        # Display the preloaded image
        img_placeholder = st.empty()

        # **Simulating a fade transition using time delay**
        for opacity in range(0, 11):  # Gradually increase visibility
            alpha = opacity / 10  # Convert to 0.0 - 1.0 range
            img_placeholder.markdown(f"""
        <style>
        .fade-img {{
            opacity: {alpha};
            transition: opacity 0.5s ease-in-out;
        }}
        </style>
        <img src="{image_urls[st.session_state.img_index1]}" class="fade-img" width="100%">
        """,
        unsafe_allow_html=True,
        )
        time.sleep(0.05)  # Small delay to create the fade effect

        # Button to cycle images
        col0,col1, col2, col3 = st.columns([0.5,1.1, 8, 1])

        with col1:
            st.write(" ")
            if st.button("← ",key="prev_btn_1"):
                st.session_state.img_index1 = (st.session_state.img_index1 - 1) % len(image_urls)
                st.rerun()  

        with col3:
            st.write(" ")
            if st.button("→",key="nex_btn_1"):
                st.session_state.img_index1 = (st.session_state.img_index1 + 1) % len(image_urls)
                st.rerun()  


    st.subheader(" ")
    st.write(" ")
    # Section 2: AI Image Generator
    col3, col4 = st.columns([2, 1])

    with col3:
        
        image_urls = ["https://i.ibb.co/XhGpctR/Screenshot-2025-02-26-222334.png",
        "https://i.ibb.co/sT4QY7x/Screenshot-2025-02-26-222442.png",
        "https://i.ibb.co/v64MHPKb/Screenshot-2025-02-26-222521.png",
        "https://i.ibb.co/Xfg4hcR2/Screenshot-2025-02-26-222631.png"
        ]

        # Preload images in session state (only once)
        if "preloaded_images" not in st.session_state:
            st.session_state.preloaded_images = []
            for url in image_urls:
                response = requests.get(url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    st.session_state.preloaded_images.append(img)

        # Initialize image index
        if "img_index2" not in st.session_state:
            st.session_state.img_index2 = 0

        # Display the preloaded image
        img_placeholder = st.empty()

        # **Simulating a fade transition using time delay**
        for opacity in range(0, 11):  # Gradually increase visibility
            alpha = opacity / 10  # Convert to 0.0 - 1.0 range
            img_placeholder.markdown(f"""
        <style>
        .fade-img {{
            opacity: {alpha};
            transition: opacity 0.5s ease-in-out;
        }}
        </style>
        <img src="{image_urls[st.session_state.img_index2]}" class="fade-img" width="100%">
        """,
        unsafe_allow_html=True,
        )
        time.sleep(0.05)  # Small delay to create the fade effect

        # Button to cycle images
        col0,col1, col2, col3 = st.columns([0.5,1.1, 8, 1])

        with col1:
            st.write(" ")
            if st.button("← ",key="prev_btn_2"):
                st.session_state.img_index2 = (st.session_state.img_index2 - 1) % len(image_urls)
                st.rerun()  

        with col3:
            st.write(" ")
            if st.button("→",key="nxt_btn_2"):
                st.session_state.img_index2 = (st.session_state.img_index2 + 1) % len(image_urls)
                st.rerun()  


    with col4:
        st.markdown("""
    <style>
        .report-box {
            text-align: left;
            background-color: #1a1c29;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #a855f7;
            max-width: 800px;
            margin: 0 auto;
        }
        .report-box h2 {
            margin-bottom: 10px;
            text-align: center;
        }
        .report-box p {
            font-size: 18px;
            line-height: 1.6;
            text-align: justify;
            hyphens: auto;
            word-spacing: -0.5px;
        }
    </style>

    <div class="report-box">
        <h2><b>Interactive Data Board</b></h2><br>
        <p>Interactive dashboard designed to help users explore and visualize data dynamically. It can also filter the data making it easier to focus on specific data points.In addition to filtering,
         it provides key dataset metrics to summarize data.</p>
        <p>The dashboard supports various types of interactive visualizations, including scatter plots, bar charts, line charts, area charts, box plots, and pie charts. This dashboard provides an efficient and intuitive way to explore, filter, and visualize datasets, making it a valuable tool for exploratory data analysis (EDA) and business intelligence reporting.</p>
        
    </div>
""", unsafe_allow_html=True)

    st.subheader(" ")
    col5, col6 = st.columns([1, 2])   

    with col5:
        st.markdown("""
    <style>
        .report-box {
            text-align: left;
            background-color: #1a1c29;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #a855f7;
            max-width: 800px;
            margin: 0 auto;
        }
        .report-box h2 {
            margin-bottom: 10px;
            text-align: center;
        }
        .report-box p {
            font-size: 18px;
            line-height: 1.6;
            text-align: justify;
            hyphens: auto;
            word-spacing: -0.5px;
        }
    </style>

    <div class="report-box">
        <h2><b>Reporting Interface</b></h2><br>
        <p>Provides a structured and interactive analysis of the dataset, allowing to explore key insights effectively.
        starting with a Dataset Overview to preview data, examine columns, detect missing values, and identify duplicates.</p>
        <p> Variable Analysis provides summaries and visualizations for individual columns, 
        while Correlation Analysis computes relationships using tables and heatmaps. Interaction Analysis explores feature relationships through scatter plots, revealing patterns and dependencies within the dataset.</p>
        
    </div>
""", unsafe_allow_html=True)

    
    with col6:
        image_urls = ["https://i.ibb.co/tPqFrjxP/overview.png",
        "https://i.ibb.co/9m5jqPTy/variable.png",
        "https://i.ibb.co/1JsXYXdK/Screenshot-2025-02-23-155627.png",
        "https://i.ibb.co/Fk94Kx6X/interaction.png"
        ]

        # Preload images in session state (only once)
        if "preloaded_images" not in st.session_state:
            st.session_state.preloaded_images = []
            for url in image_urls:
                response = requests.get(url)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    st.session_state.preloaded_images.append(img)

        # Initialize image index
        if "img_index3" not in st.session_state:
            st.session_state.img_index3 = 0

        # Display the preloaded image
        img_placeholder = st.empty()

        # **Simulating a fade transition using time delay**
        for opacity in range(0, 11):  # Gradually increase visibility
            alpha = opacity / 10  # Convert to 0.0 - 1.0 range
            img_placeholder.markdown(f"""
        <style>
        .fade-img {{
            opacity: {alpha};
            transition: opacity 0.5s ease-in-out;
        }}
        </style>
        <img src="{image_urls[st.session_state.img_index3]}" class="fade-img" width="100%">
        """,
        unsafe_allow_html=True,
        )
        time.sleep(0.05)  # Small delay to create the fade effect

        # Button to cycle images
        col0,col1, col2, col3 = st.columns([0.5,1.1, 8, 1])

        with col1:
            st.write(" ")
            if st.button("← ",key="prev_btn_3"):
                st.session_state.img_index3 = (st.session_state.img_index3 - 1) % len(image_urls)
                st.rerun()  

        with col3:
            st.write(" ")
            if st.button("→",key="nxt_btn_3"):
                st.session_state.img_index3 = (st.session_state.img_index3 + 1) % len(image_urls)
                st.rerun()  

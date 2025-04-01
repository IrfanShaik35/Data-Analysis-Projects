import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import plotly.express as px


def km(df):
    st.write(" ")
   
    st.markdown("<h1 style='text-align: center; '>K-MEAN CLUSTERING ALGORITHM</h1>", unsafe_allow_html=True)

    st.write(" ")
    st.write(" ")
    with st.expander("Show Data overview"):
        st.subheader("Data preview")
        st.dataframe(df, use_container_width=True)
    st.write(" ")
    # Auto-detect column types
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    st.warning("⚠️ K-Means clustering works best with only numerical data")
    if not numeric_cols:
        st.error("⚠️ No numeric columns found! Please upload a dataset with numeric features.")
        st.stop()


   
    st.sidebar.header("Feature Selection")
    all_features = list(set(numeric_cols)) 
    feature_cols = st.sidebar.multiselect("Select Features for Clustering", options=[col for col in all_features  if pd.notna(col)])
    
    if len(feature_cols) < 2:
        st.error("⚠️ Please select at least two numeric features.")
        st.stop()
        
    df = df.dropna(subset=feature_cols).reset_index(drop=True)
    
    # Prepare data
    X = df[feature_cols]
    
    # Select number of clusters dynamically
    n_clusters = st.sidebar.slider("Select Number of Clusters", min_value=2, max_value=10, value=3)
    
    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df["Cluster_Label"] = kmeans.fit_predict(X)
    
    # Display segmented dataset
    st.subheader("Segmented Dataset")
    st.write(" ")
    st.dataframe(df.sort_values(by="Cluster_Label"), use_container_width=True)
    
    # Analytics
    st.subheader("Cluster Analytics")
    analytics_df = df.groupby("Cluster_Label").agg(
        cluster_size=("Cluster_Label", "count"),
        avg_features1=(feature_cols[0], "mean"),
        avg_feature2=(feature_cols[1], "mean")
    ).reset_index()
    st.dataframe(analytics_df, use_container_width=True)
    st.write(" ")
    # Visualization
    st.subheader("Cluster Visualization")
    fig = px.scatter(df, x=feature_cols[0], y=feature_cols[1], color=df["Cluster_Label"].astype(str),
                      labels={"color": "Cluster"})
    st.plotly_chart(fig)
    
    # Prediction form
    with st.sidebar.form("prediction_form"):
        st.subheader("Predict Cluster for New Data")
        new_data = []

        for col in feature_cols:
            
            new_data.append(st.number_input(f"{col}", value=float(df[col].mean())))

        submit_button = st.form_submit_button("Predict")
        if submit_button:
            new_cluster = kmeans.predict([new_data])[0]
            st.sidebar.success(f"Predicted Cluster: {new_cluster}")


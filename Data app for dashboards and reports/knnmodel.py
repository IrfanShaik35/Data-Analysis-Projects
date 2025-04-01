import streamlit as st
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import accuracy_score, r2_score, mean_absolute_error
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from numerize import numerize
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


def knn(df,date_cols):
    st.write(" ")
    st.markdown("<h1 style='text-align: center; '>K-NEAREST NEIGHBORS ALGORITHM: PREDICTION & TRENDS</h1>", unsafe_allow_html=True)

    

    st.write(" ")
    st.write(" ")
    with st.expander("Show Data overview"):
        st.subheader("Data preview")
        st.dataframe(df, use_container_width=True)
    st.write(" ")
    # Auto-detect column types
    categorical_cols = [col for col in df.select_dtypes(include=['object', 'category']).columns if col not in date_cols]
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    
    if not numeric_cols:
        st.error("⚠️ No numeric columns found! Please upload a dataset with numeric features.")
        st.stop()
    for date_col in date_cols:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')  # Convert to datetime
        df[date_col] = df[date_col].fillna(pd.Timestamp("1970-01-01")) 

        df[date_col + "_timestamp"] = df[date_col].map(pd.Timestamp.timestamp)  # Convert to numeric format

    date_timestamp_cols = [col + "_timestamp" for col in date_cols]
    # Sidebar: Select Features & Target
    st.sidebar.header("Feature Selection")
    all_features = list(set(numeric_cols + categorical_cols + date_timestamp_cols))  
    target_col = st.sidebar.selectbox("Select Target Column", options=[col for col in all_features  if pd.notna(col)])
    feature_cols = st.sidebar.multiselect("Select Feature Columns", options=[col for col in all_features  if pd.notna(col)])


    if not target_col or target_col == "None":
        st.error("⚠️ Please select a target column.")
        st.stop()
    
    if len(feature_cols) < 1:
        st.error("⚠️ Please select at least one feature column.")
        st.stop()
    
    
    if df[target_col].dtype in ["int64", "float64"]:  # Regression (Numerical Target)
        if df[target_col].isna().sum() > 0:
            
            df[target_col].fillna(df[target_col].mean(), inplace=True)  # Mean imputation

    else:  # Classification (Categorical Target)
        if df[target_col].isna().sum() > 0:
            df = df.dropna(subset=[target_col])

    
    num_features = [col for col in feature_cols if col in numeric_cols]
    cat_features = [col for col in feature_cols if col in categorical_cols]

    # Pipeline: Preprocessing for mixed features
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),  # Handle missing values
        ("scaler", StandardScaler())  # Scale numerical features
    ])

    cat_pipeline = Pipeline([
        ("encoder", OneHotEncoder(handle_unknown="ignore"))  # Encode categorical features
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipeline, num_features),
        ("cat", cat_pipeline, cat_features)
    ])

    # Prepare X and y
    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

     # Apply preprocessing
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)


    # Train KNN model
    if df[target_col].dtype in ["int64", "float64"]:  # Regression (Numerical Target)
        param_grid = {'n_neighbors': [3, 5, 7, 10, 15]}
        knn = GridSearchCV(KNeighborsRegressor(), param_grid, cv=5)
        knn.fit(X_train_transformed, y_train)
        knn = knn.best_estimator_ 
    else:  # Classification (Categorical Target)
        knn = KNeighborsClassifier(n_neighbors=5)

        knn.fit(X_train_transformed, y_train)

    
    # Predict
    df["Predicted_" + target_col] = knn.predict(preprocessor.transform(X))
    
    y_pred = knn.predict(X_test_transformed)

    # Show basic analytics
    st.subheader("Grouped statistical analysis")
    st.write(" ")

    # Ensure feature_cols[0] is numeric before using it
    col1,col2,col3=st.columns(3)
    with col1:
        feature_cols1 = st.selectbox("Choose selected Feature Columns", options=[col for col in feature_cols if pd.notna(col)])
    f = feature_cols.index(feature_cols1)
    selected_feature = feature_cols[f]
    st.write(" ")
    if selected_feature in numeric_cols:
        analytics_df = df.groupby(target_col).agg(
        count=(target_col, 'count'),
        max_value=(selected_feature, 'max'),
        min_value=(selected_feature, 'min'),
        range_value=(selected_feature, lambda x: x.max() - x.min()),
        std_dev=(selected_feature, 'std')
    ).reset_index()
        
    else:
        analytics_df = df.groupby(target_col).agg(
        count=(target_col, 'count')
    ).reset_index()
        analytics_df["max_value"] = "N/A"
        analytics_df["min_value"] = "N/A"
        analytics_df["range_value"] = "N/A"
        analytics_df["std_dev"] = "N/A"

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("Unique Categories", df[target_col].nunique())
    if feature_cols and selected_feature in df.columns and selected_feature in numeric_cols:
        max_value = df[selected_feature].max()
        min_value = df[selected_feature].min()
    else:
        category_counts = df[selected_feature].dropna().value_counts()
        max_value = f"{category_counts.idxmax()} ({category_counts.max()})" if not category_counts.empty else "No Data"
        min_value = f"{category_counts.idxmin()} ({category_counts.min()})" if not category_counts.empty else "No Data"

    col2.metric("Max Value", max_value)
    col3.metric("Min Value", min_value)
    if feature_cols and selected_feature in df.columns:
        mode_values = df[selected_feature].dropna().mode()
        range_value = mode_values[0] if not mode_values.empty else "No Mode Found"
    else:
        range_value = "Column Not Found"

    with col4: st.metric("Mode Value", range_value)


    with col5: st.metric("Total Records", numerize.numerize(df.shape[0]))

    style_metric_cards(
        background_color="#1a1c29",
        border_left_color="#a855f7",
        border_color="#a855f7",
        box_shadow="#a855f7"
        )
    # Show analytics table
    st.dataframe(analytics_df, use_container_width=True)
    st.write(" ")

    # Sidebar: Prediction for new record
    with st.sidebar.form("prediction_form"):
        st.subheader("Enter New Data for Prediction")
        new_data = []
        for col in feature_cols:
            if col in numeric_cols:
                new_data.append(st.number_input(f"{col}", value=float(df[col].mean())))
            elif col in categorical_cols:
                df[col] = df[col].astype(str)  # Ensure it's properly treated as categorical
                unique_values = df[col].dropna().unique().tolist()
                
                if not unique_values:  # Prevent empty selectbox issue
                    unique_values = ["No Data Available"]
    
                new_data.append(st.selectbox(f"{col}", options=unique_values, index=0))
            else:
                new_data.append(None)

        submit_button = st.form_submit_button("Predict")

        if submit_button:
            new_data_df = pd.DataFrame([new_data], columns=feature_cols)

            # Apply preprocessing before prediction
            new_data_transformed = preprocessor.transform(new_data_df)

            # Predict
            new_prediction = knn.predict(new_data_transformed)
            st.success(f"Predicted {target_col}: {new_prediction[0]}")
    


    if df[target_col].dtype in ["int64", "float64"]:  # Regression (Numerical Target)
        model_score = r2_score(y_test, y_pred)  # Use R² score for regression
        st.subheader("Model Performance (Regression)")
        st.success(f"R² Score: {model_score:.2f}")
        st.markdown(f"""
    <div style="font-size:18px;">
        The dataset contains numerical values, meaning the model predicts continuous outputs rather than categories.
        The model learns from patterns in the data by analyzing feature relationships and it represent the model’s best estimate for each input based on past trends, helping in forecasting future values.<br><br>
        ● <b>R² Score:</b> {model_score * 100:.2f}%&ensp;(Higher is better, indicates how well the model explains variance).<br>
        ● <b>Mean Absolute Error:</b> {mean_absolute_error(y_test, y_pred):.2f} &ensp;(Lower is better, shows avearge prediction error).<br><br>
    </div>
    """, 
    unsafe_allow_html=True)


    else:  # Classification (Categorical Target)
        model_score = accuracy_score(y_test, y_pred)  # Use accuracy for classification
        st.subheader("Model Accuracy (Classification)")
        st.success(f"Accuracy: {model_score:.2f}")
        st.write(" ")
        st.markdown(f"""
    <div style="font-size:18px;">
        The dataset contains categorical values, meaning the model classifies data into different categories. 
        The model learns from patterns in the data, identifying characteristics that define each class.
        <b>Predicted Value:</b> <b>{model_score * 100:.2f}%</b>.
        The model determines which category each new record belongs to, helping in decision-making and identifying key trends. 
        A higher accuracy score indicates better model performance.<br><br>
    </div>
    """, 
    unsafe_allow_html=True)
        
        predicted_counts = df["Predicted_" + target_col].value_counts(normalize=True) * 100
        total_counts = df["Predicted_" + target_col].value_counts()

        if len(predicted_counts) >= 3:
            top_segments = predicted_counts.index.tolist()[:3]
            top_percentages = predicted_counts.values[:3]
            top_totals = total_counts.values[:3]

            st.markdown(f"""
            <div style="font-size:18px;">
                ●  <b> Most High-Frequency Predicted Category:</b> <span style="color:#2E86C1;">{top_segments[0]}</span> 
                  → {top_percentages[0]:.2f}% ({top_totals[0]} occurrences) <br>
                ●  <b>Second Most Frequent:</b> <span style="color:#28B463;">{top_segments[1]}</span> 
                  → {top_percentages[1]:.2f}% ({top_totals[1]} occurrences) <br>
                ●  <b>Third Most Frequent:</b> <span style="color:#F39C12;">{top_segments[2]}</span> 
                  → {top_percentages[2]:.2f}% ({top_totals[2]} occurrences) <br>
            </div>
            """, unsafe_allow_html=True)


    st.write(" ")
    st.write(" ")
    # Show dataset with predictions
    st.subheader("Dataset with Predictions")
    st.write(" ")
    selected_columns = st.multiselect("Filter Columns", df.columns.tolist(), default=df.columns.tolist())
    st.dataframe(df[selected_columns], use_container_width=True)

   
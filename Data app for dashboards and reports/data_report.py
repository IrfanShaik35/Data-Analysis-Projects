import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt  
import io  
import re


def report(df):
            
           
            st.markdown("""
                <style>
                    body { background-color: #0f111a; color: white; font-family: Arial, sans-serif; font-size:16px; }
                    .container { display: flex; gap: 0px; padding: 40px; }
                    .box { background-color: #1a1c29; border-radius: 10px;margin-bottom: 20px;width: 100%; }
                    h1, h2 { color: #a855f7;text-align: center;  }
                    
                </style>
            """, unsafe_allow_html=True)
            # ------------------------ Dataset Overview ------------------------
            st.markdown("""
                <div class="container">
                    <div class="box">
                        <h1>&nbsp;Overview</h1>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            st.write("### Dataset Preview")
            
            data_height = min(35 * len(df), 400) if not df.empty else 100
            st.dataframe(df, width=1500, height=data_height)

            
            st.write(" ")
            col1, col2 = st.columns([1,2])  # Creating two columns

            # Left Column: Dataset Information
            with col1:
                st.write("### Dataset Information")
                if "date_cols" not in st.session_state:
                    st.session_state["date_cols"] = []

                
                date_cols = []
                for col in df.columns:
                    if df[col].dtype == 'object':  # Only check object/text columns
                        converted = pd.to_datetime(df[col], errors='coerce')
                        valid_ratio = converted.notna().sum() / len(df)
                        if valid_ratio >= 0.1:
                            df[col] = converted  # Convert the column to datetime
                            date_cols.append(col)

                # Merge previous and new date columns (avoids loss of previously detected dates)
                st.session_state["date_cols"] = list(set(st.session_state["date_cols"]) | set(date_cols))

    
                # Capture dataset info
                buffer = io.StringIO()
                df.info(buf=buffer)  
                info_str = buffer.getvalue().split("\n")  
                columns_info = []
    
                for line in info_str[5:-2]:  # Extract relevant column details
                    parts = line.split()
                    if len(parts) >= 5:
                        columns_info.append({
                        "Column Name": parts[1],  
                        "Non-Null Count": parts[2] + " " + parts[3],  
                        "Data Type": parts[4]  
                    })

                info_df = pd.DataFrame(columns_info)
               
                info_height = min(42 * len(info_df), 400) if not info_df.empty else 100
                st.dataframe(info_df, width=400, height=info_height)

            # Right Column: Summary Statistics
            with col2:
                st.write("### Summary Statistics")

                
                # Summary Statistics
                summary = df.describe(include="all").T  # Includes categorical & numerical columns
                numeric_df = df.select_dtypes(include=['number'])  # Numeric columns only

                # Compute skewness and kurtosis only for numeric columns
                summary["Skewness"] = numeric_df.skew()
                summary["Kurtosis"] = numeric_df.kurtosis()

                
                # Handle datetime columns separately
                datetime_cols = df.select_dtypes(include=['datetime64'])
                if not datetime_cols.empty:
                    summary.loc[datetime_cols.columns, ["mean", "min", "max"]] = datetime_cols.agg(['mean', 'min', 'max']).T

                # Format datetime values properly
                summary = summary.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) else x)

                # Fill NaN values with "-"
                summary = summary.fillna("-")  

                # Display in Streamlit
                summary_height = min(42 * len(summary), 400) if not summary.empty else 100
                st.dataframe(summary, width=900, height=summary_height)

            # Count duplicate rows
            duplicate_count = df.duplicated().sum()

            if duplicate_count > 0:
                st.write(" ")
                st.write("### Duplicate Rows")
                df_duplicates = df[df.duplicated(keep=False)].copy()
    
                # Display the duplicate rows
                st.dataframe(df_duplicates,width=1500, height=400)  # Display all duplicate rows
            else:
                st.write(f"**Duplicate Rows:** {duplicate_count}")


            # ------------------------ Variables Analysis ------------------------
            st.markdown("""
                <div class="container">
                    <div class="box">
                        <h1>Variables Analysis</h1>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            sns.set_theme(style="dark")
            
            valid_date_cols = [col for col in st.session_state["date_cols"] if col in df.columns]
    
            # Selecting numerical and categorical columns
            numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

            
            all_columns = numerical_cols + categorical_cols + valid_date_cols
            
            all_columns.insert(0, "All Columns")

            col1, col2 = st.columns([1, 3]) 
            with col1:
                selected_col = st.selectbox("Select Column", all_columns)

            @st.cache_data
            def display_column_analysis(selected_col):
                if selected_col in date_cols:
                    col_type = "Date"
                elif selected_col in numerical_cols:
                    col_type = "Numerical"
                else:
                    col_type = "Categorical"

 
                col_type = "Numerical" if selected_col in numerical_cols else ("Date" if selected_col in date_cols else "Categorical")
                st.markdown(f"<h4 style='color: white;'>{selected_col} ({col_type})</h4>", unsafe_allow_html=True)

                background_color = "#000000"  # Adjust this based on Streamlit's theme
                text_color = "white"  

                if selected_col in numerical_cols:
                    # Creating three columns
                    col_summary, col_quality, col_chart = st.columns([1,1,3])

                    # Column 1: Summary Statistics
                    with col_summary:
                
                        summary = df[selected_col].describe().T
                        summary["Skewness"] = df[selected_col].skew()
                        summary["Kurtosis"] = df[selected_col].kurt()
                        st.write("##### Summary")
                        st.dataframe(summary, width=300, height=390)

                    # Column 2: Data Quality Summary
                    with col_quality:
                
                        missing_values = df[selected_col].isnull().sum()
                        missing_percentage = (missing_values / len(df)) * 100
                        duplicate_values = df.duplicated(subset=[selected_col]).sum()

                        summary_df = pd.DataFrame({
                        "Metric": ["Missing Values", "Missing Value %", "Duplicate Values"],
                        "Count": [missing_values, f"{missing_percentage:.2f}%", duplicate_values]
                        })
                        
                        st.write("##### Data Quality")
                        st.dataframe(summary_df, width=250)

                    # Column 3: Histogram
                    with col_chart:
                        fig, ax = plt.subplots(figsize=(7,3))
                        fig.patch.set_facecolor(background_color)
                        ax.set_facecolor(background_color)
                        ax.spines["bottom"].set_color(text_color)
                        ax.spines["left"].set_color(text_color)
                        ax.tick_params(axis="x", colors=text_color)
                        ax.tick_params(axis="y", colors=text_color)
                        ax.title.set_color(text_color)
                        ax.xaxis.label.set_color(text_color)
                        ax.yaxis.label.set_color(text_color)
                        sns.histplot(df[selected_col].dropna(), bins=30, kde=True, color='#a855f7', ax=ax)
                        ax.set_title(f"Histogram for {selected_col}",fontsize=12)
                        ax.set_xlabel(selected_col,fontsize=10)
                        ax.set_ylabel("Frequency",fontsize=10)
                        ax.tick_params(axis='both', labelsize=8)
                        st.pyplot(fig)

                # Categorical Column Analysis
                elif selected_col in categorical_cols and selected_col not in date_cols:
                    col_summary, col_quality, col_chart = st.columns([1, 1, 3])

                    with col_summary:
                        st.write("##### Summary")
                        st.dataframe(df[selected_col].value_counts().reset_index(), width=300)


                    with col_quality:
                        unique_values = df[selected_col].nunique()
                        missing_values = df[selected_col].isnull().sum()
                        duplicate_values = df.duplicated(subset=[selected_col]).sum()

                        summary_df = pd.DataFrame({
                        "Metric": ["Unique Values", "Missing Values", "Missing Value %", "Duplicate Rows"],
                        "Count": [unique_values, missing_values, f"{(missing_values / len(df)) * 100:.2f}%", duplicate_values]
                        })

                        st.write("##### Data Quality")
                        st.dataframe(summary_df, width=300)

                    with col_chart:
                        fig, ax = plt.subplots(figsize=(7,3))
                        fig.patch.set_facecolor(background_color)
                        ax.set_facecolor(background_color)
                        ax.spines["bottom"].set_color(text_color)
                        ax.spines["left"].set_color(text_color)
                        ax.tick_params(axis="x", colors=text_color)
                        ax.tick_params(axis="y", colors=text_color)
                        ax.title.set_color(text_color)
                        ax.xaxis.label.set_color(text_color)
                        ax.yaxis.label.set_color(text_color)
                        if df[selected_col].dropna().nunique() > 10:
                            top_10_data = df[selected_col].value_counts().nlargest(10)
                            sns.histplot(top_10_data.dropna(), bins=30, kde=True, color='#a855f7', ax=ax)
                            ax.set_title(f"Histogram for {selected_col}",fontsize=12)
                            ax.set_xlabel("Count", fontsize=10)
                            ax.set_ylabel(selected_col, fontsize=10)
                            ax.tick_params(axis='both', labelsize=8)
                        else:
                            sns.histplot(df[selected_col].dropna(), bins=30, kde=True, color='#a855f7', ax=ax)
                            ax.set_title(f"Histogram for {selected_col}",fontsize=12)
                            ax.set_xlabel(selected_col, fontsize=10)
                            ax.set_ylabel("Count", fontsize=10)
                            ax.tick_params(axis='both', labelsize=8)
                        
                        st.pyplot(fig)

                elif selected_col in date_cols:
                    col_summary, col_chart = st.columns([2, 2.5])

                    with col_summary:
                        min_date = df[selected_col].min()
                        max_date = df[selected_col].max()
                        missing_values = df[selected_col].isnull().sum()
                        missing_percentage = (missing_values / len(df)) * 100
                        unique_values = df[selected_col].nunique()
                        duplicate_values = df.duplicated(subset=[selected_col]).sum()

                        summary_df = pd.DataFrame({
                        "Metric": ["Min Date", "Max Date", "Missing Values", "Missing Value %","Unique Values","Duplicate Values"],
                        "Value": [min_date, max_date, missing_values, f"{missing_percentage:.2f}%",unique_values,duplicate_values]
                        })
                        st.write("##### Summary")
                        st.dataframe(summary_df, width=400)
 
                    with col_chart:
                        df_sorted = df[[selected_col]].dropna().sort_values(by=selected_col)
                        df_sorted['Count'] = range(1, len(df_sorted) + 1)

                        fig, ax = plt.subplots(figsize=(6, 2))
                        fig.patch.set_facecolor(background_color)
                        ax.set_facecolor(background_color)
                        ax.spines["bottom"].set_color(text_color)
                        ax.spines["left"].set_color(text_color)
                        ax.tick_params(axis="x", colors=text_color)
                        ax.tick_params(axis="y", colors=text_color)
                        ax.title.set_color(text_color)
                        ax.xaxis.label.set_color(text_color)
                        ax.yaxis.label.set_color(text_color)
                        sns.histplot(df[selected_col].dropna(), bins=30, kde=True, color='#a855f7', ax=ax)
                        ax.set_title(f"Time Series Plot for {selected_col}", fontsize=12)
                        ax.set_xlabel("Date", fontsize=10)
                        ax.set_ylabel("Cumulative Count", fontsize=10)
                        ax.tick_params(axis='both', labelsize=8)
                        st.pyplot(fig)
    
     

            if selected_col == "All Columns":
                for col in all_columns[1:]:  # Excluding "All Columns" itself
        
                    display_column_analysis(col)

            elif selected_col:
                display_column_analysis(selected_col)
                    
            # ------------------------ Correlations ------------------------
            st.markdown("""
                <div class="container">
                    <div class="box">
                        <h1>Correlations</h1>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            sns.set_theme(style="dark")
            background_color = "#000000"  # Adjust this based on Streamlit's theme
            text_color = "white"  
             
            df_numeric = df.select_dtypes(include=[np.number]) 
            # Encode categorical columns
            df_categorical = df.select_dtypes(include=['object', 'category'])
            if not df_categorical.empty:
                df_categorical_encoded = df_categorical.apply(lambda x: pd.factorize(x)[0])  # Convert to numbers
                df_numeric = pd.concat([df_numeric, df_categorical_encoded], axis=1)

            # Convert datetime columns to numeric
            df_datetime = df.select_dtypes(include=['datetime64'])
            if not df_datetime.empty:
                # Convert datetime to numeric safely while keeping NaN values as NaN (avoids index mismatch)
                df_datetime_numeric = df_datetime.apply(lambda x: x.astype('int64', errors='ignore'))

                # Fill NaN values with a default (e.g., 0) to maintain alignment
                df_datetime_numeric = df_datetime_numeric.fillna(0)

                # Concatenate with numeric dataframe
                df_numeric = pd.concat([df_numeric, df_datetime_numeric], axis=1)
 
            corr = df_numeric.corr() 

            col1, col2 = st.columns([3, 2])
            with col1:
                
                if not corr.empty:
                    st.write("#### Correlation Matrix Table")
                    st.dataframe(corr, width=800)
                
            with col2:
                if not corr.empty:
                
                    fig, ax = plt.subplots(figsize=(7, 6))
                    fig.patch.set_facecolor(background_color)
                    ax.set_facecolor(background_color)
                    ax.spines["bottom"].set_color(text_color)
                    ax.spines["left"].set_color(text_color)
                    ax.tick_params(axis="x", which="both", bottom=False, top=False, labelbottom=False)
                    ax.tick_params(axis="y", which="both", left=False, right=False, labelleft=False)

                    ax.title.set_color(text_color)
                    ax.xaxis.label.set_color(text_color)
                    ax.yaxis.label.set_color(text_color)
                    sns.heatmap(corr, annot=True, cmap='Purples', fmt=".2f", linewidths=0.5,cbar=False, ax=ax)            
                    ax.set_title("Heatmap", fontsize=12)
                    ax.tick_params(axis='both', labelsize=6)
                    st.pyplot(fig)

                

            # ------------------------ Interaction ------------------------

            numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numerical_cols) > 1:
                

                st.markdown("""
                <div class="container">
                    <div class="box">
                        <h1>Interaction Analysis</h1>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns([1,3])


                with col1:
                    st.write("### Interactions")

                    x_col = st.selectbox("Select X-axis Column", numerical_cols)
                    y_col = st.selectbox("Select Y-axis Column", numerical_cols, index=1)

                with col2:
                    # Creating the scatter plot
                    if x_col and y_col:
                        fig, ax = plt.subplots(figsize=(8, 2.5))
                        fig.patch.set_facecolor(background_color)
                        ax.set_facecolor(background_color)
                        ax.spines["bottom"].set_color(text_color)
                        ax.spines["left"].set_color(text_color)
                        ax.tick_params(axis="x", colors=text_color)
                        ax.tick_params(axis="y", colors=text_color)
                        ax.title.set_color(text_color)
                        ax.xaxis.label.set_color(text_color)
                        ax.yaxis.label.set_color(text_color)
                        # Scatter plot
                        sns.scatterplot(x=df[x_col], y=df[y_col], color='#a855f7', alpha=0.7, ax=ax)
                        ax.set_title(f"Scatter Plot: {x_col} vs {y_col}", fontsize=12)
                        ax.set_xlabel(x_col, fontsize=10)
                        ax.set_ylabel(y_col, fontsize=10)
                        ax.tick_params(axis='both', labelsize=8)
                        st.pyplot(fig)

                    else:
                        st.warning("Not enough numerical columns to compare.")

            
                         

            
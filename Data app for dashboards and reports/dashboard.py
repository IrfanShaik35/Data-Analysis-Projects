import streamlit as st
import pandas as pd  
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards

def dash(df,uploaded_file):
    if "df_dash" not in st.session_state:
        st.warning("⚠️ No data available! Please upload a file in the main page.")
        return

    df = st.session_state["df_dash"]  # Always retrieve latest df

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
                            
    categorical_cols = [col for col in df.select_dtypes(include=['object', 'category']).columns if col not in date_cols]
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    # Sidebar filters
    st.sidebar.header("Filter Options")
    

    

    filters = {}

    for col in categorical_cols:
        unique_values = df[col].dropna().unique()
        filters[col]= st.sidebar.multiselect(
        f"Filter {col}", options=unique_values, default=[]
    )
    # Apply categorical filters
    query_conditions = [f"`{col}` == @filters['{col}']"
    for col, selected_values in filters.items() if selected_values]

    df_filtered = df.query(" & ".join(query_conditions)) if query_conditions else df


    # **Date Filters**

    if "date_filters" not in st.session_state:
        st.session_state["date_filters"] = {}

    date_filters = st.session_state["date_filters"]

    for col in date_cols:
        if col not in df.columns or df[col].isna().all():
            continue 

        df[col] = pd.to_datetime(df[col], errors='coerce')  # Ensure proper datetime format
        df = df.dropna(subset=[col]) 

         

        if df[col].empty:
            continue
        
        min_date, max_date = df[col].min(), df[col].max()
        
        # Ensure min_date and max_date are valid dates
        if pd.isnull(min_date) or pd.isnull(max_date) or min_date == max_date:
            continue

        if col not in date_filters:
            date_filters[col] = [min_date, max_date]


        selected_dates= st.sidebar.date_input(
            f"Filter {col}",
            value=date_filters[col],
            min_value=min_date,
            max_value=max_date
        )
        
        if len(selected_dates) == 2:
            start_date, end_date = map(pd.Timestamp, selected_dates)

            df_filtered = df_filtered[
            (df_filtered[col] >= start_date) & (df_filtered[col] <= end_date)
            ]

        
    # **Numeric Filters**
   
    numeric_filters = {}
    
    for col in numeric_cols:
        min_val, max_val = float(df[col].min()), float(df[col].max())
        numeric_filters[col] = st.sidebar.slider(
        f"Filter {col}", min_value=min_val, max_value=max_val, value=(min_val, max_val))

    # **Apply numeric range filters**
    for col, (min_val, max_val) in numeric_filters.items():
        if col in df_filtered.columns:
            df_filtered = df_filtered[(df_filtered[col] >= min_val) & (df_filtered[col] <= max_val)]


    # Display filtered data
    with st.expander("Show Filtered Data"):
        st.subheader("Filtered Data")
        st.dataframe(df_filtered, use_container_width=True)
    
    c1,c2=st.columns(2)
    

    with c1:

        with st.form("form_2", clear_on_submit=True):
            st.subheader("Add New Data",divider='violet',)

        
            # **Date Inputs (Two per row)**
            date_inputs = {}
            date_cols_iter = iter(date_cols)
            while True:
                try:
                    col1, col2,col3 = st.columns(3)
                    with col1:
                        col = next(date_cols_iter)
                        date_inputs[col] = st.date_input(f"{col}")

                    with col2:
                        col = next(date_cols_iter)
                        date_inputs[col] = st.date_input(f"{col}")

                    with col3:
                        col = next(date_cols_iter)
                        date_inputs[col] = st.date_input(f"{col}")
                except StopIteration:
                    break  # Stop when all columns are processed

            # **Categorical Inputs (Two per row)**
            categorical_inputs = {}
            cat_cols_iter = iter(categorical_cols)
            while True:
                try:
                    col1, col2,col3 = st.columns(3)
                    for col_container in [col1, col2, col3]:
                        with col_container:
                            col = next(cat_cols_iter)
                            options = list(df[col].dropna().unique())

                            if len(options) <= 4:
                                selection = st.selectbox(f"{col}", list(options), key=f"{col}_select")
                            else:
                                example=", ".join(map(str, options[:5])) + "..."
                                selection = st.text_input(f"{col}", key=f"{col}_input",help=f"Examples: {example}")
                                
                            categorical_inputs[col] = selection
                except StopIteration:
                    break  

                

            # **Numeric Inputs (Two per row)**
            numeric_inputs = {}
            num_cols_iter = iter(numeric_cols)
            while True:
                try:
                    col1, col2,col3 = st.columns(3)
                    with col1:
                        col = next(num_cols_iter)
                        numeric_inputs[col] = st.number_input(f"{col}")

                    with col2:
                        col = next(num_cols_iter)
                        numeric_inputs[col] = st.number_input(f"{col}") 
                    with col3:
                        col = next(num_cols_iter)
                        numeric_inputs[col] = st.number_input(f"{col}") 

                except StopIteration:
                    break

            # **Submit Button**
            btn = st.form_submit_button("Save Data")

            # **Validation & Saving**
            if btn:
                if any(v is None or v == "" for v in {**date_inputs, **categorical_inputs, **numeric_inputs}.values()):
                    st.warning("⚠️ All fields are required!")
                else:
                    # Append new data
                    new_data = {**date_inputs, **categorical_inputs, **numeric_inputs}
                    df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

                    """Save the DataFrame to the uploaded file format (CSV or Excel)"""
                    file_name = uploaded_file.name  # Get the uploaded file name

                    try:
                        if file_name.endswith(".csv"):
                            df.to_csv(file_name, index=False)
                        elif file_name.endswith((".xls", ".xlsx")):
                            df.to_excel(file_name, index=False)
        
                        st.success("Data saved successfully!")
    
                    except PermissionError:
                        st.error("⚠️ Unable to write! Please close the dataset and try again.")
    with c2:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df_filtered.select_dtypes(include=['object', 'category']).columns.tolist()

        st.subheader('Dataset Metrics', divider='violet')

        metrics = {}

        
        if numeric_cols:
            selected_col = st.selectbox("Select a Column:", numeric_cols, index=0)
            if selected_col:
                metrics[f"Total {selected_col}"] = {
                    "value": f"{df_filtered[selected_col].sum():,.0f}",
                    "delta": f"Median: {df_filtered[selected_col].median():,.0f}"
                }
                metrics[f"Maximum {selected_col}"] = {
                    "value": f"{df_filtered[selected_col].max():,.0f}",
                    "delta": "Highest Value"
                }
                metrics[f"Minimum {selected_col}"] = {
                    "value": f"{df_filtered[selected_col].min():,.0f}",
                    "delta": "Lowest Value"
                }
                metrics[f"Range of {selected_col}"] = {
                    "value": f"{df_filtered[selected_col].max() - df_filtered[selected_col].min():,.0f}",
                    "delta": "Value Spread"
                }
        else:
            selected_col = st.selectbox("Select a Column:", categorical_cols, index=0)
            if selected_col:
                most_common_value = df_filtered[col].mode()[0] if not df_filtered[col].mode().empty else "N/A"
                unique_count = df_filtered[col].nunique()
                total_count = df_filtered[col].count()
                most_common_count = df_filtered[col].value_counts().iloc[0] if not df_filtered[col].value_counts().empty else 0
                skewness_percentage = (most_common_count / total_count) * 100 if total_count > 0 else 0
                metrics[f"Most Common {col}"] = {
                    "value": most_common_value,
                    "delta": "Most Frequent"
                }
                metrics[f"Unique Values in {col}"] = {
                    "value": f"{unique_count:,}",
                    "delta": "Distinct Categories"
                }
                metrics[f"Total Count in {col}"] = {
                    "value": f"{total_count:,}",
                    "delta": "Non-empty Values"
                }
                metrics[f"Skewness in {col}"] = {
                    "value": f"{skewness_percentage:.2f}%",
                    "delta": "Dominant Category Ratio"
                }

        metric_items = list(metrics.items())
        num_metrics = len(metric_items)

        # Create dynamic rows
        for i in range(0, num_metrics, 2):
            
            cols = st.columns(2)  # Create 3 columns per row
            for col, (label, data) in zip(cols, metric_items[i:i + 3]):
                col.metric(label=label, value=data["value"], delta=data["delta"])

        # Apply styling
        style_metric_cards(
        background_color="#1a1c29",
        border_left_color="#a855f7",
        border_color="#a855f7",
        box_shadow="#a855f7"
        )

   
    c11,c22,c33=st.columns([3,0.2,3])
    with c11:
            
            # Identify potential columns
            categorical_cols = df_filtered.select_dtypes(include=["object", "category"]).columns.tolist()
            numeric_cols = df_filtered.select_dtypes(include=["number"]).columns.tolist()
            # Handle empty cases
            if not numeric_cols and not categorical_cols:
                st.warning("⚠️ The dataset does not contain any numeric or categorical columns to visualize.")
                st.stop()

            # Sidebar selection for user to pick columns dynamically
            default_x1 = categorical_cols[0] if categorical_cols else None
            default_y1 = numeric_cols[0] if numeric_cols else None
            default_color1 = categorical_cols[1] if len(categorical_cols) > 1 else None
            st.write(" ")
            
            if default_x1 and default_y1:
                dynamic_title = f"{default_x1} vs {default_y1} by {default_color1}" if default_color1 else f"{default_x1} vs {default_y1}"
            else:
                dynamic_title = "Dynamic Data Visualization"
            title_placeholder=st.subheader(dynamic_title, divider="violet")
            st.write(" ")
            

            col11, col22,col33 = st.columns(3)
    
            with col11:
                x_axis1 = st.selectbox("Select X-Axis (Categorical)", categorical_cols if categorical_cols else ["None"], key="x_axis_select1")
            with col22:
            
                y_axis1 = st.selectbox("Select Y-Axis (Numeric)", numeric_cols if numeric_cols else ["None"], key="y_axis_select1")
            with col33:
                color_col1 = st.selectbox("Select Category", categorical_cols if categorical_cols else ["None"], key="color_col_select1")

            df_viz = df_filtered.copy()   
            # If the dataset has no categorical columns, use numeric column for x-axis
            if y_axis1 == "None" :
                y_axis1 = "count"
    
                df_viz[y_axis1] = 1  # Add temporary count column for visualization

            if x_axis1 == "None":
                x_axis1 = "count"
                
                df_viz[x_axis1] = 1  # Add temporary count column for visualization
           

        
                
            
            new_title = f"{x_axis1} vs {y_axis1} by {color_col1}" if color_col1 != "None" else f"{x_axis1} vs {y_axis1}"
            title_placeholder.subheader(new_title, divider="violet")

               
            fig = px.scatter(df_viz, x=x_axis1, y=y_axis1, color=color_col1 if color_col1 != "None" else None,
            hover_data=[x_axis1, y_axis1])

            # Display interactive chart
            st.plotly_chart(fig, use_container_width=True)
            

    with c33:
           
        
            # Detect numeric and categorical columns dynamically
            numeric_cols = df_filtered.select_dtypes(include=["number"]).columns.tolist()
            categorical_cols = df_filtered.select_dtypes(include=["object", "category"]).columns.tolist()

            # Handle empty cases
            if not numeric_cols and not categorical_cols:
                st.warning("⚠️ The dataset does not contain any numeric or categorical columns to visualize.")
                st.stop()

            # Sidebar selection for user to pick columns dynamically
            default_x = categorical_cols[0] if categorical_cols else None
            default_y = numeric_cols[0] if numeric_cols else None
            default_color = categorical_cols[1] if len(categorical_cols) > 1 else None
            st.write(" ")
            
            if default_x and default_y:
                dynamic_title = f"{default_x} vs {default_y} by {default_color}" if default_color else f"{default_x} vs {default_y}"
            else:
                dynamic_title = "Dynamic Data Visualization"
            title_placeholder=st.subheader(dynamic_title, divider="violet")
            st.write(" ")

            col2, col3,col4 = st.columns(3)
           
            with col2:
                x_axis = st.selectbox("Select X-Axis (Categorical)", categorical_cols if categorical_cols else ["None"], key="x_axis_select2")
            with col3:
                y_axis = st.selectbox("Select Y-Axis (Numeric)", numeric_cols if numeric_cols else ["None"], key="y_axis_select2")
            with col4:
                color_col = st.selectbox("Select Category", categorical_cols if categorical_cols else ["None"], key="color_col_select2")
            
            # If the dataset has no categorical columns, use numeric column for x-axis
            if x_axis == "None" and numeric_cols:
                x_axis = numeric_cols[0]  # Default to first numeric column
            elif x_axis == "None":
                st.warning("⚠️ No categorical columns available for X-axis.")
                st.stop()

            # If the dataset has no numeric columns, use categorical column for y-axis with count aggregation
            if y_axis == "None" and categorical_cols:
                y_axis = "count"
                df_viz = df_filtered.copy()  # Create a copy to avoid modifying the original DataFrame
                df_viz[y_axis] = 1  # Add temporary count column for visualization
            else:
                df_viz = df_filtered.copy() 
                
            
            new_title = f"{x_axis} vs {y_axis} by {color_col}" if color_col != "None" else f"{x_axis} vs {y_axis}"
            title_placeholder.subheader(new_title, divider="violet")

               
            fig = px.bar(df_viz, x=x_axis, y=y_axis, color=color_col if color_col != "None" else None,
                 hover_data=[x_axis, y_axis])

            # Display interactive chart
            st.plotly_chart(fig, use_container_width=True)




    
    c111,c222,c333=st.columns([3,0.2,3])
    with c111:
         # Handle empty cases
            if not numeric_cols and not categorical_cols:
                st.warning("⚠️ The dataset does not contain any numeric or categorical columns to visualize.")
                st.stop()

            # Sidebar selection for user to pick columns dynamically
            default_x = categorical_cols[0] if categorical_cols else None
            default_y = numeric_cols[0] if numeric_cols else None
            default_color = categorical_cols[1] if len(categorical_cols) > 1 else None
            st.write(" ")
            
            if default_x and default_y:
                dynamic_title = f"{default_x} vs {default_y} by {default_color}" if default_color else f"{default_x} vs {default_y}"
            else:
                dynamic_title = "Dynamic Data Visualization"
            title_placeholder=st.subheader(dynamic_title, divider="violet")
            st.write(" ")

            col2, col3,col4 = st.columns(3)
            with col2:
                x_axis = st.selectbox("Select X-Axis (Categorical)", categorical_cols if categorical_cols else ["None"], key="x_axis_select3")
            with col3:
                y_axis = st.selectbox("Select Y-Axis (Numeric)", numeric_cols if numeric_cols else ["None"], key="y_axis_select3")
            with col4:
                color_col = st.selectbox("Select Category", categorical_cols if categorical_cols else ["None"], key="color_col_select3")
            
            # If the dataset has no categorical columns, use numeric column for x-axis
            if x_axis == "None" and numeric_cols:
                x_axis = numeric_cols[0]  # Default to first numeric column
            elif x_axis == "None":
                st.warning("⚠️ No categorical columns available for X-axis.")
                st.stop()

            # If the dataset has no numeric columns, use categorical column for y-axis with count aggregation
            if y_axis == "None" and categorical_cols:
                y_axis = "count"
                df_viz = df_filtered.copy()  # Create a copy to avoid modifying the original DataFrame
                df_viz[y_axis] = 1  # Add temporary count column for visualization
            else:
                df_viz = df_filtered.copy() 
                


            new_title = f"{x_axis} vs {y_axis} by {color_col}" if color_col != "None" else f"{x_axis} vs {y_axis}"
            title_placeholder.subheader(new_title, divider="violet")
               
            fig = px.box(df_viz, x=x_axis, y=y_axis, color=color_col if color_col != "None" else None,
            hover_data=[x_axis, y_axis])

            # Display interactive chart
            st.plotly_chart(fig, use_container_width=True)

    with c333:
        # Ensure the dataset has categorical or numeric columns for visualization
        if not numeric_cols and not categorical_cols:
            st.warning("⚠️ The dataset does not contain any numeric or categorical columns to visualize.")
            st.stop()

        if not categorical_cols and numeric_cols:

            # Choose a numeric column to bin
            num_col_for_bins = numeric_cols[0]  # Default to first numeric column

            # Bin numeric column into 5 ranges and convert to categorical labels
            df_filtered["Auto_Categories"] = pd.cut(df_filtered[num_col_for_bins], bins=5, precision=0).astype(str)
            categorical_cols = ["Auto_Categories"] 

        else:
            default_x = categorical_cols[0] if categorical_cols else None  # For names
            default_y = numeric_cols[0] if numeric_cols else None  # For value

        st.write(" ")
        if default_x and default_y:
            dynamic_title = f"{default_x} vs {default_y}"
        else:
            dynamic_title = "Dynamic Data Visualization"
        title_placeholder=st.subheader(dynamic_title, divider="violet")
        st.write(" ")


        # Sidebar selections for dynamic control
        col1, col2 = st.columns(2)
        with col1:
            category_col = st.selectbox("Select Category (Names)", categorical_cols if categorical_cols else ["None"], key="pie_category_select")
        with col2:
            value_col = st.selectbox("Select Values", numeric_cols if numeric_cols else ["None"], key="pie_value_select")

            

        if value_col == "None" and numeric_cols:
            value_col = numeric_cols[0]
        elif value_col == "None":
            value_col = "count"  # Use count-based aggregation
            df_viz = df_filtered.copy()
            df_viz[value_col] = 1
        else:
            df_viz = df_filtered.copy()

        # Update title dynamically
        new_title = f"{category_col} vs {value_col}"
        title_placeholder.subheader(new_title, divider="violet")

        if 'Auto_Categories' in df_filtered.columns:
            st.info("ℹ️ No categorical columns found. Creating categories from numeric data.")


        
        fig = px.pie(
            df_viz,
            names=category_col,
            values=value_col,
            )

        # Customize chart layout and labels
        fig.update_layout(
            legend_title="Categories",
            legend_y=0.9
            )
        fig.update_traces(
            textinfo="percent+label",
            textposition="inside"
            )

        # Display the chart
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
        if 'Auto_Categories' in df_filtered.columns:
            df_filtered=df_filtered.drop(columns=['Auto_Categories'])
            
        

    c1111,c2222,c3333=st.columns([3,0.2,3])
    with c1111:
        # Detect numeric and categorical columns dynamically
            numeric_cols = df_filtered.select_dtypes(include=["number"]).columns.tolist()
            categorical_cols = df_filtered.select_dtypes(include=["object", "category"]).columns.tolist()

            # Handle empty cases
            if not numeric_cols and not categorical_cols:
                st.warning("⚠️ The dataset does not contain any numeric or categorical columns to visualize.")
                st.stop()

            # Sidebar selection for user to pick columns dynamically
            default_x = categorical_cols[0] if categorical_cols else None
            default_y = numeric_cols[0] if numeric_cols else None
            default_color = categorical_cols[1] if len(categorical_cols) > 1 else None
            st.write(" ")
            
            if default_x and default_y:
                dynamic_title = f"{default_x} vs {default_y} by {default_color}" if default_color else f"{default_x} vs {default_y}"
            else:
                dynamic_title = "Dynamic Data Visualization"
            title_placeholder=st.subheader(dynamic_title, divider="violet")
            st.write(" ")

            col2, col3,col4 = st.columns(3)
        
            with col2:
                x_axis = st.selectbox("Select X-Axis (Categorical)", categorical_cols if categorical_cols else ["None"], key="x_axis_select6")
            with col3:
                y_axis = st.selectbox("Select Y-Axis (Numeric)", numeric_cols if numeric_cols else ["None"], key="y_axis_select6")
            with col4:
                color_col = st.selectbox("Select Category", categorical_cols if categorical_cols else ["None"], key="color_col_select6")
            
            # If the dataset has no categorical columns, use numeric column for x-axis
            if x_axis == "None" and numeric_cols:
                x_axis = numeric_cols[0]  # Default to first numeric column
            elif x_axis == "None":
                st.warning("⚠️ No categorical columns available for X-axis.")
                st.stop()

            # If the dataset has no numeric columns, use categorical column for y-axis with count aggregation
            if y_axis == "None" and categorical_cols:
                y_axis = "count"
                df_viz = df_filtered.copy()  # Create a copy to avoid modifying the original DataFrame
                df_viz[y_axis] = 1  # Add temporary count column for visualization
            else:
                df_viz = df_filtered.copy() 


            new_title = f"{x_axis} vs {y_axis} by {color_col}" if color_col != "None" else f"{x_axis} vs {y_axis}"
            title_placeholder.subheader(new_title, divider="violet")
               
            fig = px.area(df_viz, x=x_axis, y=y_axis, color=color_col if color_col != "None" else None,
                 hover_data=[x_axis, y_axis])

            # Display interactive chart
            st.plotly_chart(fig, use_container_width=True)

    with c3333:

            # Dynamically determine default X-axis
        if date_cols:
            default_x = date_cols[0]  # Prefer date column for time-series data
        elif categorical_cols:
            default_x = categorical_cols[0]  # Use categorical column if no dates
        elif numeric_cols:
            default_x = numeric_cols[0]  # Use numeric column if no dates or categorical columns
        else:
            st.warning("⚠️ No valid columns for X-axis.")
            st.stop()

        # Ensure Y-axis is numeric
        default_y = numeric_cols[0] if numeric_cols else None
        
        st.write(" ")
        if default_x and default_y:
            dynamic_title = f"{default_x} vs {default_y}"
        else:
            dynamic_title = "Dynamic Data Visualization"
        title_placeholder=st.subheader(dynamic_title, divider="violet")
        st.write(" ")

        # User selection for X and Y axes
        col1, col2 = st.columns(2)
        with col1:
            x_axis2 = st.selectbox("Select X-axis", options=date_cols+categorical_cols + numeric_cols, 
            index=0 if (date_cols + categorical_cols + numeric_cols) else None, key="x_axis_select4")
        with col2:
            y_axis2 = st.selectbox("Select Y-axis", options=categorical_cols + numeric_cols,
            index=0 if numeric_cols else None, key="y_axis_select4")

        # Ensure valid selections
        if not x_axis2 or not y_axis2:
            st.warning("⚠️ Please select valid X and Y axes.")
            st.stop()

        if x_axis2 == y_axis2:
            
            df_filtered["count"] = 1  # Create count column
            y_axis2 = "count"


        unique_x_values = df_filtered[x_axis2].nunique()

        # If X is categorical and has too many unique values, group by the top 10 categories
        if x_axis2 in categorical_cols and unique_x_values > 10:
            
            top_x_categories = df_filtered[x_axis2].value_counts().nlargest(10).index
            df_filtered = df_filtered[df_filtered[x_axis2].isin(top_x_categories)]

        # If X is numeric and has too many unique values, bin it into ranges
        elif x_axis2 in numeric_cols and unique_x_values > 20:
            
            df_filtered[x_axis2] = pd.to_numeric(df_filtered[x_axis2], errors="coerce")  # Convert to numeric, force errors to NaN
            df_filtered[x_axis2].dropna(inplace=True)  # Remove NaN values
            df_filtered[x_axis2] = pd.cut(df_filtered[x_axis2], bins=10).astype(str) 


        # If X is a date, resample data dynamically
        elif x_axis2 in date_cols:
           
            df_filtered[x_axis2] = pd.to_datetime(df_filtered[x_axis2])
            df_filtered = df_filtered.set_index(x_axis2).resample("M").sum().reset_index()


        # Group data for visualization
        investment_by_state = df_filtered.groupby(by=[x_axis2]).count()[[y_axis2]] if y_axis2 != "count" else df_filtered.groupby(x_axis2).size().reset_index(name="count")
        st.write(" ")
        
        # Create the line chart
        new_title = f"{x_axis2} vs {y_axis2}"
        title_placeholder.subheader(new_title, divider="violet")
               
        fig_state = px.line(
        investment_by_state,
        x=investment_by_state[x_axis2] if y_axis2 == "count" else investment_by_state.index,
        y=y_axis2,
        
        color_discrete_sequence=["#0083B8"] * len(investment_by_state),
        template="plotly_white",
        )

        # Update layout based on X-axis type
        if x_axis2 in date_cols:
            fig_state.update_layout(
            xaxis2=dict(
            tickmode="auto",  # Auto spacing for better readability
            tickformat="%Y-%m-%d",  # Format date labels
            tickangle=-45,  # Tilt labels for clarity
            type="date",  # Ensure it's treated as a date axis
            title=x_axis2
            )
            )
        else:
            # Update layout
            fig_state.update_layout(
            xaxis2=dict(tickmode="linear", tickangle=45, title=x_axis2),
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis2=dict(showgrid=True),
        )
            

        # Display chart
        st.plotly_chart(fig_state, use_container_width=True)
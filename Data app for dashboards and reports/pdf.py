import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt  # Optimized import statement
import os
from fpdf import FPDF
import io  
import re  # Regular expressions for splitting file name



def pdf(uploaded_file,df):
            def detect_date_columns(df, threshold=0.1):
                """Detects date columns based on valid date percentage."""
                date_cols = []
                for col in df.columns:
                    if df[col].dtype == 'object':
                        converted = pd.to_datetime(df[col], errors='coerce')
                        valid_ratio = converted.notna().sum() / len(df)
                        if valid_ratio >= threshold:
                            df[col] = converted
                            date_cols.append(col)
                    elif np.issubdtype(df[col].dtype, np.datetime64):  # Check if already datetime
                        date_cols.append(col)
                return date_cols

            
            def generate_column_charts(df):
                """Generates histogram/bar charts for numerical, categorical, and date columns."""
                numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                date_cols = detect_date_columns(df)

                output_dir = "charts"  # Change to your preferred directory
                os.makedirs(output_dir, exist_ok=True) 
                chart_paths = []
    
                for col in numerical_cols + categorical_cols + date_cols:
                    fig, ax = plt.subplots(figsize=(5, 3))
        
                    if col in numerical_cols:
                        sns.histplot(df[col].dropna(), bins=30, kde=True, color='#a855f7', ax=ax)
                        ax.set_title(f"Histogram: {col}",fontsize=12)
                        ax.set_xlabel(col,fontsize=10)
                        ax.set_ylabel("Frequency",fontsize=10)
                        ax.tick_params(axis='both', labelsize=8)
                    elif col in categorical_cols:
                        if df[col].dropna().nunique() > 10:
                            top_10_data = df[col].value_counts().nlargest(10)
                            sns.histplot(top_10_data.dropna(), bins=30, kde=True, color='#a855f7', ax=ax)
                            ax.set_title(f"Histogram for {col}",fontsize=12)
                            ax.set_xlabel("Count", fontsize=10)
                            ax.set_ylabel(col, fontsize=10)
                            ax.tick_params(axis='both', labelsize=8)
                        else:
                            sns.histplot(df[col].dropna(), bins=30, kde=True, color='#a855f7', ax=ax)
                            ax.set_title(f"Histogram for {col}",fontsize=12)
                            ax.set_xlabel(col, fontsize=10)
                            ax.set_ylabel("Count", fontsize=10)
                            ax.tick_params(axis='both', labelsize=8)
                    elif col in date_cols:
                        df_sorted = df[[col]].dropna().sort_values(by=col)
                        df_sorted['Count'] = range(1, len(df_sorted) + 1)
                        sns.histplot(df[col].dropna(), bins=30, kde=True, color='#a855f7', ax=ax)
                        ax.set_title(f"Time Series: {col}",fontsize=12)
                        ax.set_xlabel("Date", fontsize=10)
                        ax.set_ylabel("Cumulative Count", fontsize=10)
                        ax.tick_params(axis='both', labelsize=8)

                    
        
                    safe_col_name = re.sub(r'[^\w\-_]', '_', col)  # Replace special characters with "_"
                    image_path = os.path.join(output_dir, f"{safe_col_name}_chart.png")
                    fig.savefig(image_path, bbox_inches='tight')
                    plt.close(fig)
        
                    chart_paths.append((col, image_path))
    
                return chart_paths

            
            def generate_correlation_heatmap(df):
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

                plt.figure(figsize=(10, 6))  # Adjust figure size
                sns.heatmap(df_numeric.corr(), annot=True, cmap="Purples", fmt=".2f", linewidths=0.5)
                heatmap_path = "correlation_heatmap.png"
                plt.savefig(heatmap_path, bbox_inches="tight")
                plt.close()
                return heatmap_path

            class PDF(FPDF):
                def header(self):
                    self.set_font("Arial", style='B', size=16)
                    self.cell(270, 10, "Data Analysis Report", ln=True, align='C')
                    self.ln(10)

                def footer(self):
                    self.set_y(-15)
                    self.set_font("Arial", size=10)
                    self.cell(0, 10, f'Page {self.page_no()}', align='C')

            
            def generate_pdf(df):
                summary = df.describe(include="all").T  # Includes categorical & numerical columns
                numeric_df = df.select_dtypes(include=['number'])
                summary["Skewness"] = numeric_df.skew()
                summary["Kurtosis"] = numeric_df.kurtosis()
                summary = summary.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
                summary = summary.fillna("-")  # Fill missing values for cleaner display

                # Create PDF
                pdf = FPDF(orientation='L')
                pdf.set_auto_page_break(auto=True, margin=10)

                pdf.add_page()
                script_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(script_dir, "assets", "repolay.png")  # Use the correct folder

                if os.path.exists(image_path):
                    pdf.image(image_path, x=0, y=0, w=pdf.w, h=pdf.h)
                else:
                    print(f"⚠️ Warning: Image '{image_path}' not found. Skipping...")
                pdf.ln(5)
                # Title
                file_name, file_extension = os.path.splitext(uploaded_file.name)  # Remove extension
                # Extract first word (ignoring underscores, spaces, or special characters)
                first_word = re.split(r'[_\s\W]+', file_name)[0].capitalize()
                pdf.set_font("Arial", style='B', size=25)
                pdf.ln(46)
                pdf.cell(270, 10, f"{first_word} Analytics Report", ln=True, align='L')
                pdf.ln(8)

                datetime_cols = df.select_dtypes(include=['datetime64'])
                if not datetime_cols.empty:
                    summary.loc[datetime_cols.columns, ["mean", "min", "max"]] = datetime_cols.agg(['mean', 'min', 'max']).T

                # Format datetime values properly for PDF
                summary = summary.applymap(lambda x: x.strftime('%Y-%m-%d') if isinstance(x, pd.Timestamp) else x)


                # Fill missing values with "-"
                summary = summary.fillna("-")

                # Summary Statistics Section
                pdf.set_font("Arial", style='B', size=15)
                pdf.cell(200, 10, "Summary Statistics", ln=True, align='L')
                pdf.ln(5)

                pdf.set_font("Arial",style="B" ,size=12)
                col_widths = [50, 30, 30, 30, 30, 30, 30, 30]  # Ensure this is defined before use

                # Define table headers
                headers = ["Column", "Count", "Mean", "Std", "Min", "Max", "Skewness", "Kurtosis"]
                total_table_width = sum(col_widths)
                page_width = 297  # A4 landscape width in mm
                table_x_position = (page_width - total_table_width) / 2  # Centering the table

                # Set the fill color for the header (Purple: #A855F7 → RGB(168, 85, 247))
                pdf.set_fill_color(200, 150, 255)

                # Move to the starting position for centering
                pdf.set_x(table_x_position)
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 7, header, border=1, fill=True, align="C")
                pdf.ln()

                # Add Table Rows
                pdf.set_font("Arial", size=12)
                for col, row in summary.iterrows():
                    pdf.set_x(table_x_position)
                    pdf.cell(col_widths[0], 6, str(col), border=1, align="C")
                    pdf.cell(col_widths[1], 6, str(row["count"]), border=1, align="C")
                    pdf.cell(col_widths[2], 6, str(row["mean"]), border=1, align="C")
                    std_value = str(row["std"]) if "std" in summary.columns else "-"
                    pdf.cell(col_widths[3], 6, std_value, border=1, align="C")
                    pdf.cell(col_widths[4], 6, str(row["min"]), border=1, align="C")
                    pdf.cell(col_widths[5], 6, str(row["max"]), border=1, align="C")
                    pdf.cell(col_widths[6], 6, str(row["Skewness"]), border=1, align="C")
                    pdf.cell(col_widths[7], 6, str(row["Kurtosis"]), border=1, align="C")
                    pdf.ln()

                pdf.ln(5)

                duplicate_count = df.duplicated().sum()
                pdf.set_font("Arial", style='B', size=12)
                pdf.cell(270,10,f"Duplicate Rows: {duplicate_count}", ln=True, align='L')
                

                chart_paths = generate_column_charts(df)
    
                x_positions = [15, 160]
                y_positions = [50, 140]  # Positions for two charts per row
                chart_height = 85  # Height of each chart
                
                charts_per_page = 4  # 2x2 layout
                chart_count = 0 
                first_chart_page = True

                for i, (col_name, img_path) in enumerate(chart_paths):
                    if chart_count % charts_per_page == 0:  
                        pdf.add_page()  # Add a new page only when 4 charts are placed

                        if first_chart_page:
                            pdf.set_font("Arial", style='B', size=16)
                            pdf.cell(270, 10, "Variable Analysis", ln=True, align='L')
                            pdf.ln(4)  # Space below title
                            first_chart_page = False  # Prevent further repetition
                            

                        y_positions = [pdf.get_y() + 5, pdf.get_y() + chart_height + 15]
                    row = (i // 2) % 2  # 0 for first row, 1 for second row
                    col = i % 2  # 0 for left, 1 for right column

                    x_pos = x_positions[col]
                    y_pos = y_positions[row]

                    pdf.set_xy(x_pos, y_pos)
                    pdf.image(img_path, x=x_pos, y=y_pos , w=130, h=chart_height)  # Add chart

                    chart_count += 1  


                
                heatmap_path = generate_correlation_heatmap(df)
                pdf.add_page()
                pdf.set_font("Arial", style='B', size=16)
                pdf.cell(270, 10, "Correlation Heatmap", ln=True, align='L')
                pdf.ln(5)
                pdf.image(heatmap_path, x=30, w=220)
                
                # Save PDF
                pdf_buffer = io.BytesIO()
                pdf_content = pdf.output(dest="S").encode("latin1")  
                pdf_buffer = io.BytesIO(pdf_content)
               
                
                for _, img_path in chart_paths:
                    os.remove(img_path)
                os.remove(heatmap_path)
                return pdf_buffer
            # Add a download button
            
            p=generate_pdf(df)
            
            st.markdown("""<br><br>
    <style>
        body { background-color: #0f111a; color: white; font-family: Arial, sans-serif; }
        .hero-section { text-align: center; margin-top: 40px; color: white; }
        .hero-section h5 { font-size: 40px; font-weight: bold; text-align:center; }
        .hero-section span { color: #a855f7; } 
    </style>
    <div class="hero-section">
        <h5>Download your<span> Data Report!</span></h5>
    </div>
    """, unsafe_allow_html=True)
            col1, col2, col3 = st.columns([3.1, 1, 3])  # Middle column is wider
            with col2:
                st.download_button(label="Click to Download", data=p, file_name="Data_Report.pdf", mime="application/pdf")

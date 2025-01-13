import streamlit as st
import pandas as pd

# Set Streamlit page configuration
st.set_page_config(
    page_title="Driver Data Comparison",  # Title of the app
    layout="wide",  # Make the layout wide
    initial_sidebar_state="expanded"  # Sidebar starts expanded
)

# Streamlit app title
st.title("Driver Data Comparison")

# File upload section
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    try:
        # Define the correct column headers manually
        headers = [
            "Driver", "Driver No", "Department", "Jan", "Feb", "Mar", "Apr", "May", 
            "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Average", "Notes"
        ]

        # Load data with manual headers
        revenue_data = pd.read_excel(uploaded_file, sheet_name="Total R", header=None, skiprows=1, names=headers)
        job_data = pd.read_excel(uploaded_file, sheet_name="Total J", header=None, skiprows=1, names=headers)
        average_data = pd.read_excel(uploaded_file, sheet_name="Total Average", header=None, skiprows=1, names=headers)

        # Ensure 'Driver' column exists and is a string
        for df in [revenue_data, job_data, average_data]:
            df['Driver'] = df['Driver'].astype(str)
            df['Driver No'] = pd.to_numeric(df['Driver No'], errors="coerce", downcast="integer")  # Ensure whole number

        # Ensure numeric columns (Jan-Dec and Average) are properly formatted
        for col in revenue_data.columns[3:16]:  # Jan-Dec and Average columns
            revenue_data[col] = pd.to_numeric(revenue_data[col], errors="coerce")
        for col in job_data.columns[3:16]:
            job_data[col] = pd.to_numeric(job_data[col], errors="coerce", downcast="integer")  # Ensure whole numbers
        for col in average_data.columns[3:16]:
            average_data[col] = pd.to_numeric(average_data[col], errors="coerce")

        # UI layout with filters on the left
        col1, col2 = st.columns([1, 4])  # Left column for filters, wider right column for results

        with col1:
            # Dropdown for department selection
            departments = revenue_data['Department'].dropna().unique().tolist()
            selected_departments = st.multiselect("Select Departments:", departments)

            # Filter drivers dynamically based on department selection
            if selected_departments:
                filtered_revenue = revenue_data[revenue_data['Department'].isin(selected_departments)]
                drivers = filtered_revenue['Driver'].dropna().unique().tolist()
            else:
                filtered_revenue = revenue_data
                drivers = revenue_data['Driver'].dropna().unique().tolist()

            # Dropdown for driver selection
            selected_drivers = st.multiselect("Select Drivers:", drivers)

            metrics = ["Revenue", "Job Numbers", "Average"]
            selected_metrics = st.multiselect("Select Metrics:", metrics)

        with col2:
            # Determine which drivers to include in the table
            if selected_departments and not selected_drivers:
                # Show all drivers in selected departments if no specific drivers are selected
                table_drivers = filtered_revenue['Driver'].unique()
            elif selected_drivers:
                # Use explicitly selected drivers
                table_drivers = selected_drivers
            else:
                # Default to showing all drivers if no filters are applied
                table_drivers = revenue_data['Driver'].unique()

            if len(table_drivers) > 0 and len(selected_metrics) > 0:  # Fixed condition
                result = []

                for driver in table_drivers:
                    driver_no = revenue_data.loc[revenue_data['Driver'] == driver, 'Driver No'].values[0]  # Get driver number
                    department = revenue_data.loc[revenue_data['Driver'] == driver, 'Department'].values[0]  # Get department
                    notes = revenue_data.loc[revenue_data['Driver'] == driver, 'Notes'].values[0]  # Get notes
                    
                    row = {"Driver": driver, "Driver No": driver_no, "Department": department}
                    for metric in selected_metrics:
                        if metric == "Revenue":
                            data = revenue_data.loc[revenue_data['Driver'] == driver]
                        elif metric == "Job Numbers":
                            data = job_data.loc[job_data['Driver'] == driver]
                        elif metric == "Average":
                            data = average_data.loc[average_data['Driver'] == driver]

                        if not data.empty:
                            row.update(data.iloc[0, 3:].to_dict())  # Add Jan-Dec, Average, and Notes values to row

                    row["Notes"] = notes  # Add notes at the end
                    result.append(row)

                # Convert result to DataFrame
                result_df = pd.DataFrame(result)
                result_df.set_index("Driver", inplace=True)  # Use Driver as index

                # Display the table
                st.dataframe(
                    result_df.style.format(
                        {
                            "Driver No": "{:.0f}",  # Whole number for Driver No
                            "Jan": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Feb": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Mar": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Apr": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "May": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Jun": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Jul": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Aug": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Sep": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Oct": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Nov": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Dec": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                            "Average": "{:.0f}" if "Job Numbers" in selected_metrics else "{:,.2f}",
                        }
                    ),
                    width=1500,  # Set table width for full month display
                    height=600,  # Optional: Adjust height for larger datasets
                )
            else:
                st.info("Please select at least one department, driver, or metric.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please upload an Excel file to proceed.")

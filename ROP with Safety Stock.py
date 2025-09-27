import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import math
import tkinter as tk
from tkinter import filedialog

# Set the style for better visualizations
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("deep")

# Function to open file explorer and select a CSV file
def load_file():
    # Open a file dialog and allow the user to select the file
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select Sales Data File",
        filetypes=[("CSV Files", "*.csv")]
    )
    return file_path

# Load the data using the file dialog
file_path = load_file()

# Ensure the file path is valid
if file_path:
    df = pd.read_csv(file_path)
    print(f"File loaded: {file_path}")
else:
    print("No file selected. Exiting program.")
    exit()

# Data cleaning and preparation
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')

# Aggregate data by month for forecasting (adjust according to your actual data)
df['Month'] = df['Date'].dt.to_period('M')
monthly_sales = df.groupby('Month')['Qty'].sum().reset_index()
monthly_sales['Month'] = monthly_sales['Month'].dt.to_timestamp()

# Visualize the monthly sales trend
plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_sales, x='Month', y='Qty', marker='o', color='steelblue', linewidth=2)
plt.title('Monthly Sales Trend', fontsize=16)
plt.xlabel('Month')
plt.ylabel('Quantity Sold')
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

# Calculate the Forecast-driven Reorder Point (ROP) and Safety Stock
def calculate_rop_and_safety_stock(lead_time, service_level, forecasted_demand, std_dev_demand):
    """
    Calculate the reorder point and safety stock using the forecasted demand and demand variability.

    Parameters:
    lead_time (int): Lead time in periods (months in this case)
    service_level (float): Desired service level (e.g., 0.95 for 95% service level)
    forecasted_demand (float): Forecasted demand per period (e.g., average sales)
    std_dev_demand (float): Standard deviation of demand (demand variability)

    Returns:
    dict: Contains 'ROP' and 'Safety Stock'
    """
    # Z-score corresponding to the desired service level
    z_score = {0.90: 1.28, 0.95: 1.645, 0.99: 2.33}[service_level]

    # Safety Stock Calculation
    safety_stock = z_score * std_dev_demand * math.sqrt(lead_time)

    # ROP Calculation
    rop = forecasted_demand * lead_time + safety_stock

    return {'ROP': rop, 'Safety Stock': safety_stock}

# For simplicity, calculate the 3-month moving average as forecasted demand
monthly_sales['Moving_Avg'] = monthly_sales['Qty'].rolling(window=3).mean()

# Calculate the standard deviation of demand over the same window
monthly_sales['Std_Dev'] = monthly_sales['Qty'].rolling(window=3).std()

# Define lead time and service level
lead_time = 1  # Assume 1-month lead time
service_level = 0.95  # 95% service level

# Apply the ROP and Safety Stock calculations for each month
rop_results = []
for idx, row in monthly_sales.iterrows():
    if not np.isnan(row['Moving_Avg']) and not np.isnan(row['Std_Dev']):
        result = calculate_rop_and_safety_stock(
            lead_time, service_level, row['Moving_Avg'], row['Std_Dev']
        )
        rop_results.append({
            'Month': row['Month'],
            'ROP': result['ROP'],
            'Safety Stock': result['Safety Stock']
        })

rop_df = pd.DataFrame(rop_results)

# Visualize ROP and Safety Stock
plt.figure(figsize=(12, 6))
sns.lineplot(data=rop_df, x='Month', y='ROP', label='Reorder Point', color='green', marker='o')
sns.lineplot(data=rop_df, x='Month', y='Safety Stock', label='Safety Stock', color='red', marker='o')

plt.title('Reorder Point (ROP) and Safety Stock over Time', fontsize=16)
plt.xlabel('Month')
plt.ylabel('Quantity')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

# Show calculated results
print(rop_df)


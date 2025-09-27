# -*- coding: utf-8 -*-
"""
Created on Wed May 14 04:30:20 2025

@author: admin
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import matplotlib.dates as mdates
import math

# Set the style for better visualizations
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("deep")

# Load the data
df = pd.read_csv("cleaned_sales_data.csv")

# Initial data exploration
print("Original columns:", df.columns.tolist())
print("Sample data:\n", df.head())

# Data cleaning and preparation
# Convert data types
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce')
df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')

# Create a customer group column (for demonstration - you'll need to adjust this based on your actual data)
# Assuming there's some indicator in your data to identify Senior/PWD customers
# For example, if there's a discount pattern or specific item codes
# This is a placeholder - modify according to your actual data structure
if 'Customer Group' not in df.columns:
    # Example logic: Create a customer group based on some pattern in the data
    # This is just an example - you'll need to adjust based on your actual data
    # For demonstration, let's randomly assign customer groups
    np.random.seed(42)  # For reproducibility
    df['Customer Group'] = np.random.choice(['Regular', 'Senior/PWD'], size=len(df), p=[0.8, 0.2])

# Clean up description field to use as medicine name
df['Medicine'] = df['Description'].str.strip()

# Aggregate data for analysis
# Group by medicine and customer group
medicine_by_group = df.groupby(['Medicine', 'Customer Group'])['Qty'].sum().reset_index()
medicine_by_group.rename(columns={'Qty': 'Quantity Sold'}, inplace=True)

# Group by customer group for total sales
sales_by_group = df.groupby('Customer Group')['Sales'].sum().reset_index()
sales_by_group.rename(columns={'Sales': 'Total Sales'}, inplace=True)

# Group by month for sales trend
df['Month'] = df['Date'].dt.to_period('M')
monthly_sales = df.groupby('Month')['Sales'].sum().reset_index()
monthly_sales['Month'] = monthly_sales['Month'].dt.to_timestamp()

# Group by medicine for top products
top_products = df.groupby('Medicine')['Qty'].sum().reset_index()
top_products.rename(columns={'Qty': 'Quantity Sold'}, inplace=True)
top_products = top_products.sort_values('Quantity Sold', ascending=False).head(10)

# ========== 1. Top 10 Medicines Bought by Customer Group ==========
# Get top 10 medicines for each customer group
regular_top10 = medicine_by_group[medicine_by_group['Customer Group'] == 'Regular'].sort_values('Quantity Sold', ascending=False).head(10)
senior_top10 = medicine_by_group[medicine_by_group['Customer Group'] == 'Senior/PWD'].sort_values('Quantity Sold', ascending=False).head(10)

# Combine the top 10 lists
top10_combined = pd.concat([regular_top10, senior_top10])

plt.figure(figsize=(14, 10))
chart = sns.barplot(
    data=top10_combined, 
    x='Quantity Sold', 
    y='Medicine', 
    hue='Customer Group',
    palette={'Regular': 'navy', 'Senior/PWD': 'orange'}
)

plt.title('Top 10 Medicines Bought by Customer Group', fontsize=16, pad=20)
plt.xlabel('Quantity Sold', fontsize=12)
plt.ylabel('Medicine', fontsize=12)
plt.legend(title='Customer Group', loc='lower right')
plt.tight_layout()
plt.savefig('top10_medicines_by_group.png', dpi=300, bbox_inches='tight')
plt.show()

# ========== 2. Total Sales: Regular vs Senior/PWD ==========
plt.figure(figsize=(10, 6))
chart = sns.barplot(
    data=sales_by_group, 
    x='Customer Group', 
    y='Total Sales',
    palette={'Regular': 'royalblue', 'Senior/PWD': 'salmon'}
)

# Format y-axis to show values in millions
def millions_formatter(x, pos):
    return f'{x/1e6:.1f}M'

plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(millions_formatter))
plt.title('Total Sales: Regular vs Senior/PWD', fontsize=16, pad=20)
plt.ylabel('Sales', fontsize=12)
plt.xlabel('Customer Group', fontsize=12)
plt.tight_layout()
plt.savefig('total_sales_by_group.png', dpi=300, bbox_inches='tight')
plt.show()

# ========== 3. Monthly Sales Trend ==========
plt.figure(figsize=(12, 6))
chart = sns.lineplot(
    data=monthly_sales,
    x='Month',
    y='Sales',
    marker='o',
    markersize=8,
    color='steelblue',
    linewidth=2
)

# Format x-axis to show month names
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

# Format y-axis to show values in thousands
def thousands_formatter(x, pos):
    return f'{x/1000:.0f}K'

plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(thousands_formatter))
plt.title('Monthly Sales Trend', fontsize=16, pad=20)
plt.ylabel('Total Sales', fontsize=12)
plt.xlabel('Month', fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('monthly_sales_trend.png', dpi=300, bbox_inches='tight')
plt.show()

# ========== 4. Top 10 Best Selling Products ==========
plt.figure(figsize=(12, 8))
chart = sns.barplot(
    data=top_products,
    x='Quantity Sold',
    y='Medicine',
    color='teal'
)

plt.title('Top 10 Best Selling Products', fontsize=16, pad=20)
plt.xlabel('Quantity Sold', fontsize=12)
plt.ylabel('Medicine', fontsize=12)
plt.tight_layout()
plt.savefig('top10_best_selling_products.png', dpi=300, bbox_inches='tight')
plt.show()

# ========== 5. Economic Order Quantity (EOQ) Model ==========
# Function to calculate EOQ
def calculate_eoq(annual_demand, ordering_cost, holding_cost_percent, unit_cost):
    """
    Calculate the Economic Order Quantity
    
    Parameters:
    annual_demand (float): Annual demand quantity
    ordering_cost (float): Cost per order
    holding_cost_percent (float): Annual holding cost as a percentage of unit cost
    unit_cost (float): Cost per unit
    
    Returns:
    float: Economic Order Quantity
    """
    holding_cost = holding_cost_percent * unit_cost
    eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
    return eoq

# Function to calculate total annual inventory cost
def calculate_total_cost(annual_demand, ordering_cost, holding_cost_percent, unit_cost, order_quantity):
    """
    Calculate the total annual inventory cost
    
    Parameters:
    annual_demand (float): Annual demand quantity
    ordering_cost (float): Cost per order
    holding_cost_percent (float): Annual holding cost as a percentage of unit cost
    unit_cost (float): Cost per unit
    order_quantity (float): Order quantity
    
    Returns:
    float: Total annual inventory cost
    """
    holding_cost = holding_cost_percent * unit_cost
    annual_ordering_cost = (annual_demand / order_quantity) * ordering_cost
    annual_holding_cost = (order_quantity / 2) * holding_cost
    total_cost = annual_ordering_cost + annual_holding_cost + (annual_demand * unit_cost)
    return total_cost

# Calculate annual demand for each medicine
# Group by medicine and sum quantities
medicine_annual_demand = df.groupby('Medicine')['Qty'].sum().reset_index()
medicine_annual_demand.rename(columns={'Qty': 'Annual Demand'}, inplace=True)

# For demonstration, let's assume some values for ordering cost, holding cost percentage, and unit cost
# In a real scenario, these would come from your actual data or business knowledge
ordering_cost = 100  # Cost per order in currency units
holding_cost_percent = 0.2  # 20% annual holding cost as percentage of unit cost

# Create a dataframe with sample unit costs for the top 10 medicines
# In a real scenario, you would use actual cost data from your database
np.random.seed(42)  # For reproducibility
top10_medicines = top_products['Medicine'].tolist()
unit_costs = np.random.uniform(10, 100, len(top10_medicines))  # Random unit costs between 10 and 100
medicine_costs = pd.DataFrame({
    'Medicine': top10_medicines,
    'Unit Cost': unit_costs
})

# Merge annual demand with unit costs
eoq_data = pd.merge(medicine_annual_demand, medicine_costs, on='Medicine', how='inner')

# Calculate EOQ and related metrics for each medicine
eoq_results = []
for _, row in eoq_data.iterrows():
    medicine = row['Medicine']
    annual_demand = row['Annual Demand']
    unit_cost = row['Unit Cost']
    
    # Calculate EOQ
    eoq = calculate_eoq(annual_demand, ordering_cost, holding_cost_percent, unit_cost)
    
    # Calculate total cost with EOQ
    total_cost_eoq = calculate_total_cost(annual_demand, ordering_cost, holding_cost_percent, unit_cost, eoq)
    
    # Calculate number of orders per year
    orders_per_year = annual_demand / eoq
    
    # Calculate days between orders (assuming 365 days per year)
    days_between_orders = 365 / orders_per_year
    
    eoq_results.append({
        'Medicine': medicine,
        'Annual Demand': annual_demand,
        'Unit Cost': unit_cost,
        'EOQ': eoq,
        'Total Annual Cost': total_cost_eoq,
        'Orders Per Year': orders_per_year,
        'Days Between Orders': days_between_orders
    })

# Create a dataframe with EOQ results
eoq_df = pd.DataFrame(eoq_results)

# Sort by annual demand for better visualization
eoq_df = eoq_df.sort_values('Annual Demand', ascending=False)

# Display EOQ results
print("\n===== Economic Order Quantity (EOQ) Analysis =====")
print(eoq_df[['Medicine', 'Annual Demand', 'EOQ', 'Orders Per Year', 'Days Between Orders', 'Total Annual Cost']].to_string(index=False))

# Visualize EOQ results
plt.figure(figsize=(12, 8))
chart = sns.barplot(
    data=eoq_df.head(10),
    x='EOQ',
    y='Medicine',
    color='forestgreen'
)

plt.title('Economic Order Quantity (EOQ) for Top Medicines', fontsize=16, pad=20)
plt.xlabel('Economic Order Quantity', fontsize=12)
plt.ylabel('Medicine', fontsize=12)
plt.tight_layout()
plt.savefig('eoq_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Visualize the relationship between EOQ and Annual Demand
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=eoq_df,
    x='Annual Demand',
    y='EOQ',
    size='Unit Cost',
    sizes=(50, 200),
    alpha=0.7,
    color='purple'
)

plt.title('Relationship Between Annual Demand and EOQ', fontsize=16, pad=20)
plt.xlabel('Annual Demand', fontsize=12)
plt.ylabel('Economic Order Quantity (EOQ)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('eoq_vs_demand.png', dpi=300, bbox_inches='tight')
plt.show()

# Demonstrate the cost curve for a specific medicine
# Choose the top selling medicine for demonstration
top_medicine = eoq_df.iloc[0]['Medicine']
top_medicine_demand = eoq_df.iloc[0]['Annual Demand']
top_medicine_unit_cost = eoq_df.iloc[0]['Unit Cost']
top_medicine_eoq = eoq_df.iloc[0]['EOQ']

# Calculate costs for different order quantities
order_quantities = np.linspace(top_medicine_eoq * 0.2, top_medicine_eoq * 2, 100)
ordering_costs = []
holding_costs = []
total_costs = []

for q in order_quantities:
    holding_cost = holding_cost_percent * top_medicine_unit_cost
    annual_ordering_cost = (top_medicine_demand / q) * ordering_cost
    annual_holding_cost = (q / 2) * holding_cost
    total_cost = annual_ordering_cost + annual_holding_cost
    
    ordering_costs.append(annual_ordering_cost)
    holding_costs.append(annual_holding_cost)
    total_costs.append(total_cost)

# Create a dataframe for cost curve visualization
cost_curve_df = pd.DataFrame({
    'Order Quantity': order_quantities,
    'Ordering Cost': ordering_costs,
    'Holding Cost': holding_costs,
    'Total Cost': total_costs
})

# Plot the cost curves
plt.figure(figsize=(12, 8))
plt.plot(cost_curve_df['Order Quantity'], cost_curve_df['Ordering Cost'], label='Ordering Cost', color='blue', linewidth=2)
plt.plot(cost_curve_df['Order Quantity'], cost_curve_df['Holding Cost'], label='Holding Cost', color='red', linewidth=2)
plt.plot(cost_curve_df['Order Quantity'], cost_curve_df['Total Cost'], label='Total Cost', color='green', linewidth=3)

# Mark the EOQ point
min_cost_idx = cost_curve_df['Total Cost'].idxmin()
min_cost_q = cost_curve_df.iloc[min_cost_idx]['Order Quantity']
min_cost = cost_curve_df.iloc[min_cost_idx]['Total Cost']
plt.scatter(min_cost_q, min_cost, color='purple', s=100, zorder=5)
plt.annotate(f'EOQ = {min_cost_q:.1f}', 
             xy=(min_cost_q, min_cost),
             xytext=(min_cost_q + 5, min_cost + 100),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
             fontsize=12)

plt.title(f'Cost Curve Analysis for {top_medicine}', fontsize=16, pad=20)
plt.xlabel('Order Quantity', fontsize=12)
plt.ylabel('Cost', fontsize=12)
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('eoq_cost_curve.png', dpi=300, bbox_inches='tight')
plt.show()

# Calculate sensitivity analysis for different holding cost percentages
holding_cost_percentages = np.linspace(0.1, 0.3, 5)  # 10% to 30%
sensitivity_results = []

for hcp in holding_cost_percentages:
    eoq = calculate_eoq(top_medicine_demand, ordering_cost, hcp, top_medicine_unit_cost)
    total_cost = calculate_total_cost(top_medicine_demand, ordering_cost, hcp, top_medicine_unit_cost, eoq)
    sensitivity_results.append({
        'Holding Cost Percentage': hcp * 100,  # Convert to percentage for display
        'EOQ': eoq,
        'Total Cost': total_cost
    })

sensitivity_df = pd.DataFrame(sensitivity_results)

# Plot sensitivity analysis
fig, ax1 = plt.subplots(figsize=(10, 6))

color = 'tab:blue'
ax1.set_xlabel('Holding Cost Percentage (%)', fontsize=12)
ax1.set_ylabel('EOQ', fontsize=12, color=color)
ax1.plot(sensitivity_df['Holding Cost Percentage'], sensitivity_df['EOQ'], color=color, marker='o')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Total Cost', fontsize=12, color=color)
ax2.plot(sensitivity_df['Holding Cost Percentage'], sensitivity_df['Total Cost'], color=color, marker='s')
ax2.tick_params(axis='y', labelcolor=color)

plt.title(f'EOQ Sensitivity Analysis for {top_medicine}', fontsize=16, pad=20)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('eoq_sensitivity.png', dpi=300, bbox_inches='tight')
plt.show()

print("\nEconomic Order Quantity (EOQ) analysis complete! All visualizations have been generated.")

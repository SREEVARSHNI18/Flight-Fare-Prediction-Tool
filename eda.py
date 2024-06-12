import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the cleaned data
df = pd.read_csv("cleaned_flight_data.csv")

# Assuming the exchange rate from SAR to INR is 18.50
exchange_rate = 18.50

# Convert the price from SAR to INR
df['Price_INR'] = df['Price'] * exchange_rate

# Display the first few rows of the DataFrame with the converted price
print("First few rows of the DataFrame with price in INR:")
print(df.head())

# Summary statistics
print("\nSummary statistics:")
print(df.describe())

# Data types and missing values
print("\nData types and missing values:")
print(df.info())

# Visualize the distribution of flight prices in INR
plt.figure(figsize=(10, 6))
sns.histplot(df['Price_INR'], bins=20, kde=True, color='skyblue')
plt.title('Distribution of Flight Prices (INR)')
plt.xlabel('Price (INR)')
plt.ylabel('Frequency')
plt.show()

# Visualize the relationship between duration and price
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Duration', y='Price_INR', color='coral')
plt.title('Relationship between Duration and Price (INR)')
plt.xlabel('Duration (minutes)')
plt.ylabel('Price (INR)')
plt.show()

# Visualize the average price by airline
plt.figure(figsize=(12, 6))
sns.barplot(data=df, x='Airline', y='Price_INR', errorbar='sd', hue='Airline', dodge=False)
plt.title('Average Price by Airline (INR)')
plt.xlabel('Airline')
plt.ylabel('Average Price (INR)')
plt.xticks(rotation=45, ha='right')
plt.legend([], frameon=False)
plt.show()

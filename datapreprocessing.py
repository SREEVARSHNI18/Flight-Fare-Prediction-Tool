import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle as pkl
import matplotlib.pyplot as plt
sns.set()

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn import metrics

def clean_duration(duration):
    duration = list(duration)
    duration_hours = []
    duration_mins = []
    for i in range(len(duration)):
        duration_hours.append(int(duration[i].split(sep="h")[0]))  # Extract hours from duration
        duration_mins.append(int(duration[i].split(sep="m")[0].split()[-1]))  # Extracts only minutes from duration

    d = []
    for i in range(len(duration)):
        d.append(duration_hours[i] * 60 + duration_mins[i])

    return d

def clean_price(price):
    price = price.str.replace(',', '', regex=True)
    price = price.str.replace('SAR', '', regex=True)
    price = price.str.strip()
    price = pd.to_numeric(price) * 19.45  # Assuming 1 SAR = 19.45 INR
    return price



def clean_date(date):
    date = pd.to_datetime(date, dayfirst=True)
    return date

def get_avg_per_airline(x):
    # Initialize an empty DataFrame to hold the results
    t_ = pd.DataFrame(columns=["Airline", "Average Price"])

    # average for trips with multiple airlines
    multiple_airlines = x[x["Airline"].str.contains(",")]
    b = list(multiple_airlines["Airline"].str.split(","))
    d = []  # Airline 1
    e = []  # Airline 2
    for i in range(len(b)):
        d.append(b[i][0])
        e.append(b[i][1])
    for i in range(len(e)):
        e[i] = e[i].strip()
    m_airlines = list(set(d)) + list(set(e))

    for airline in m_airlines:
        t = pd.DataFrame(x[x["Airline"].str.contains(airline)]["Airline"])
        t["Average Price"] = x[x["Airline"].str.contains(airline)]["Price"].mean()
        t_ = pd.concat([t_, t])  # Use concat instead of append

    t__ = t_.groupby("Airline", as_index=False)["Average Price"].mean()
    k = multiple_airlines.copy()
    k = k.merge(t__, on="Airline", how="left")

    # average for trips with single airlines
    single_airlines = x[~x["Airline"].str.contains(",")]
    avg_per_airline = single_airlines.groupby("Airline", as_index=False)["Price"].mean()
    avg_per_airline = avg_per_airline.rename(columns={"Price": "Average Price"})
    temp = single_airlines.copy()
    temp = temp.merge(avg_per_airline, on='Airline', how="left")

    temp_1 = temp.groupby("Airline", as_index=False)["Average Price"].mean()
    k_1 = k.groupby("Airline", as_index=False)["Average Price"].mean()
    k_temp = pd.concat([k_1, temp_1])
    y = x.merge(k_temp, on="Airline")

    return y

# Read data
df1 = pd.read_csv(r"C:\Users\sreev\OneDrive\Desktop\Web scrapper proj\BLR_MAA.csv")
df2 = pd.read_csv(r"C:\Users\sreev\OneDrive\Desktop\Web scrapper proj\DEL_BLR.csv")

dfs_raw = [df1, df2]
dfs = []

# Clean and preprocess data
for df in dfs_raw:
    df.drop_duplicates(inplace=True)  # drop duplicate rows
    df["Duration"] = clean_duration(df["Duration"])  # convert duration to numerical minutes format
    df["Price"] = clean_price(df["Price"])  # convert price to numerical format in INR
    df["Date"] = clean_date(df["Date"])  # convert date to datetime format
    # Extracting time component if available
    df['Time'] = df['Date'].dt.time  # Extracting time component
    df["Date"] = df["Date"].dt.date  # Extracting date component
    dfs.append(get_avg_per_airline(df))  # get average per airline


# Merge dataframes and perform further preprocessing
df = pd.concat(dfs)

# Check for missing values
print(df.isnull().sum())
cheapest_price = df['Price'].min()
# Find the row with the cheapest price
cheapest_row = df[df['Price'] == cheapest_price]

# Extract the corresponding airline
cheapest_airline = cheapest_row['Airline'].iloc[0]
cheapest_datetime = cheapest_row['Date'].iloc[0]
# Print the cheapest price and corresponding airline
print("Cheapest Price:", cheapest_price)
print("Cheapest Airline:", cheapest_airline)
print("Date and Time of Cheapest Price:", cheapest_datetime)
plt.figure(figsize=(12, 6))
sns.barplot(x='Airline', y='Average Price', data=df, color='skyblue')
plt.xlabel('Airline')
plt.ylabel('Average Price (INR)')
plt.title('Average Price of Flights by Airline')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

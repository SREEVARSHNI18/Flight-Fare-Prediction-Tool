import os
import re
import time
from datetime import datetime
import pandas as pd
import numpy as np

def clean_data(df):
    # Step 1: Initial Data Inspection
    print("Initial Data Inspection:")
    print(df.head())
    print(df.describe())
    print(df.info())

    # Step 2: Handle Missing Values
    # Drop rows with missing values in important columns
    df = df.dropna(subset=['Airline', 'Source', 'Destination', 'Duration', 'Total stops', 'Price', 'Date'])

    # Step 3: Correct Data Types
    # Convert 'Date' column to datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')

    # Convert 'Price' column to numeric, removing currency symbols and commas
    df['Price'] = df['Price'].str.replace(r'[^\d.]', '', regex=True).astype(float)

    # Extract numerical value for 'Total stops' and replace 'non-stop' with 0
    df['Total stops'] = df['Total stops'].apply(lambda x: 0 if 'nonstop' in x.lower() else int(re.findall(r'\d+', x)[0]))

    # Step 4: Handle Duplicates
    df = df.drop_duplicates()

    # Step 5: Handle Outliers (Optional)
    # Using IQR to filter out outliers in 'Price' column
    Q1 = df['Price'].quantile(0.25)
    Q3 = df['Price'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df['Price'] < (Q1 - 1.5 * IQR)) | (df['Price'] > (Q3 + 1.5 * IQR)))]

    # Step 6: Feature Engineering
    # Extracting date features
    df['day_of_week'] = df['Date'].dt.dayofweek
    df['month'] = df['Date'].dt.month
    df['day_of_month'] = df['Date'].dt.day

    # Convert 'Duration' from string to total minutes
    def duration_to_minutes(duration):
        hours, minutes = 0, 0
        if 'h' in duration:
            hours = int(re.findall(r'(\d+)h', duration)[0])
        if 'm' in duration:
            minutes = int(re.findall(r'(\d+)m', duration)[0])
        return hours * 60 + minutes

    df['Duration'] = df['Duration'].apply(duration_to_minutes)

    # Step 7: Final Inspection
    print("Final Data Inspection:")
    print(df.head())
    print(df.describe())
    print(df.info())

    return df

# Load your scraped data
df = pd.read_csv(r"C:\Users\sreev\OneDrive\Desktop\Web scrapper proj\BLR_MAA.csv")

# Clean the data
cleaned_df = clean_data(df)

# Save the cleaned data to a new CSV file
cleaned_df.to_csv('cleaned_flight_data.csv', index=False)

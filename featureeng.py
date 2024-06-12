import pandas as pd
from sklearn.preprocessing import StandardScaler

# Load the cleaned data
df = pd.read_csv("cleaned_flight_data.csv")

# 1. Extract date features
df['Date'] = pd.to_datetime(df['Date'])
df['day_of_week'] = df['Date'].dt.dayofweek
df['month'] = df['Date'].dt.month
df['day_of_month'] = df['Date'].dt.day

# 2. Convert duration to minutes if it's in string format
if isinstance(df['Duration'][0], str):
    df['Duration'] = df['Duration'].apply(lambda x: int(x.split()[0].replace('h', '')) * 60 + int(x.split()[1].replace('m', '')))

# 3. One-hot encoding for categorical variables
df = pd.get_dummies(df, columns=['Airline', 'Source', 'Destination'], drop_first=True)

# 4. Scale numerical features
scaler = StandardScaler()
numerical_features = ['Duration', 'day_of_week', 'month', 'day_of_month']
df[numerical_features] = scaler.fit_transform(df[numerical_features])

# 5. Create additional features
df['TimeOfDay'] = pd.to_datetime(df['Date']).dt.hour

# Display the updated DataFrame
print(df.head())

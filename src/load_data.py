import pandas as pd

# Load dataset
df = pd.read_csv("data/tech_mental_health_burnout.csv")

# Show first 5 rows
print(df.head())

# Dataset information
print(df.info())

# Missing values
print(df.isnull().sum())
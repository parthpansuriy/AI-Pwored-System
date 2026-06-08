import pandas as pd

# Load dataset
df = pd.read_csv("data/tech_mental_health_burnout.csv")

# Show duplicate rows
print("Duplicate Rows:", df.duplicated().sum())

# Remove duplicates
df = df.drop_duplicates()

# Convert categorical columns into numbers
df["gender"] = df["gender"].astype("category").cat.codes
df["job_role"] = df["job_role"].astype("category").cat.codes
df["company_size"] = df["company_size"].astype("category").cat.codes
df["work_mode"] = df["work_mode"].astype("category").cat.codes
df["burnout_level"] = df["burnout_level"].astype("category").cat.codes

# Show processed data
print(df.head())

# Save cleaned dataset
df.to_csv("data/cleaned_burnout_dataset.csv", index=False)

print("Data preprocessing completed successfully!")
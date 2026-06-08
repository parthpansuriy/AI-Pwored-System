import joblib
import pandas as pd

# Load trained model
model = joblib.load("burnout_model.pkl")

# Sample employee data
employee_data = {
    "age": [30],
    "gender": [1],
    "job_role": [2],
    "experience_years": [5],
    "company_size": [1],
    "work_mode": [2],
    "work_hours_per_week": [50],
    "overtime_hours": [10],
    "meetings_per_day": [4],
    "deadlines_missed": [2],
    "job_satisfaction": [4],
    "manager_support": [3],
    "work_life_balance": [2],
    "sleep_hours": [5],
    "physical_activity_days": [2],
    "screen_time_hours": [10],
    "caffeine_intake": [3],
    "social_support_score": [4],
    "has_therapy": [0],
    "stress_level": [8],
    "anxiety_score": [7],
    "depression_score": [6],
    "burnout_score": [8],
    "seeks_professional_help": [0]
}

# Convert into dataframe
employee_df = pd.DataFrame(employee_data)

# Predict burnout level
prediction = model.predict(employee_df)

print("Predicted Burnout Level:", prediction[0])
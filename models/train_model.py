import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load cleaned dataset
df = pd.read_csv("data/cleaned_burnout_dataset.csv")

# Features
X = df.drop("burnout_level", axis=1)

# Target
y = df["burnout_level"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create model
model = RandomForestClassifier()

# Train model
model.fit(X_train, y_train)

# Prediction
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy)

# Save model
joblib.dump(model, "burnout_model.pkl")

print("Model saved successfully!")
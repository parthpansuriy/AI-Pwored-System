import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="parth@2101",
    database="burnout_db"
)

cursor = db.cursor()

print("Database Connected Successfully!")
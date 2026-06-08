import mysql.connector
from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
import joblib
from reportlab.pdfgen import canvas

# ==============================
# FLASK APP
# ==============================

app = Flask(__name__)

app.secret_key = "burnout_secret_key"

# ==============================
# LOAD ML MODEL
# ==============================

model = joblib.load("burnout_model.pkl")

# ==============================
# MYSQL CONNECTION
# ==============================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="parth@2101",
    database="burnout_db"
)

cursor = db.cursor()

# ==============================
# HOME PAGE
# ==============================

@app.route("/")
def home():
    return render_template("home.html")

# ==============================
# SIGNUP PAGE
# ==============================

@app.route("/signup")
def signup():
    return render_template("signup.html")

# ==============================
# SIGNUP VALIDATION
# ==============================

@app.route("/signup_validation", methods=["POST"])
def signup_validation():

    full_name = request.form["full_name"]
    email = request.form["email"]
    password = request.form["password"]

    # CHECK USER

    query = """
    SELECT * FROM users
    WHERE full_name=%s
    """

    cursor.execute(query, (full_name,))
    existing_user = cursor.fetchone()

    # USER ALREADY EXISTS

    if existing_user:
        return render_template(
            "signup.html",
            error="Username already exists"
        )

    # INSERT USER

    insert_query = """
    INSERT INTO users
    (
        full_name,
        email,
        password
    )
    VALUES (%s, %s, %s)
    """

    values = (
        full_name,
        email,
        password
    )

    cursor.execute(insert_query, values)
    db.commit()

    session["user"] = full_name

    return redirect("/employee_form")

# ==============================
# LOGIN PAGE
# ==============================

@app.route("/login")
def login():
    return render_template("login.html")

# ==============================
# LOGIN VALIDATION
# ==============================

@app.route("/login_validation", methods=["POST"])
def login_validation():

    username = request.form["username"]
    password = request.form["password"]

    # ADMIN LOGIN

    if username == "admin" and password == "admin123":

        session["admin"] = "admin"
        session["user"] = "Admin"

        return redirect("/dashboard")

    # NORMAL USER LOGIN

    query = """
    SELECT * FROM users
    WHERE full_name=%s AND password=%s
    """

    values = (
        username,
        password
    )

    cursor.execute(query, values)
    user = cursor.fetchone()

    # LOGIN SUCCESS

    if user:

        session["user"] = user[1]

        return redirect("/employee_form")

    # LOGIN FAILED

    return render_template(
        "login.html",
        error="Invalid Username or Password"
    )

# ==============================
# EMPLOYEE FORM PAGE
# ==============================

@app.route("/employee_form")
def employee_form():

    if "user" not in session:
        return redirect("/login")

    return render_template("employee_form.html")

# ==============================
# USER DASHBOARD
# ==============================

@app.route("/user_dashboard")
def user_dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "user_dashboard.html",
        username=session.get("user"),
        prediction="No Prediction Yet",
        burnout_percentage=0,
        sleep_hours=0,
        stress_level=0,
        work_hours=0
    )

# ==============================
# ADMIN DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/login")

    query = """
    SELECT * FROM employee_predictions
    """

    cursor.execute(query)
    records = cursor.fetchall()

    total_predictions = len(records)

    return render_template(
        "dashboard.html",
        records=records,
        total_predictions=total_predictions
    )

# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.pop("user", None)
    session.pop("admin", None)

    return redirect("/")

# ==============================
# PREDICTION ROUTE
# ==============================

@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return redirect("/login")

    # FORM DATA

    age = int(request.form["age"])
    stress_level = int(request.form["stress_level"])
    sleep_hours = int(request.form["sleep_hours"])
    work_type = request.form["work_type"]
    work_hours = int(request.form["work_hours"])

    # WEEKLY HOURS

    if work_type == "day":
        weekly_hours = work_hours * 6
    else:
        weekly_hours = work_hours

    # DATAFRAME

    data = {
        "age": [age],
        "gender": [1],
        "job_role": [2],
        "experience_years": [5],
        "company_size": [1],
        "work_mode": [2],
        "work_hours_per_week": [weekly_hours],
        "overtime_hours": [10],
        "meetings_per_day": [4],
        "deadlines_missed": [2],
        "job_satisfaction": [4],
        "manager_support": [3],
        "work_life_balance": [2],
        "sleep_hours": [sleep_hours],
        "physical_activity_days": [2],
        "screen_time_hours": [10],
        "caffeine_intake": [3],
        "social_support_score": [4],
        "has_therapy": [0],
        "stress_level": [stress_level],
        "anxiety_score": [7],
        "depression_score": [6],
        "burnout_score": [8],
        "seeks_professional_help": [0]
    }

    df = pd.DataFrame(data)

    # ML PREDICTION

    prediction = model.predict(df)[0]

    probability = model.predict_proba(df)

    burnout_percentage = round(
        max(probability[0]) * 100,
        2
    )

    burnout_labels = {
        0: "High Burnout",
        1: "Low Burnout",
        2: "Moderate Burnout"
    }

    result = burnout_labels[prediction]

    # SAVE DATABASE

    query = """
    INSERT INTO employee_predictions
    (
        age,
        stress_level,
        sleep_hours,
        work_type,
        work_hour,
        burnout_prediction,
        burnout_percentage
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        age,
        stress_level,
        sleep_hours,
        work_type,
        weekly_hours,
        result,
        burnout_percentage
    )

    cursor.execute(query, values)
    db.commit()

    return render_template(
        "user_dashboard.html",
        username=session.get("user"),
        prediction=result,
        burnout_percentage=burnout_percentage,
        sleep_hours=sleep_hours,
        stress_level=stress_level,
        work_hours=weekly_hours
    )

# ==============================
# PDF REPORT
# ==============================

@app.route("/generate_report")
def generate_report():

    burnout_percentage = request.args.get("burnout_percentage", "0")
    prediction = request.args.get("prediction", "Unknown")
    sleep_hours = request.args.get("sleep_hours", "0")
    stress_level = request.args.get("stress_level", "0")
    work_hours = request.args.get("work_hours", "0")

    pdf = canvas.Canvas("Burnout_Report.pdf")

    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(150, 800, "BurnoutAI Wellness Report")

    pdf.line(60, 780, 550, 780)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(60, 740, "Employee Wellness Summary")

    pdf.setFont("Helvetica", 13)

    pdf.drawString(
        70,
        700,
        f"Employee Name : {session.get('user')}"
    )

    pdf.drawString(
        70,
        670,
        f"Burnout Prediction : {prediction}"
    )

    pdf.drawString(
        70,
        640,
        f"Burnout Percentage : {burnout_percentage}%"
    )

    pdf.drawString(
        70,
        610,
        f"Stress Level : {stress_level}/10"
    )

    pdf.drawString(
        70,
        580,
        f"Sleep Hours : {sleep_hours} hrs"
    )

    pdf.drawString(
        70,
        550,
        f"Weekly Workload : {work_hours} hrs"
    )

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(60, 490, "AI Recommendations")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        70,
        450,
        "Maintain proper work-life balance."
    )

    pdf.drawString(
        70,
        425,
        "Sleep 7-8 hours daily."
    )

    pdf.drawString(
        70,
        400,
        "Reduce continuous stress and workload."
    )

    pdf.drawString(
        70,
        375,
        "Practice meditation and exercise."
    )

    pdf.drawString(
        70,
        350,
        "Regular wellness monitoring recommended."
    )

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        60,
        80,
        "Generated using Flask + Machine Learning + AI Analytics"
    )

    pdf.drawString(
        60,
        60,
        "BurnoutAI | Developed by Parth Pansuriya"
    )

    pdf.save()

    return send_file(
        "Burnout_Report.pdf",
        as_attachment=True
    )

# ==============================
# RUN APP
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
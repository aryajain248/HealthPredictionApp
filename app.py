from flask import Flask, render_template, request, redirect
import sqlite3
import os
from google import genai

app = Flask(__name__)

# =========================
# GEMINI API KEY (SAFE)
# =========================
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

# =========================
# DATABASE INIT
# =========================
def init_db():
    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dob TEXT,
            email TEXT,
            glucose REAL,
            haemoglobin REAL,
            cholesterol REAL,
            remarks TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# AI FUNCTION
# =========================
def get_remarks(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except:
        return "AI temporarily unavailable"

# =========================
# HOME
# =========================
@app.route("/", methods=["GET", "POST"])
def home():
    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        dob = request.form["dob"]
        email = request.form["email"]
        glucose = float(request.form["glucose"])
        haemoglobin = float(request.form["haemoglobin"])
        cholesterol = float(request.form["cholesterol"])

        prompt = f"""
        Patient health analysis:
        Glucose: {glucose}
        Haemoglobin: {haemoglobin}
        Cholesterol: {cholesterol}
        Give short medical risk remark.
        """

        remarks = get_remarks(prompt)

        cursor.execute("""
            INSERT INTO patients
            (name, dob, email, glucose, haemoglobin, cholesterol, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, dob, email, glucose, haemoglobin, cholesterol, remarks))

        conn.commit()

    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()

    conn.close()

    return render_template("index.html", patients=patients)

# =========================
# DELETE
# =========================
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("patients.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
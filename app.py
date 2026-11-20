
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "cloudhire-development-secret-key"

# DEMO ADMIN CREDENTIALS
ADMIN_EMAIL = "admin@cloudhire.com"
ADMIN_PASSWORD = "Admin@123"

# Temporary storage (will later migrate to DynamoDB)
users = {}
applications = []

jobs = [
    {
        "id": 1,
        "title": "Python Developer",
        "company": "Tech Solutions",
        "location": "Bengaluru",
        "type": "Full Time",
        "salary": "₹4 - 6 LPA",
        "skills": ["Python", "SQL"],
        "description": "Develop and maintain applications, work with databases and build reliable backend solutions.",
        "requirements": [
            "Knowledge of Python programming",
            "Basic SQL and database knowledge",
            "Understanding of HTML and CSS",
            "Good problem-solving skills"
        ]
    },
    {
        "id": 2,
        "title": "Frontend Developer",
        "company": "Digital Works",
        "location": "Hyderabad",
        "type": "Full Time",
        "salary": "₹3 - 5 LPA",
        "skills": ["HTML", "CSS"],
        "description": "Create responsive and user-friendly websites.",
        "requirements": [
            "Knowledge of HTML and CSS",
            "Basic JavaScript knowledge",
            "Understanding of responsive design",
            "Good communication skills"
        ]
    },
    {
        "id": 3,
        "title": "Data Analyst",
        "company": "Analytics Hub",
        "location": "Bengaluru",
        "type": "Internship",
        "salary": "₹15,000 per month",
        "skills": ["Python", "Excel"],
        "description": "Analyse datasets, prepare reports and identify useful business insights.",
        "requirements": [
            "Basic Python knowledge",
            "Knowledge of Microsoft Excel",
            "Basic SQL knowledge",
            "Interest in data analysis"
        ]
    }
]


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html", jobs=jobs)


# ---------------- JOB DETAILS ----------------

@app.route("/job/<int:job_id>")
def job_details(job_id):
    job = next((j for j in jobs if nj["id"] == job_id), None)

    if not job:
        return "Job not found", 404

    already_applied = any(
        a["job_id"] == job_id and
        a["email"] == session.get("user_email")
        for a in applications
    )

    return render_template(
        "job_details.html",
        job=job,
        already_applied=already_applied
    )


# ---------------- USER REGISTRATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must contain at least 6 characters.")
            return redirect(url_for("register"))

        if email in users:
            flash("Email is already registered.")
            return redirect(url_for("register"))

        users[email] = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password)
        }

        flash("Registration successful! Please login.")
        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- USER LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = users.get(email)

        if user and check_password_hash(user["password"], password):
            session["user_email"] = email
            session["user_name"] = user["name"]
            session.pop("admin", None)

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- USER DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))

    user_applications = [
        a for a in applications
        if a["email"] == session["user_email"]
    ]

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        jobs=jobs,
        applications=user_applications
    )


# ---------------- APPLY FOR JOB ----------------

@app.route("/apply/<int:job_id>", methods=["POST"])
def apply_job(job_id):
    if "user_email" not in session:
        flash("Please login before applying.")
        return redirect(url_for("login"))

    job = next((j for j in jobs if j["id"] == job_id), None)

    if not job:
        return "Job not found", 404

    email = session["user_email"]

    for application in applications:
        if application["job_id"] == job_id and application["email"] == email:
            flash("You have already applied for this job.")
            return redirect(url_for("job_details", job_id=job_id))

    applications.append({
        "application_id": len(applications) + 1,
        "job_id": job_id,
        "job_title": job["title"],
        "company": job["company"],
        "email": email,
        "name": session["user_name"],
        "status": "Pending"
    })

    flash("Application submitted successfully!")
    return redirect(url_for("dashboard"))


# ---------------- ADMIN LOGIN ----------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session.clear()
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))

        flash("Invalid administrator credentials.")

    return render_template("admin_login.html")


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    return render_template(
        "admin.html",
        jobs=jobs,
        users=users,
        applications=applications
    )


# ---------------- ADD JOB ----------------

@app.route("/admin/add-job", methods=["POST"])
def add_job():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    title = request.form.get("title", "").strip()
    company = request.form.get("company", "").strip()
    location = request.form.get("location", "").strip()
    job_type = request.form.get("type", "").strip()
    salary = request.form.get("salary", "").strip()
    skills = request.form.get("skills", "").strip()
    description = request.form.get("description", "").strip()

    if not all([title, company, location, job_type, salary, skills, description]):
        flash("Please complete all job fields.")
        return redirect(url_for("admin_dashboard"))

    new_id = max((job["id"] for job in jobs), default=0) + 1

    jobs.append({
        "id": new_id,
        "title": title,
        "company": company,
        "location": location,
        "type": job_type,
        "salary": salary,
        "skills": [skill.strip() for skill in skills.split(",") if skill.strip()],
        "description": description,
        "requirements": [
            "Relevant knowledge and skills",
            "Good communication skills",
            "Problem-solving ability"
        ]
    })

    flash("New job added successfully!")
    return redirect(url_for("admin_dashboard"))


# ---------------- EDIT JOB ----------------

@app.route("/admin/edit-job/<int:job_id>", methods=["POST"])
def edit_job(job_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    job = next((j for j in jobs if j["id"] == job_id), None)

    if not job:
        flash("Job not found.")
        return redirect(url_for("admin_dashboard"))

    title = request.form.get("title", "").strip()
    company = request.form.get("company", "").strip()
    location = request.form.get("location", "").strip()
    job_type = request.form.get("type", "").strip()
    salary = request.form.get("salary", "").strip()
    skills = request.form.get("skills", "").strip()
    description = request.form.get("description", "").strip()

    if not all([title, company, location, job_type, salary, skills, description]):
        flash("Please complete all edit fields.")
        return redirect(url_for("admin_dashboard"))

    job.update({
        "title": title,
        "company": company,
        "location": location,
        "type": job_type,
        "salary": salary,
        "skills": [s.strip() for s in skills.split(",") if s.strip()],
        "description": description
    })

    flash("Job updated successfully!")
    return redirect(url_for("admin_dashboard"))


# ---------------- DELETE JOB ----------------

@app.route("/admin/delete-job/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    global jobs, applications

    jobs = [j for j in jobs if j["id"] != job_id]
    applications = [
        a for a in applications if a["job_id"] != job_id
    ]

    flash("Job and its applications deleted.")
    return redirect(url_for("admin_dashboard"))


# ---------------- UPDATE APPLICATION STATUS ----------------

@app.route("/admin/application/<int:application_id>", methods=["POST"])
def update_application(application_id):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    new_status = request.form.get("status")

    if new_status not in ["Pending", "Accepted", "Rejected"]:
        flash("Invalid application status.")
        return redirect(url_for("admin_dashboard"))

    application = next(
        (a for a in applications if a["application_id"] == application_id),
        None
    )

    if application:
        application["status"] = new_status
        flash("Application status updated.")

    return redirect(url_for("admin_dashboard"))


# ---------------- ADMIN LOGOUT ----------------

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# ---------------- USER LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out successfully.")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)

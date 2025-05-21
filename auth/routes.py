from flask import Blueprint, request, redirect, url_for, session, render_template, flash
import cx_Oracle
from database import get_db_connection
auth = Blueprint("auth", __name__)
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db_connection()
        if not conn: 
            flash("Database connection error. Please try again later.", "danger")
            return redirect(url_for("auth.login"))
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM hr_users WHERE username = :1 AND password = :2", (username, password))
            user = cursor.fetchone()
        except cx_Oracle.DatabaseError as e:
            flash(f"Database error: {e}", "danger")
            user = None
        finally:
            cursor.close()
            conn.close()
        if user:
            session["hr_user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

  
        else:
            flash("Invalid credentials. Try again.", "danger")
    return render_template("login.html")
@auth.route("/logout")  
def logout():
    """Logout the HR user and redirect to login page"""
    session.pop("hr_user", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


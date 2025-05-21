from flask import Flask, session, redirect, url_for, render_template
from auth.routes import auth
from resume.routes import resume_bp
from rank.routes import rank_bp
app = Flask(__name__)
app.secret_key = "vellore_technology" 
app.register_blueprint(auth)
app.register_blueprint(resume_bp, url_prefix='/resume')
app.register_blueprint(rank_bp, url_prefix='/rank')
@app.route("/")
def home():
    """Welcome page before HR login"""
    return render_template("welcome.html")
@app.route("/dashboard")
def dashboard():
    """HR Dashboard after login"""
    if "hr_user" not in session:
        return redirect(url_for("auth.login")) 
    return render_template("dashboard.html")
if __name__ == "__main__":
    app.run(debug=True)

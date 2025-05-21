import os
import re
import spacy
import cx_Oracle
import PyPDF2
from flask import Blueprint, request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
from database import get_db_connection
resume_bp = Blueprint("resume", __name__)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf"}
nlp = spacy.load("en_core_web_sm")
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
def extract_resume_details(text):
    """Extract name, email, phone number, and skills from resume text"""
    doc = nlp(text)
    name = None
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text
            break
    email = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    email = email.group(0) if email else None
    phone = re.search(r"\b\d{10}\b", text)
    phone = phone.group(0) if phone else None
    skills = set()
    for chunk in doc.noun_chunks:
        if len(chunk.text) > 2:
            skills.add(chunk.text.lower())
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": ", ".join(skills)
    }
@resume_bp.route("/upload", methods=["GET", "POST"])
def upload_resume():
    if request.method == "POST":
        if "resume" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["resume"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            resume_text = extract_text_from_pdf(filepath)
            resume_data = extract_resume_details(resume_text)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO resumes (id, name, email, phone, skills) VALUES (resumes_seq.NEXTVAL, :1, :2, :3, :4)",
                (resume_data["name"], resume_data["email"], resume_data["phone"], resume_data["skills"])
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Resume uploaded and processed successfully!")
            return redirect(url_for("resume.upload_resume"))
        flash("Invalid file format. Only PDFs are allowed.")
    return render_template("upload.html")

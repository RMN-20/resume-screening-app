import cx_Oracle
import spacy
import numpy as np
from flask import Blueprint, request, render_template
from fuzzywuzzy import fuzz
from database import get_db_connection
from pyswarm import pso
import os
import PyPDF2
nlp = spacy.load("en_core_web_sm")
rank_bp = Blueprint("rank", __name__)
UPLOAD_FOLDER = "uploads"  
def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file"""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
        return text.strip() 
def extract_skills(text):
    """Extracts key skills using NLP"""
    doc = nlp(text.lower())
    skills = set(chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text) > 2)
    return skills
def objective_function(weights, job_skills, resume_skills):
    """Objective function for PSO-based resume ranking"""
    score = sum(weights[i] * fuzz.partial_ratio(job_skills[i], resume_skills[i]) for i in range(len(job_skills)))
    return -score  
@rank_bp.route("/", methods=["GET", "POST"])
def rank_resumes():
    if request.method == "POST":
        job_desc = request.form["job_description"]
        job_skills = list(extract_skills(job_desc))  
        resume_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith(".pdf")]
        ranked_resumes = []
        for resume_file in resume_files:
            resume_path = os.path.join(UPLOAD_FOLDER, resume_file)
            resume_text = extract_text_from_pdf(resume_path)
            resume_skills = list(extract_skills(resume_text))
            if not resume_skills:
                continue  
            lb = [0] * len(job_skills)  
            ub = [1] * len(job_skills)  
            best_weights, _ = pso(objective_function, lb, ub, args=(job_skills, resume_skills), swarmsize=10, maxiter=20)
            similarity_score = -objective_function(best_weights, job_skills, resume_skills)
            candidate_name = os.path.splitext(resume_file)[0]
            ranked_resumes.append((candidate_name, similarity_score))
        ranked_resumes.sort(key=lambda x: x[1], reverse=True)
        return render_template("results.html", resumes=ranked_resumes)
    return render_template("rank.html")

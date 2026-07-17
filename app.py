import os
import uuid
import re 

import fitz
from docx import Document
from flask import Flask, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Create the uploads folder automatically if it does not exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    """
    Check whether the uploaded file has an allowed extension.
    """
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file for backend processing.

    This text will not be shown directly to the user.
    """
    extracted_text = ""

    with fitz.open(pdf_path) as document:
        for page in document:
            extracted_text += page.get_text()

    return extracted_text


def extract_text_from_docx(docx_path):
    """
    Extract text from a DOCX file for backend processing.

    This text will not be shown directly to the user.
    """
    document = Document(docx_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)
def analyze_resume_text(resume_text):
    """
    Analyze extracted resume text using explainable,
    rule-based ATS-readiness checks.
    """
    text = resume_text.lower()
    word_count = len(resume_text.split())
    normalized_lines = [
    line.strip().lower()
    for line in resume_text.splitlines()
    if line.strip()
]
    
    score = 0
    strengths = []
    improvements = []

    # 1. Contact-information checks: 16 points
    email_pattern = r"[\w.+-]+@[\w-]+\.[\w.-]+"
    phone_pattern = r"(?:\+?\d[\d\s()-]{8,}\d)"

    has_email = bool(re.search(email_pattern, resume_text))
    has_phone = bool(re.search(phone_pattern, resume_text))

    if has_email:
        score += 8
        strengths.append("Email address detected.")
    else:
        improvements.append("Add a professional email address.")

    if has_phone:
        score += 8
        strengths.append("Phone number detected.")
    else:
        improvements.append("Add a valid phone number.")

    # 2. Essential resume sections: 32 points
    section_keywords = {
        "Education": ["education", "academic background"],
        "Experience": [
            "experience",
            "work experience",
            "employment"
        ],
        "Skills": [
            "skills",
            "technical skills",
            "core competencies"
        ],
        "Projects": [
            "projects",
            "academic projects",
            "personal projects"
        ]
    }

    detected_sections = []
    missing_sections = []

    for section_name, keywords in section_keywords.items():
        section_found = any(
    line == keyword or line.startswith(f"{keyword}:")
    for line in normalized_lines
    for keyword in keywords
)

        if section_found:
            score += 8
            detected_sections.append(section_name)
        else:
            missing_sections.append(section_name)
            improvements.append(
                f"Consider adding a {section_name} section."
            )

    if detected_sections:
        strengths.append(
            "Detected sections: "
            + ", ".join(detected_sections)
            + "."
        )

    # 3. Resume length: 15 points
    if 300 <= word_count <= 1000:
        score += 15
        strengths.append(
            f"Resume length is appropriate ({word_count} words)."
        )
    elif word_count < 300:
        improvements.append(
            f"The resume contains only {word_count} words. "
            "Add more relevant detail and achievements."
        )
    else:
        improvements.append(
            f"The resume contains {word_count} words. "
            "Consider making it more concise."
        )

    # 4. Action verbs: 15 points
    action_verbs = [
        "achieved",
        "built",
        "created",
        "developed",
        "designed",
        "implemented",
        "improved",
        "increased",
        "led",
        "managed",
        "optimized",
        "reduced"
    ]

    detected_action_verbs = [
        verb for verb in action_verbs
        if re.search(rf"\b{verb}\b", text)
    ]

    if len(detected_action_verbs) >= 5:
        score += 15
        strengths.append(
            "Uses several strong action verbs."
        )
    elif detected_action_verbs:
        score += 8
        improvements.append(
            "Use more action verbs to describe achievements."
        )
    else:
        improvements.append(
            "Begin experience and project points with action verbs."
        )

    # 5. Measurable achievements: 12 points
    achievement_pattern = (
        r"\b\d+(?:\.\d+)?%|"
        r"[$₹€£]\s?\d+|"
        r"\b\d+\+"
    )

    has_measurable_results = bool(
        re.search(achievement_pattern, resume_text)
    )

    if has_measurable_results:
        score += 12
        strengths.append(
            "Contains measurable or quantified achievements."
        )
    else:
        improvements.append(
            "Add numbers, percentages, or measurable outcomes "
            "to demonstrate impact."
        )

    # 6. Professional links: 10 points
    has_professional_link = (
        "linkedin.com" in text
        or "github.com" in text
        or "portfolio" in text
    )

    if has_professional_link:
        score += 10
        strengths.append(
            "Professional profile or portfolio link detected."
        )
    else:
        improvements.append(
            "Add a LinkedIn, GitHub, or portfolio link."
        )

    return {
        "score": min(score, 100),
        "word_count": word_count,
        "strengths": strengths,
        "improvements": improvements,
        "detected_sections": detected_sections,
        "missing_sections": missing_sections
    }



@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return "No resume file was received.", 400

    resume_file = request.files["resume"]

    if resume_file.filename == "":
        return "No file was selected.", 400

    if not allowed_file(resume_file.filename):
        return "Only PDF and DOCX files are supported.", 400

    original_filename = secure_filename(resume_file.filename)

    file_extension = original_filename.rsplit(".", 1)[1].lower()

    # Create a unique filename so different users' files do not overwrite each other
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"

    saved_file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    # Save the original uploaded resume
    resume_file.save(saved_file_path)

    # Extract text using the correct parser
    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(saved_file_path)

    elif file_extension == "docx":
        extracted_text = extract_text_from_docx(saved_file_path)

    else:
        return "Unsupported file format.", 400

    # Temporary backend check
    print("Extracted resume text:")
    print(extracted_text[:500])

    return redirect(
        url_for(
            "results_page",
            filename=unique_filename
        )
    )


@app.route("/results/<filename>")
def results_page(filename):
    saved_file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    if not os.path.exists(saved_file_path):
        return "Uploaded resume was not found.", 404

    file_extension = filename.rsplit(".", 1)[1].lower()

    if file_extension == "pdf":
        extracted_text = extract_text_from_pdf(saved_file_path)

    elif file_extension == "docx":
        extracted_text = extract_text_from_docx(saved_file_path)

    else:
        return "Unsupported file format.", 400

    analysis = analyze_resume_text(extracted_text)

    file_url = url_for(
        "static",
        filename=f"uploads/{filename}"
    )

    return render_template(
        "results.html",
        file_url=file_url,
        filename=filename,
        file_extension=file_extension,
        analysis=analysis
    )

if __name__ == "__main__":
    app.run(debug=True,port=5001)
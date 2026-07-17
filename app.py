import os
import uuid

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
    file_url = url_for(
        "static",
        filename=f"uploads/{filename}"
    )
    file_extension = filename.rsplit(".", 1)[1].lower()

    return render_template(
        "results.html",
        file_url=file_url,
        filename=filename,
        file_extension=file_extension
    )


if __name__ == "__main__":
    app.run(debug=True,port=5001)
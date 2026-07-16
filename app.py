from flask import Flask, render_template, request 

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")
@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    resume_file = request.files.get("resume")

    if resume_file is None or resume_file.filename == "":
        return "No resume file was selected.", 400

    return f"Resume received successfully: {resume_file.filename}"


if __name__ == "__main__":
    app.run(debug=True)
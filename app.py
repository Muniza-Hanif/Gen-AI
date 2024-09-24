from flask import Flask, request, render_template, send_file
from model import translate_text, extract_text_from_pdf, extract_text_from_docx, extract_text_from_image, query_content, recognize_speech, translate_file
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads/"

@app.route("/")
def index():
    return render_template("index.html")

# Translation Route for text input
@app.route("/translate", methods=["POST"])
def translate():
    text = request.form["text"]
    language = request.form["language"]
    translated_text = translate_text(text, language)
    return render_template("result.html", result=translated_text)

# Voice Translation Route
@app.route("/voice_translate", methods=["POST"])
def voice_translate():
    language = request.form["language"]
    voice_text = recognize_speech()
    translated_text = translate_text(voice_text, language)
    return render_template("result.html", result=translated_text, voice=True)

@app.route("/upload_file", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    # Determine file type
    file_type = file.filename.split('.')[-1].lower()
    query = request.form.get("query", "").strip()

    # Process PDF, DOCX, or Image file
    if file_type == "pdf":
        file_content = extract_text_from_pdf(file_path)
    elif file_type == "docx":
        file_content = extract_text_from_docx(file_path)
    elif file_type in ["jpg", "jpeg", "png"]:
        file_content = extract_text_from_image(file_path)
    else:
        return "Unsupported file format", 400

    if query:  # If the user asked a question related to the file
        response = query_content(file_content, query)
        return render_template("result.html", result=response)
    else:  # If no query, translate the entire file and return it
        translated_file_path = translate_file(file_path, file_content, file_type, request.form["language"])

        # Ensure the translated file path is correct and set the download_name
        return send_file(translated_file_path, as_attachment=True, download_name=os.path.basename(translated_file_path))

if __name__ == "__main__":
    app.run(debug=True)

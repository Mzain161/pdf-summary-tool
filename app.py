from flask import Flask, render_template, request
import fitz  # PyMuPDF
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/result', methods=['POST'])
def result():
    file = request.files['pdf']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    text = extract_text_from_pdf(filepath)
    short_summary = generate_summary(text)
    top_keywords = extract_keywords(text)

    return render_template('result.html', summary=short_summary, keywords=top_keywords)

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text

def generate_summary(text):
    sentences = text.split('.')
    short_summary = '. '.join(sentences[:5]) + '.' if len(sentences) >= 5 else text
    return short_summary

def extract_keywords(text):
    words = text.lower().split()
    common_words = ['the', 'is', 'and', 'to', 'in', 'of', 'a', 'for', 'on', 'with', 'as', 'at', 'this', 'that']
    filtered = [word for word in words if word.isalpha() and word not in common_words]
    top_keywords = list(set(filtered))[:10]
    return top_keywords

from flask import send_file
from io import BytesIO

@app.route('/download', methods=['POST'])
def download_summary():
    summary_text = request.form['summary']
    file_stream = BytesIO()
    file_stream.write(summary_text.encode('utf-8'))
    file_stream.seek(0)
    return send_file(file_stream, as_attachment=True, download_name='summary.txt', mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)


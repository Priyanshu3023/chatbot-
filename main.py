import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import google.generativeai as genai
from dotenv import load_dotenv
import fitz  # PyMuPDF for PDFs
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("API Key not found. Please set GEMINI_API_KEY in your .env file.")


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def extract_text_from_pdf(filepath):
    try:
        doc = fitz.open(filepath)
        return "\n".join([page.get_text() for page in doc]).strip()
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_image(filepath):
    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    user_text = request.form.get("text", "").strip()
    uploaded_file = request.files.get("file")

    try:
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)

            mimetype = uploaded_file.mimetype
            print(f"Uploaded file: {filename}, Mimetype: {mimetype}")

            if mimetype == "application/pdf":
                extracted_text = extract_text_from_pdf(filepath)
                if not extracted_text or "Error" in extracted_text:
                    return jsonify({'response': "No text could be extracted from the PDF."})

                prompt = f"{user_text}\n\nSummarize the following text:\n{extracted_text}" if user_text else f"Summarize the following text:\n{extracted_text}"
                response = model.generate_content({"parts": [{"text": prompt}]})
                return jsonify({'response': response.text})

            elif mimetype.startswith("image/"):
                extracted_text = extract_text_from_image(filepath)
                if not extracted_text or "Error" in extracted_text:
                    return jsonify({'response': "No readable text detected in the image."})

                prompt = f"{user_text}\n\nSummarize the following extracted text:\n{extracted_text}" if user_text else f"Summarize the following extracted text:\n{extracted_text}"
                response = model.generate_content({"parts": [{"text": prompt}]})
                return jsonify({'response': response.text})

            else:
                return jsonify({'response': "Only PDF and image files are supported."})

        elif user_text:
            response = model.generate_content({"parts": [{"text": user_text}]})
            return jsonify({'response': response.text})

        else:
            return jsonify({'response': 'Please provide a message or upload a file.'})

    except Exception as e:
        print("Error:", e)
        return jsonify({'response': f"Error processing your request: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)

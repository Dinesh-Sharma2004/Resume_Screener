from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import fitz  # PyMuPDF
from dotenv import load_dotenv

load_dotenv()


HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Please set HF_API_TOKEN in your environment variables.")

app = Flask(__name__)
CORS(app)

CLASS_MODEL_ID = "facebook/bart-large-mnli"
CLASS_API_URL = f"https://api-inference.huggingface.co/models/{CLASS_MODEL_ID}"

# For resume improvements (instruction-tuned text generation to output LaTeX)
IMPROVE_MODEL_ID = "google/flan-t5-base"
IMPROVE_API_URL = f"https://api-inference.huggingface.co/models/{IMPROVE_MODEL_ID}"

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text")
    except Exception as e:
        print(f"Error extracting text: {e}")
        return ""
    return text.strip()

def suggest_job_role(resume_text, candidate_labels):
    data = {
        "inputs": resume_text,
        "parameters": {
            "candidate_labels": candidate_labels,
            "multi_label": False
        }
    }
    response = requests.post(CLASS_API_URL, headers=HEADERS, json=data)
    if response.status_code == 200:
        result = response.json()
        if "labels" in result and "scores" in result and result["labels"]:
            best_index = result["scores"].index(max(result["scores"]))
            best_role = result["labels"][best_index]
            result["best_fitted_role"] = best_role
        return result
    else:
        return {"error": response.json()}

def get_improvements(resume_text):
    # Instruct the model to output a fully formatted LaTeX resume.
    prompt = (
        "Below is a resume. Rewrite and format this resume as an improved, fully formatted LaTeX document "
        "using a modern resume template. The LaTeX code should include clear sections for Contact Information, Summary, "
        "Education, Experience, Skills, and Projects, and be ready for compilation with pdflatex. Do not merely list suggestions; "
        "output the complete LaTeX source code for the improved resume.\n\n"
        "Resume:\n" + resume_text
    )
    data = {"inputs": prompt, "parameters": {"max_length": 1000}}
    response = requests.post(IMPROVE_API_URL, headers=HEADERS, json=data)
    
    # Debug logging
    print("Response status:", response.status_code)
    print("Response text:", response.text)
    
    if not response.text:
        return "Error: Received an empty response from the improvements API."
    
    try:
        result = response.json()
    except ValueError:
        return "Error: Unable to parse JSON from improvements API response: " + response.text

    if response.status_code == 200:
        if isinstance(result, list) and result:
            generated_text = result[0].get("generated_text", "")
            return generated_text if generated_text else "No improvements generated."
        else:
            return "No improvements generated."
    else:
        return "Error in generating improvements: " + str(result)

@app.route("/analyze", methods=["POST"])
def analyze_endpoint():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["resume"]
    if file.filename == "" or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Invalid file type. Only PDFs are allowed."}), 400
    candidate_labels_str = request.form.get("candidate_labels", "")
    if candidate_labels_str:
        candidate_labels = [label.strip() for label in candidate_labels_str.split(",") if label.strip()]
    else:
        candidate_labels = ["Data Scientist", "Software Engineer", "AI Researcher"]
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        if not resume_text:
            return jsonify({"error": "Could not extract text from the PDF"}), 500
        prediction = suggest_job_role(resume_text, candidate_labels)
        return jsonify({"job_suggestion": prediction, "extracted_text": resume_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

@app.route("/improve", methods=["POST"])
def improve_endpoint():
    if "resume" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["resume"]
    if file.filename == "" or not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Invalid file type. Only PDFs are allowed."}), 400
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        if not resume_text:
            return jsonify({"error": "Could not extract text from the PDF"}), 500
        improvements = get_improvements(resume_text)
        return jsonify({"improvements": improvements})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
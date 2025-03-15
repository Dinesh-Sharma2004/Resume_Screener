from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import json
import os
import nltk
nltk.download('punkt_tab')

app = Flask(__name__)
CORS(app)

# Load Llama model
MODEL_ID =  "google-bert/bert-base-uncased" 
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=os.environ.get("HF_TOKEN"))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu") #Check for CUDA availability
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
).to(device)

def generate_llama_response(prompt, max_length=1024):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=max_length,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract the model's response part only
    return response.split("Assistant: ")[-1].strip()

@app.route('/career_recommendations', methods=['POST'])
def career_recommendations():
    data = request.json
    academic_performance = data.get('academic_performance', '')
    interests = data.get('interests', '')
    skills = data.get('skills', '')
    
    prompt = f"""
    Human: I need personalized career recommendations based on the following information:
    
    Academic Performance: {academic_performance}
    Interests: {interests}
    Skills: {skills}
    
    Please analyze this information along with current market trends and provide:
    1. Suitable career paths (3-5 options)
    2. Relevant courses for each career path
    3. Certifications that would improve employability
    4. Projects that would strengthen my portfolio
    
    Format your response as a JSON with these categories.
    
    Assistant:
    """
    
    response = generate_llama_response(prompt)
    
    try:
        # Try to extract JSON from the response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        json_str = response[json_start:json_end]
        result = json.loads(json_str)
    except:
        # If JSON extraction fails, return a structured response
        result = {
            "career_paths": [
                {
                    "title": "Based on your profile, I recommend considering these career paths",
                    "options": ["Software Engineer", "Data Scientist", "Machine Learning Engineer"],
                    "courses": ["Python Programming", "Machine Learning Fundamentals", "Data Structures and Algorithms"],
                    "certifications": ["AWS Certified Developer", "TensorFlow Developer Certificate"],
                    "projects": ["Personal portfolio website", "Machine learning model for predicting market trends"]
                }
            ]
        }
    
    return jsonify(result)

@app.route('/resume_screening', methods=['POST'])
def resume_screening():
    data = request.json
    resume = data.get('resume', '')
    job_description = data.get('job_description', '')
    
    prompt = f"""
    Human: I need to optimize my resume for a job application.
    
    Here is my current resume:
    {resume}
    
    And here is the job description I'm applying for:
    {job_description}
    
    Please evaluate my resume against this job description and provide:
    1. Formatting improvements
    2. Keywords that should be added or emphasized
    3. Content suggestions to better match the job requirements
    4. A tailored version of my resume for this specific job
    
    Format your response as a JSON with these categories.
    
    Assistant:
    """
    
    response = generate_llama_response(prompt, max_length=2048)
    
    try:
        # Try to extract JSON from the response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        json_str = response[json_start:json_end]
        result = json.loads(json_str)
    except:
        # If JSON extraction fails, return a structured response
        result = {
            "formatting_improvements": [
                "Use bullet points for achievements",
                "Add section headers to improve readability",
                "Ensure consistent spacing throughout the document"
            ],
            "important_keywords": [
                "project management", "agile", "scrum", "data analysis"
            ],
            "content_suggestions": [
                "Quantify your achievements with metrics",
                "Add relevant technical skills section",
                "Tailor your summary to match the job requirements"
            ],
            "tailored_resume": "Please use the content suggestions to update your resume manually."
        }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port="7860",debug=True)

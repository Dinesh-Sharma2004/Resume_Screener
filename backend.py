from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import json

ollama.pull('mistral')
app = Flask(__name__)
CORS(app)

# Function to generate responses using Ollama

def generate_response(prompt, max_length=1024):
    response = ollama.chat(
        model="mistral",  # You can change this to other Ollama models
        messages=[{"role": "user", "content": prompt}],
        options={"max_length": max_length}
    )
    return response["message"]["content"].strip()

@app.route('/career_recommendations', methods=['POST'])
def career_recommendations():
    data = request.json
    academic_performance = data.get('academic_performance', '')
    interests = data.get('interests', '')
    skills = data.get('skills', '')
    
    prompt = f"""
    I need personalized career recommendations based on the following information:
    
    Academic Performance: {academic_performance}
    Interests: {interests}
    Skills: {skills}
    
    Please analyze this information along with current market trends and provide:
    1. Suitable career paths (1-5 options)
    2. Relevant courses for each career path
    3. Certifications that would improve employability
    4. Projects that would strengthen my portfolio
    
    Format your response as a JSON with these categories.
    """
    
    response = generate_response(prompt)
    
    try:
        result = json.loads(response)
    except:
        result = {"error": "Could not parse AI response as JSON"}
    
    return jsonify(result)

@app.route('/resume_screening', methods=['POST'])
def resume_screening():
    data = request.json
    resume = data.get('resume', '')
    job_description = data.get('job_description', '')
    
    prompt = f"""
    I need to optimize my resume for a job application.
    
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
    """
    
    response = generate_response(prompt, max_length=2048)
    
    try:
        result = json.loads(response)
    except:
        result = {"error": "Could not parse AI response as JSON"}
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)

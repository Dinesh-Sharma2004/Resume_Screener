import gradio as gr
import requests
import json
from utils import analyze_resume_match, extract_keywords

# Configure the backend URL
BACKEND_URL = "http://127.0.0.1:5000"  # Local development

def get_career_recommendations(academic_performance, interests, skills):
    """Get career recommendations from backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/career_recommendations",
            json={
                "academic_performance": academic_performance,
                "interests": interests,
                "skills": skills
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error: {response.status_code}", "message": response.text}
    except Exception as e:
        return {"error": str(e)}

def screen_resume(resume, job_description):
    """Screen resume using backend"""
    try:
        # Quick local analysis
        match_analysis = analyze_resume_match(resume, job_description)
        
        # Get detailed analysis from backend
        response = requests.post(
            f"{BACKEND_URL}/resume_screening",
            json={
                "resume": resume,
                "job_description": job_description
            },
            timeout=60
        )
        if response.status_code == 200:
            backend_results = response.json()
            # Combine local and backend analysis
            backend_results["match_analysis"] = match_analysis
            return backend_results
        else:
            return {"error": f"Error: {response.status_code}", "message": response.text}
    except Exception as e:
        return {"error": str(e)}

# Create Gradio interface
with gr.Blocks(title="Career and Resume Assistant") as demo:
    gr.Markdown("# Career and Resume Assistant")
    
    with gr.Tab("Career Recommendation"):
        gr.Markdown("## Personalized Career Recommendations")
        gr.Markdown("Analyze your academic performance, interests and skills to get tailored career path suggestions.")
        
        with gr.Row():
            with gr.Column():
                academic_input = gr.Textbox(
                    label="Academic Performance", 
                    placeholder="Describe your academic background, GPA, major courses, etc.",
                    lines=4
                )
                interests_input = gr.Textbox(
                    label="Interests", 
                    placeholder="What are your interests and passions?",
                    lines=3
                )
                skills_input = gr.Textbox(
                    label="Skills", 
                    placeholder="List technical and soft skills you possess",
                    lines=3
                )
                career_button = gr.Button("Get Career Recommendations", variant="primary")
            
            with gr.Column():
                career_output = gr.JSON(label="Career Recommendations")
    
    with gr.Tab("Resume Screening"):
        gr.Markdown("## AI Resume Screener and Optimizer")
        gr.Markdown("Get your resume analyzed and optimized for specific job applications.")
        
        with gr.Row():
            with gr.Column():
                resume_input = gr.Textbox(
                    label="Your Resume", 
                    placeholder="Paste your entire resume text here",
                    lines=10
                )
                job_desc_input = gr.Textbox(
                    label="Job Description", 
                    placeholder="Paste the job description you're applying for",
                    lines=7
                )
                resume_button = gr.Button("Analyze and Optimize Resume", variant="primary")
            
            with gr.Column():
                resume_output = gr.JSON(label="Resume Analysis and Suggestions")
    
    # Connect the buttons to the functions
    career_button.click(
        get_career_recommendations, 
        inputs=[academic_input, interests_input, skills_input], 
        outputs=career_output
    )
    
    resume_button.click(
        screen_resume, 
        inputs=[resume_input, job_desc_input], 
        outputs=resume_output
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()

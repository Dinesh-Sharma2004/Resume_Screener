import json
import requests
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def extract_keywords(text):
    """Extract important keywords from text"""
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    
    # Count word frequencies
    word_freq = {}
    for word in filtered_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Return top 10 words
    return [word for word, freq in sorted_words[:10]]

def fetch_job_trends(skills):
    """Fetch current job market trends (mock function)"""
    # In a real application, this would connect to a job API or database
    trends = {
        "python": {"demand": "High", "growth": "+15%", "avg_salary": "$120,000"},
        "java": {"demand": "Medium", "growth": "+5%", "avg_salary": "$110,000"},
        "data analysis": {"demand": "Very High", "growth": "+20%", "avg_salary": "$125,000"},
        "machine learning": {"demand": "Very High", "growth": "+25%", "avg_salary": "$135,000"},
        "web development": {"demand": "High", "growth": "+10%", "avg_salary": "$95,000"},
        
    }
    
    results = {}
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in trends:
            results[skill] = trends[skill_lower]
    
    return results

def analyze_resume_match(resume, job_description):
    """Analyze how well a resume matches a job description"""
    resume_keywords = extract_keywords(resume)
    job_keywords = extract_keywords(job_description)
    
    # Find matching keywords
    matching_keywords = [k for k in resume_keywords if k in job_keywords]
    
    # Calculate match percentage
    match_percentage = len(matching_keywords) / len(job_keywords) * 100 if job_keywords else 0
    
    # Missing important keywords
    missing_keywords = [k for k in job_keywords if k not in resume_keywords]
    
    return {
        "match_percentage": round(match_percentage, 2),
        "matching_keywords": matching_keywords,
        "missing_keywords": missing_keywords[:5]  # Top 5 missing keywords
    }

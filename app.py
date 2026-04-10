from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from symptom_parser import SymptomParser
from triage_engine import TriageEngine
from recommendation_engine import RecommendationEngine
from hospital_matcher import HospitalMatcher

app = Flask(__name__)
# In production, use a strong random secret key
app.secret_key = os.urandom(24) 

parser = SymptomParser()
triage = TriageEngine()
recommender = RecommendationEngine()
matcher = HospitalMatcher()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        symptoms = data.get('symptoms', '')
        age = data.get('age', '')
        gender = data.get('gender', '')
        location = data.get('location', '')
        
        # Sprint 2: Parse initial symptoms
        parsed_symptoms = parser.parse_symptoms(symptoms)
        
        # Sprint 4: Save initial context to session for follow-up questions
        session['parsed_symptoms'] = parsed_symptoms
        session['age'] = age
        session['gender'] = gender
        session['location'] = location
        session['raw_symptoms'] = symptoms
        
        print("--- Initial Triage Capture ---")
        print(f"Raw Symptoms: {symptoms}")
        print(f"Parsed Symptoms: {parsed_symptoms}")
        
        # Trigger redirect to follow-up questions page
        return jsonify({
            "status": "redirect",
            "url": url_for('questions')
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/questions', methods=['GET'])
def questions():
    # Only allow access if they've submitted symptoms
    if 'parsed_symptoms' not in session:
        return redirect(url_for('index'))
    return render_template('questions.html')

@app.route('/assess', methods=['POST'])
def assess():
    try:
        data = request.json
        base_symptoms = session.get('parsed_symptoms', [])
        saved_location = session.get('location', '')
        
        # Extract Yes/No answers and map them directly into symptoms
        explicit_findings = []
        if data.get('breathing_difficulty') == 'yes':
            explicit_findings.append('shortness_of_breath')
        if data.get('bleeding') == 'yes':
            explicit_findings.append('bleeding')
        if data.get('unconsciousness') == 'yes':
            explicit_findings.append('unconscious')
        if data.get('severe_pain') == 'yes':
            explicit_findings.append('chest_pain') # Assuming severe unlocalized pain routes to urgent/emergency path mapping
        if data.get('pregnancy') == 'yes':
            explicit_findings.append('pregnancy')
        if data.get('child') == 'yes':
            explicit_findings.append('child')
            
        combined_symptoms = list(set(base_symptoms + explicit_findings))
        
        # Sprint 3/4: Determine accurate urgency mapping
        urgency = triage.determine_urgency(combined_symptoms)
        
        # Sprint 5: Generate Doctor/Department and Action Recommendations
        recommendation = recommender.get_recommendation(combined_symptoms, urgency['level'])
        
        # Sprint 6: Find Matching Hospitals
        hospitals = matcher.find_hospitals(saved_location, recommendation['department'], urgency['level'])
        
        # Final log
        print("--- Final Triage Assessment ---")
        print(f"Combined Symptoms Context: {combined_symptoms}")
        print(f"Urgency Result: {urgency['level']} {urgency['color']}")
        print(f"Recommended Dept: {recommendation['department']}")
        print(f"Immediate Action: {recommendation['action']}")
        print(f"Found Hospitals: {len(hospitals)}")
        print("-------------------------------")
        
        return jsonify({
            "status": "success",
            "message": "Final assessment complete.",
            "combined_symptoms": combined_symptoms,
            "urgency": urgency,
            "recommendation": recommendation,
            "hospitals": hospitals
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)

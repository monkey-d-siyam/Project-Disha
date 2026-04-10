from __future__ import annotations
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
from symptom_parser import SymptomParser
from triage_engine import TriageEngine
from recommendation_engine import RecommendationEngine
from hospital_matcher import HospitalMatcher

app = Flask(__name__)
# Use stable secret key from environment; fallback for local dev only
app.secret_key = os.environ.get('DISHA_SECRET_KEY', 'disha-dev-local-secret-2024')

parser = SymptomParser()
triage = TriageEngine()
recommender = RecommendationEngine()
matcher = HospitalMatcher()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    """Sprint 9: System health check — verifies all modules are loaded."""
    return jsonify({
        "status": "ok",
        "modules": {
            "symptom_parser": parser is not None,
            "triage_engine": triage is not None,
            "recommendation_engine": recommender is not None,
            "hospital_matcher": matcher is not None and len(matcher.hospitals) > 0
        },
        "hospital_count": len(matcher.hospitals)
    }), 200

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "error", "message": "Invalid or missing JSON body."}), 400

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
    
    age_raw = session.get('age')
    gender = session.get('gender', '').lower()
    symptoms = session.get('parsed_symptoms', [])
    
    # Try to clean age
    age = None
    try: age = int(age_raw)
    except: pass
    
    # Define clinical follow-up questions with adaptive logic and Bangla support
    all_questions = [
        {
            "id": "breathing_difficulty",
            "en": "Are you experiencing severe breathing difficulty?",
            "bn": "আপনার কি শ্বাস নিতে তীব্র কষ্ট হচ্ছে?",
            "relevant": True
        },
        {
            "id": "bleeding",
            "en": "Is there severe or active bleeding?",
            "bn": "তীব্র বা সক্রিয় রক্তপাত কি হচ্ছে?",
            "relevant": True
        },
        {
            "id": "unconsciousness",
            "en": "Did the patient act confused or experience unconsciousness?",
            "bn": "রোগী কি বিভ্রান্ত কাজ করছেন বা অচেতন হয়ে পড়েছেন?",
            "relevant": True
        },
        {
            "id": "severe_pain",
            "en": "Are you experiencing severe, unbearable pain?",
            "bn": "আপনার কি প্রচণ্ড, অসহ্য ব্যথা হচ্ছে?",
            "relevant": True
        },
        {
            "id": "pregnancy",
            "en": "Are you currently pregnant?",
            "bn": "আপনি কি বর্তমানে গর্ভবতী?",
            "relevant": (gender == 'female' and (age is None or 12 <= age <= 55))
        },
        {
            "id": "dengue_signals",
            "en": "Do you have a skin rash or severe pain behind the eyes?",
            "bn": "আপনার কি শরীরে র‍্যাশ বা চোখের পিছনে প্রচণ্ড ব্যথা আছে?",
            "relevant": ('fever' in symptoms)
        },
        {
            "id": "dehydration_signals",
            "en": "Have you noticed very dark urine, dry mouth, or extreme thirst?",
            "bn": "আপনার কি খুব গাঢ় প্রস্রাব, মুখ শুকিয়ে যাওয়া বা তীব্র তৃষ্ণা অনুভব হচ্ছে?",
            "relevant": ('vomiting' in symptoms or 'stomach_pain' in symptoms)
        },
        {
            "id": "child",
            "en": "Is the patient a child under 12 years old?",
            "bn": "রোগী কি ১২ বছরের নিচের শিশু?",
            "relevant": (age_raw is None)
        }
    ]
    
    # Filter only relevant questions
    relevant_questions = [q for q in all_questions if q['relevant']]
    
    return render_template('questions.html', questions=relevant_questions)

@app.route('/assess', methods=['POST'])
def assess():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "error", "message": "Invalid or missing JSON body."}), 400

        base_symptoms = session.get('parsed_symptoms', [])
        saved_location = session.get('location', '')
        
        # Extract Yes/No answers and map them directly into symptoms
        explicit_findings = []
        
        # Helper to safely get form data, defaulting to 'no' if the question was filtered out/not asked
        def check_yes(key):
            return data.get(key) == 'yes'

        if check_yes('breathing_difficulty'):
            explicit_findings.append('shortness_of_breath')
        if check_yes('bleeding'):
            explicit_findings.append('bleeding')
        if check_yes('unconsciousness'):
            explicit_findings.append('unconscious')
        if check_yes('severe_pain'):
            explicit_findings.append('severe_pain')
        if check_yes('pregnancy'):
            explicit_findings.append('pregnancy')
        if check_yes('dengue_signals'):
            explicit_findings.append('rash')
        if check_yes('dehydration_signals'):
            explicit_findings.append('weakness')
        
        # Priority check: If the question wasn't asked but age was provided as < 12
        is_child = check_yes('child')
        if not is_child and session.get('age'):
            try:
                if int(session.get('age')) < 12:
                    is_child = True
            except: pass
            
        if is_child:
            explicit_findings.append('child')
            
        combined_symptoms = list(set(base_symptoms + explicit_findings))
        
        # Determine accurate urgency mapping
        urgency = triage.determine_urgency(combined_symptoms)
        
        # Generate Doctor/Department and Action Recommendations
        recommendation = recommender.get_recommendation(combined_symptoms, urgency['level'])
        
        # Find Matching Hospitals
        hospitals = matcher.find_hospitals(saved_location, recommendation['department'], urgency['level'])
        
        # Explicit Emergency Flag for Demo UI
        is_emergency = (urgency['level'] == "Emergency")

        return jsonify({
            "status": "success",
            "message": "Final assessment complete.",
            "combined_symptoms": combined_symptoms,
            "urgency": urgency,
            "recommendation": recommendation,
            "hospitals": hospitals,
            "is_emergency": is_emergency
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)

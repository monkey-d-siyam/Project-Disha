from __future__ import annotations
class TriageEngine:
    def __init__(self):
        # We define severity based on specific symptom combinations or individual symptoms
        pass

    def determine_urgency(self, parsed_symptoms: list[str]) -> dict:
        if not parsed_symptoms:
            return {"level": "Home Care", "color": "🟢", "description": "No symptoms provided. Rest and monitor your condition."}
            
        s = set(parsed_symptoms)
        
        # 1. EMERGENCY (Demo Scope: Cardiac/Pregnancy Only)
        is_cardiac = (("chest_pain" in s or "chest_tightness" in s) and "shortness_of_breath" in s)
        is_pregnancy = ("pregnancy" in s)
        
        if is_cardiac or is_pregnancy:
            return {
                "level": "Emergency", 
                "color": "🔴", 
                "description": "High-risk condition detected (Cardiac/Obstetric). Immediate medical attention is vital."
            }
            
        # 2. URGENT
        # significant issues that aren't the specific demo cardiac/pregnancy triggers
        is_urgent = (
            "unconscious" in s or 
            "bleeding" in s or 
            "chest_pain" in s or 
            "shortness_of_breath" in s or 
            "chest_tightness" in s or 
            "burn" in s or 
            "cut" in s or
            ("fever" in s and ("vomiting" in s or "child" in s or "rash" in s)) or
            ("vomiting" in s and "weakness" in s)
        )
        
        if is_urgent:
            return {
                "level": "Urgent", 
                "color": "🟠", 
                "description": "Needs medical attention soon. Visit a clinic or urgent care."
            }

        # 3. ROUTINE
        is_routine = (
            "stomach_pain" in s or 
            "back_pain" in s or 
            "leg_pain" in s or 
            "blurry_vision" in s or 
            "dizziness" in s or 
            "child" in s or 
            "severe_pain" in s
        )
        
        if is_routine:
            return {
                "level": "Routine", 
                "color": "🔵", 
                "description": "Stable condition. Schedule an appointment with a doctor within a few days."
            }
            
        # 4. DEFAULT
        return {
            "level": "Home Care", 
            "color": "🟢", 
            "description": "Manageable at home with over-the-counter remedies and rest."
        }

    def _check_conditions(self, symptoms_set: set, conditions_list: list) -> bool:
        """Helper method to check if any condition in the list is met by the symptoms set."""
        for condition in conditions_list:
            if isinstance(condition, str):
                if condition in symptoms_set:
                    return True
            elif isinstance(condition, set):
                # Check if all elements in the set are present in symptoms_set
                if condition.issubset(symptoms_set):
                    return True
        return False

# Standalone test
if __name__ == '__main__':
    engine = TriageEngine()
    print(engine.determine_urgency(["headache", "fever"])) # Should be Home Care
    print(engine.determine_urgency(["stomach_pain"])) # Should be Routine
    print(engine.determine_urgency(["chest_pain"])) # Should be Urgent
    print(engine.determine_urgency(["chest_pain", "shortness_of_breath"])) # Should be Emergency

from __future__ import annotations
class TriageEngine:
    def __init__(self):
        # We define severity based on specific symptom combinations or individual symptoms
        pass

    def determine_urgency(self, parsed_symptoms: list[str]) -> dict:
        """
        Takes a list of structured symptoms and returns the urgency level determination.
        """
        if not parsed_symptoms:
            return {"level": "Home Care", "color": "🟢", "description": "No symptoms provided. Rest and monitor your condition."}
            
        symptoms_set = set(parsed_symptoms)
        
        # 1. Check for Emergency scenarios first (Highest Priority)
        # Conditions: unconscious, or combination of severe symptoms
        emergency_conditions = [
            "unconscious",
            {"chest_pain", "shortness_of_breath"},
            {"shortness_of_breath", "chest_tightness"},
            {"bleeding", "weakness"}
        ]
        
        if self._check_conditions(symptoms_set, emergency_conditions):
            return {
                "level": "Emergency", 
                "color": "🔴", 
                "description": "Immediate life-threatening condition. Seek emergency medical care immediately."
            }
            
        # 2. Check for Urgent scenarios
        # Conditions: significant but not immediately life-limiting unless it worsens
        urgent_conditions = [
            "chest_pain",
            "shortness_of_breath",
            "bleeding",
            "burn",
            "chest_tightness",
            {"vomiting", "fever"},
            {"child", "fever"},   # child with fever is clinically Urgent
            "cut"
        ]
        
        if self._check_conditions(symptoms_set, urgent_conditions):
            return {
                "level": "Urgent", 
                "color": "🟠", 
                "description": "Needs medical attention soon. Visit a clinic or urgent care."
            }

        # 3. Check for Routine scenarios
        # Conditions: stable issues that require a doctor's visit
        routine_conditions = [
            "stomach_pain",
            "back_pain",
            "leg_pain",
            "blurry_vision",
            "dizziness",
            "pregnancy",
            "child"
        ]
        
        if self._check_conditions(symptoms_set, routine_conditions):
            return {
                "level": "Routine", 
                "color": "🔵", 
                "description": "Stable condition. Schedule an appointment with a doctor within a few days."
            }
            
        # 4. Default to Home Care if it's minor symptoms
        # Conditions: cold, cough, fever, headache, rash, sweating, weakness
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

class RecommendationEngine:
    def __init__(self):
        # Basic mapping of priority symptoms to specialized departments
        self.department_map = {
            "chest_pain": "Cardiology",
            "chest_tightness": "Cardiology",
            "shortness_of_breath": "Pulmonology",
            "unconscious": "Neurology",
            "headache": "Neurology",
            "dizziness": "Neurology",
            "stomach_pain": "Gastroenterology",
            "vomiting": "Gastroenterology",
            "back_pain": "Orthopedics",
            "leg_pain": "Orthopedics",
            "blurry_vision": "Ophthalmology",
            "pregnancy": "Obstetrics & Gynecology",
            "child": "Pediatrics",
            "burn": "Dermatology / Emergency",
            "rash": "Dermatology",
            "cut": "Surgery / Emergency",
            "bleeding": "Surgery / Emergency"
        }

    def get_recommendation(self, symptoms: list[str], urgency_level: str) -> dict:
        """
        Determines the appropriate doctor/department and an immediate action directive.
        """
        department = "General Physician"
        
        # Determine department based on symptoms.
        # We can just pick the first mapped department found in the symptoms list, 
        # or prioritize based on some logic. Since we just need A primary recommendation,
        # we iterate and take the first match. In a real app we'd weight them.
        for symptom in symptoms:
            if symptom in self.department_map:
                department = self.department_map[symptom]
                # If they have multiple, we just take the first mapped one for simplicity. 
                # (e.g. chest pain + headache -> Cardiology)
                break
                
        # Determine immediate action based on urgency level
        action = "Monitor your symptoms."
        if urgency_level == "Emergency":
            action = "Call an ambulance immediately or rush to the nearest Emergency Room. Do not wait."
            if department == "General Physician":
                # Override general physician to emergency medicine if it's an emergency
                department = "Emergency Medicine"
        elif urgency_level == "Urgent":
            action = "Please visit an Urgent Care clinic or exactly the recommended hospital department within the next few hours."
        elif urgency_level == "Routine":
            action = "Schedule an appointment with the recommended doctor within the next 48 hours."
        elif urgency_level == "Home Care":
            action = "Rest, stay hydrated, and use appropriate over-the-counter medication. Consult a doctor if symptoms worsen."

        return {
            "department": department,
            "action": action
        }

# Standalone execution
if __name__ == '__main__':
    engine = RecommendationEngine()
    print(engine.get_recommendation(["chest_pain", "fever"], "Emergency"))
    print(engine.get_recommendation(["rash"], "Home Care"))

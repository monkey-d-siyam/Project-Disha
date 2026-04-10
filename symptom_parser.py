from __future__ import annotations
import re

class SymptomParser:
    def __init__(self):
        # Dictionary mapping keywords/phrases to structured symptoms
        self.symptom_map = {
            "chest_pain": ["buk betha", "buke batha", "bukebatha", "chest pain", "pain in chest"],
            "shortness_of_breath": ["shash nite koshto", "shash kosto", "shashkosto", "shortness of breath", "breathing issue", "nisash nite kosto", "kosto hocche shash nite", "breathing difficulty", "shwas nite parchhi na", "shwas nite", "shwas", "nisash", "cant breathe", "can t breathe", "breathe"],
            "fever": ["jor", "jwor", "fever", "tapmatra", "high temperature", "temperature"],
            "headache": ["matha betha", "matha batha", "matha byatha", "headache", "mathabatha", "head ache"],
            "stomach_pain": ["pet betha", "pet batha", "petebatha", "stomach pain", "stomach ache", "belly ache"],
            "cough": ["kashi", "kasi", "cough", "coughing"],
            "weakness": ["durbol", "weakness", "weak", "klanto", "fatigue", "tiredness"],
            "dizziness": ["matha ghora", "matha ghura", "matha ghurchhe", "dizziness", "dizzy", "vertigo", "chokkor"],
            "vomiting": ["bomi", "vomiting", "vomit", "puke", "throw up", "bomi asche"],
            "back_pain": ["komor betha", "pith betha", "back pain", "merudondo betha", "peeth betha"],
            "bleeding": ["rokto", "bleeding", "blood", "roktopat", "rokto pora"],
            "burn": ["pora", "pure geche", "burn", "burnt", "agune pura"],
            "unconscious": ["oggan", "agyian", "unconscious", "faint", "senseless", "behus", "behudh"],
            "leg_pain": ["pa betha", "pa batha", "leg pain", "payer betha"],
            "cold": ["thanda", "sordi", "cold"],
            "cut": ["kete geche", "kata", "cut", "kete gese"],
            "chest_tightness": ["buke chap", "chest tightness", "buk dhorphor", "palpitation"],
            "sweating": ["gham", "ghamche", "sweat", "sweating"],
            "rash": ["chulkani", "rash", "allergy", "allergi"],
            "blurry_vision": ["jhapsa", "chokhe jhapsa", "blurry vision", "kom dekhchi"]
        }
        
    def parse_symptoms(self, text: str) -> list[str]:
        if not text:
            return []
            
        # Convert text to lowercase and remove common punctuation for basic matching
        clean_text = text.lower()
        clean_text = re.sub(r'[^\w\s]', ' ', clean_text)
        
        detected_symptoms = set()
        
        for symptom_key, keywords in self.symptom_map.items():
            for keyword in keywords:
                # We use regex word boundary to avoid matching "fever" inside "feverish" if it's not intended,
                # but simple `keyword in text` is often robust enough for transliteration misspellings.
                # Let's try simple inclusion first, or regex word boundary.
                # Regex boundary works well, but we need to handle multi-word keywords.
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, clean_text):
                    detected_symptoms.add(symptom_key)
                    # We can break early for this symptom_key if we found a match
                    break
                    
        return list(detected_symptoms)

# Simple standalone test
if __name__ == "__main__":
    parser = SymptomParser()
    test_cases = [
        "buk betha + shash nite koshto",
        "amar matha batha korche",
        "severe chest pain and fever",
        "pure geche hath"
    ]
    for case in test_cases:
        print(f"Input: '{case}' -> Parsed: {parser.parse_symptoms(case)}")

from __future__ import annotations
import json
import os

class HospitalMatcher:
    def __init__(self, json_path: str | None = None):
        # Resolve path relative to this module's directory so it works
        # regardless of which directory Flask is launched from.
        if json_path is None:
            json_path = os.path.join(os.path.dirname(__file__), 'hospitals.json')
        # Load the dataset
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                self.hospitals: list[dict] = json.load(f)
        else:
            self.hospitals: list[dict] = []

    def find_hospitals(self, location_query: str, target_department: str, urgency_level: str) -> list[dict]:
        """
        Filters and prioritizes hospitals based on location, department, and emergency needs.
        Returns a sorted list of top match dictionaries.
        """
        if not self.hospitals:
            return []
            
        location_query = location_query.lower().strip() if location_query else ""
        
        # 1. Filter by location (soft match)
        # If the user put a location, try to match it. If no hospitals match, gracefully fall back to all.
        location_matches = [
            h for h in self.hospitals 
            if location_query in h['location'].lower() or h['location'].lower() in location_query
        ]
        
        pool = location_matches if location_matches else self.hospitals
        
        # 2. Score the hospitals
        scored_hospitals = []
        for h in pool:
            score = 0
            
            # Emergency context rule: Must route safely
            is_emergency = urgency_level == "Emergency" or target_department in ["Emergency Medicine", "Surgery / Emergency"]
            if is_emergency and not h.get('has_er'):
                # Heavily penalize or outright skip non-ER hospitals for life-threatening issues
                continue
                
            if is_emergency and h.get('has_er'):
                score += 50
                
            # Department match rule
            # If the specific department aligns, boost score
            if target_department in h.get('departments', []):
                score += 30
            elif "General Physician" in h.get('departments', []):
                # Fallback bump for general practice availability
                score += 10
                
            scored_hospitals.append({
                "hospital": h,
                "score": score
            })
            
        # 3. Sort by score descending and return top 3
        # Exclude score from final payload, just return the hospital dict
        scored_hospitals.sort(key=lambda x: x["score"], reverse=True)
        
        top_results = [item["hospital"] for item in scored_hospitals[:3]]
        
        return top_results

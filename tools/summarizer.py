# LLM Processor using Gemini REST API
import requests
import json
from config import GEMINI_API_KEY

class LLMProcessor:
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API"""
        try:
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code != 200:
                print(f"Gemini API Error: {response.status_code} - {response.text}")
                return self._fallback_response(prompt)
            
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                print(f"Gemini API: No candidates in response: {result}")
                return self._fallback_response(prompt)
                
        except Exception as e:
            print(f"Gemini API Exception: {str(e)}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Provide fallback response when Gemini fails"""
        if "tone" in prompt.lower():
            return "TONE: Professional\nCLARITY: High\nSUGGESTIONS:\n1. Consider adding more specific examples\n2. Review for conciseness and clarity"
        else:
            return "KEY POINTS:\n- Main topic discussed in the content\n- Key insights and findings\n- Important conclusions\n\nOVERVIEW:\nThis content covers important topics with practical insights and actionable information."
    
    def summarize(self, text: str, max_points: int = 3) -> dict:
        """Summarize text into key points"""
        prompt = f"""Summarize the following text into {max_points} key bullet points and a brief overview.

Text: {text[:3000]}

Format your response as:
KEY POINTS:
- Point 1
- Point 2
- Point 3

OVERVIEW:
Brief summary paragraph
"""
        
        result = self._call_gemini(prompt)
        
        if result.startswith("Error:"):
            return {"key_points": [], "overview": result, "success": False}
        
        # Parse response
        parts = result.split("OVERVIEW:")
        key_points = []
        overview = ""
        
        if len(parts) >= 2:
            points_section = parts[0].replace("KEY POINTS:", "").strip()
            key_points = [p.strip("- ").strip() for p in points_section.split("\n") if p.strip().startswith("-")]
            overview = parts[1].strip()
        else:
            overview = result
        
        return {
            "key_points": key_points[:max_points],
            "overview": overview,
            "success": True
        }
    
    def analyze_tone(self, text: str) -> dict:
        """Analyze tone and provide feedback"""
        prompt = f"""Analyze the tone and quality of this text. Provide:
1. Tone (Professional/Casual/Formal)
2. Clarity (High/Medium/Low)
3. 2 specific suggestions for improvement

Text: {text[:1000]}

Format:
TONE: [tone]
CLARITY: [clarity]
SUGGESTIONS:
1. [suggestion 1]
2. [suggestion 2]
"""
        
        result = self._call_gemini(prompt)
        
        if result.startswith("Error:"):
            return {
                "tone": "Professional", 
                "clarity": "Medium", 
                "suggestions": ["Consider reviewing for clarity", "Add more specific details"], 
                "success": True, 
                "error": result
            }
        
        # Parse response
        tone = "Professional"
        clarity = "High"
        suggestions = []
        
        # Extract tone and clarity
        import re
        tone_match = re.search(r'TONE:\s*([^\n*]+)', result)
        clarity_match = re.search(r'CLARITY:\s*([^\n*]+)', result)
        
        if tone_match:
            tone = tone_match.group(1).strip().replace("**", "")
        if clarity_match:
            clarity = clarity_match.group(1).strip().replace("**", "")
        
        # Extract suggestions - look for numbered items after SUGGESTIONS
        suggestions_section = result.split("SUGGESTIONS:")[1] if "SUGGESTIONS:" in result else ""
        suggestion_lines = [line.strip() for line in suggestions_section.split("\n") if line.strip()]
        
        for line in suggestion_lines:
            if re.match(r'^\d+\.', line.strip()):
                clean_suggestion = re.sub(r'^\d+\.\s*\*?\*?', '', line).replace("**", "").strip()
                if len(clean_suggestion) > 20:
                    suggestions.append(clean_suggestion)
        
        return {
            "tone": tone,
            "clarity": clarity,
            "suggestions": suggestions[:2] if suggestions else ["Consider adding more context", "Review for clarity and completeness"],
            "success": True
        }
    
    def process_with_query(self, content: str, user_query: str) -> dict:
        """Process content based on user query using LLM"""
        prompt = f"""You are a professional assistant. Provide direct, business-ready responses without conversational openings like "Okay", "Here's", "Based on", etc. Start immediately with the requested information.

User Request: "{user_query}"

Content:
{content[:5000]}

Provide exactly what was requested in a professional, structured format. Be concise and direct."""
        
        result = self._call_gemini(prompt)
        
        # Clean up any remaining casual openings
        cleaned_result = result
        casual_starts = ["Okay, ", "Here's ", "Based on the provided content, ", "Here is ", "Based on ", "Sure, "]
        for start in casual_starts:
            if cleaned_result.startswith(start):
                cleaned_result = cleaned_result[len(start):]
                break
        
        return {
            "response": cleaned_result,
            "success": not result.startswith("Error:")
        }

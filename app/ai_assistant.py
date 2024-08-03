import os
from dotenv import load_dotenv
import requests

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

class AI_Assistant:
    def __init__(self):
        self.gemini_api_key = gemini_api_key

        # Initial prompt
        self.full_transcript = [
            {"role": "system", "content": "You have to suggest three recipes I can make. Here are the ingredients: _____, you have to only generate a 4-line paragraph only. "},
        ]

    def generate_ai_response(self, transcript_text):
        transcript_str = ', '.join([f"{item['name']} ({item['quantity']})" for item in transcript_text])
        prompt_text = (f"You have to suggest three recipes I can make. Here are the ingredients: {transcript_str}. "
                    "You have to generate only a 4-line paragraph only. Make proper headings and bullets for them; "
                    "don't use asterisks (*). For each suggestion, return each suggestion within <p> </p> tags.")

        self.full_transcript.append({"role": "user", "content": prompt_text})
        print(f"\nUser: {prompt_text}")

        response = self.query_gemini(prompt_text)

        if response:
            try:
                ai_response = response['candidates'][0]['content']['parts'][0]['text']
                if ai_response:
                    formatted_response = ai_response.replace('\n', '<br>').replace('\n\n', '</p><p>')
                    formatted_response = formatted_response.replace('**', '<strong>').replace('</strong><strong>', '</strong><strong>')
                    formatted_response = f"<p>{formatted_response}</p>"
                    return [formatted_response]  
                else:
                    print("Received empty AI response")
                    return ["Sorry, I couldn't generate a response."]
            except (IndexError, KeyError) as e:
                print(f"Error parsing AI response: {e}")
                return ["Sorry, I couldn't generate a response."]
        else:
            return ["Sorry, I couldn't understand the question."]

    def query_gemini(self, text):
        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": text}
                    ]
                }
            ]
        }

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={self.gemini_api_key}"
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error querying AI service: {e}")
            return None

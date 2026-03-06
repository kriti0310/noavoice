import requests
from app.config.settings import settings


class ElevenLabsService:

    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self):
        self.api_key = settings.ELEVEN_LABS_API_KEY
        self.headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        print("LOADED KEY:", self.api_key)
        
    def get_voices(self):
        response = requests.get(
            f"{self.BASE_URL}/voices",
            headers=self.headers
        )

        data = response.json()

        voices = []

        for voice in data.get("voices", []):
            voices.append({
                "voice_id": voice.get("voice_id"),
                "name": voice.get("name"),
                "gender": voice.get("labels", {}).get("gender"),
                "accent": voice.get("labels", {}).get("accent"),
                "age": voice.get("labels", {}).get("age"),
                "description": voice.get("description"),
                "preview_url": voice.get("preview_url")
            })

        return {"voices": voices}
        

    def text_to_speech(self, voice_id: str, text: str) -> bytes:

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "xi-api-key": settings.ELEVEN_LABS_API_KEY,
            "Content-Type": "application/json",
            "accept": "audio/mpeg"
        }

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            print("ELEVEN ERROR:", response.text)
            return None

        return response.content
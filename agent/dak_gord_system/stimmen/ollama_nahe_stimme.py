import os
import requests
from typing import List, Dict, Any


class OllamaNaheStimme:
    def __init__(self):
        self.url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.modell = os.environ.get("OLLAMA_MODELL", "qwen2.5-coder:14b")

    def chat(self, nachrichten: List[Dict[str, str]], temperatur: float = 0.25) -> str:
        antwort = requests.post(
            f"{self.url}/api/chat",
            json={
                "model": self.modell,
                "stream": False,
                "messages": nachrichten,
                "options": {"temperature": temperatur},
            },
            timeout=180,
        )
        antwort.raise_for_status()
        daten: Dict[str, Any] = antwort.json()
        return daten["message"]["content"]

import google.generativeai as genai
from app.config.settings import settings
from app.core.prompts import get_chat_prompt
import json
import os
from typing import List, Dict
import uuid

class ChatbotService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def _load_chat_history(self, session_id: str) -> List[Dict]:
        """Load chat history from file."""
        history_file = os.path.join(settings.CHAT_HISTORY_DIR, f"{session_id}.json")
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_chat_history(self, session_id: str, history: List[Dict]):
        """Save chat history to file."""
        os.makedirs(settings.CHAT_HISTORY_DIR, exist_ok=True)
        history_file = os.path.join(settings.CHAT_HISTORY_DIR, f"{session_id}.json")
        with open(history_file, 'w') as f:
            json.dump(history, f)
    
    async def process_message(self, message: str, session_id: str = None) -> tuple[str, str, List[Dict]]:
        """Process a message and return response with session ID and history."""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        history = self._load_chat_history(session_id)
        
        # Generate prompt
        prompt = get_chat_prompt(history, message)
        
        # Get response from Gemini
        response = self.model.generate_content(prompt)
        
        # Update history
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response.text})
        
        # Save updated history
        self._save_chat_history(session_id, history)
        
        return response.text, session_id, history 
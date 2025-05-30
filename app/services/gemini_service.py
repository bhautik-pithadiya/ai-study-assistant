import base64
import google.generativeai as genai
from core.config import API_KEY, MODEL_NAME, GENERATION_CONFIG, SYSTEM_PROMPT

class GeminiService:
    def __init__(self):
        """Initialize Gemini service with API key"""
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel(MODEL_NAME)

    async def generate_answer(self, image_content: bytes, image_mime_type: str, text: str = "") -> str:
        """
        Generate answer using Gemini model
        
        Args:
            image_content (bytes): The image content
            image_mime_type (str): The MIME type of the image
            text (str): Optional text context
            
        Returns:
            str: The generated answer
        """
        # Prepare the image for Gemini
        image_parts = [
            {
                "mime_type": image_mime_type,
                "data": base64.b64encode(image_content).decode('utf-8')
            }
        ]
        
        # Combine system prompt with user's text if provided
        prompt = SYSTEM_PROMPT
        if text:
            prompt += f"\n\nAdditional context: {text}"
        
        # Generate response
        response = self.model.generate_content(
            contents=[prompt, *image_parts],
            generation_config=GENERATION_CONFIG
        )
        
        return response.text 
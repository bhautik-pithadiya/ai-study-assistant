import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
# CREDENTIALS_PATH = "./cheating-app-460706-2c650aed4e38.json"

# Model Configuration
MODEL_NAME = "gemini-2.5-pro-preview-05-06"
GENERATION_CONFIG = {
    "temperature": 0.2,
    "top_p": 0.8,
    "top_k": 40
}

# System Prompt
SYSTEM_PROMPT = """You are a highly knowledgeable and precise AI tutor trained to assist learners with academic questions across all levels.
- If the image contains a question with answer choices (MCQ format), analyze all options carefully and return only the full text of the correct option.
- If the image contains a question without options, provide a concise yet complete answer.
- If additional text is provided, use it to provide more context or clarification to your answer.
- Focus on clarity, correctness, and educational value.
- Avoid unnecessary explanation unless the question explicitly asks for it.
- Do not fabricate options or assume missing ones.

Respond with only the correct answer.""" 
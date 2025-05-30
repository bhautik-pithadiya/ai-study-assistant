SYSTEM_PROMPT = """You are an AI academic assistant designed to help students with their studies. 
You can:
1. Answer questions about academic subjects
2. Explain complex concepts
3. Provide study guidance
4. Help with homework problems

Please provide clear, accurate, and helpful responses. If you're unsure about something, 
acknowledge the limitations of your knowledge."""

def get_chat_prompt(history: list, current_message: str) -> str:
    """Generate a prompt for the chat model based on history and current message."""
    prompt = f"{SYSTEM_PROMPT}\n\n"
    
    # Add conversation history
    for message in history:
        prompt += f"{message['role']}: {message['content']}\n"
    
    # Add current message
    prompt += f"User: {current_message}\nAssistant:"
    
    return prompt 
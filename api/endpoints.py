from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from models.schemas import AnswerResponse
from services.gemini_service import GeminiService

router = APIRouter()
gemini_service = GeminiService()

@router.post("/answer/", 
    response_model=AnswerResponse,
    summary="Answer questions from images with optional text context",
    description="Processes an image containing a question and optional text context to provide an answer using Gemini's multimodal capabilities"
)
async def answer_question(
    file: UploadFile = File(..., description="Image file containing the question"),
    text: str = Form("", description="Optional text context to provide additional information")
):
    """
    Process an image containing a question and optional text context to provide an answer.
    
    Args:
        file (UploadFile): The image file containing the question
        text (str): Optional text context to provide additional information
        
    Returns:
        AnswerResponse: Contains the answer to the question
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Read the image file
        contents = await file.read()
        
        # Generate answer using Gemini service
        answer = await gemini_service.generate_answer(
            image_content=contents,
            image_mime_type=file.content_type,
            text=text
        )
        
        return AnswerResponse(answer=answer)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        ) 
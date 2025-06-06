from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import logging
from typing import AsyncGenerator

from app.services.transcribe_service import TranscribeService

router = APIRouter()
transcribe_service = TranscribeService()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.websocket("/stream")
async def stream_transcribe(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    request_async_queue = asyncio.Queue()

    async def feed_request_queue(websocket: WebSocket, async_queue: asyncio.Queue):
        try:
            while True:
                chunk = await websocket.receive_bytes()
                if chunk:
                    await async_queue.put(chunk)
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
            await async_queue.put(None)
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
            await async_queue.put(None)

    async def async_request_generator(async_queue: asyncio.Queue) -> AsyncGenerator:
        while True:
            chunk = await async_queue.get()
            if chunk is None:
                break
            yield chunk

    feed_task = asyncio.create_task(feed_request_queue(websocket, request_async_queue))
    asr_task = asyncio.create_task(
        _asr_loop(async_request_generator(request_async_queue), websocket)
    )

    await asyncio.gather(feed_task, asr_task)

async def _asr_loop(generator: AsyncGenerator, websocket: WebSocket):
    try:
        async for chunk in generator:
            if isinstance(chunk, str):
                audio_bytes = bytes(chunk, 'latin1')
            else:
                audio_bytes = chunk
            transcript, confidence = transcribe_service.transcribe(audio_bytes)
            payload = {
                "transcript": transcript,
                "confidence": confidence,
                "is_final": True
            }
            await websocket.send_json(payload)
    except Exception as e:
        logger.error(f"_asr_loop error: {e}")

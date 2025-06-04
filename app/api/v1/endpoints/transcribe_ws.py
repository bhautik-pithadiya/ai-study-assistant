from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import queue
import logging
from typing import Generator

from app.services.transcribe_service import TranscribeService  # Import your service

router = APIRouter()
transcribe_service = TranscribeService()  # Instantiate the service
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@router.websocket("/stream")
async def stream_transcribe(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    request_sync_queue = queue.Queue()

    # PCM chunk feed task
    async def feed_request_queue(websocket: WebSocket, sync_queue: queue.Queue):
        try:
            while True:
                chunk = await websocket.receive_bytes()
                if chunk:
                    sync_queue.put(chunk)
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
            sync_queue.put(None)
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
            sync_queue.put(None)

    # Sync generator for audio chunks
    def sync_request_generator(sync_queue: queue.Queue) -> Generator:
        while True:
            chunk = sync_queue.get()
            if chunk is None:
                break
            yield chunk

    # Start feed task and ASR task
    feed_task = asyncio.create_task(feed_request_queue(websocket, request_sync_queue))
    asr_task = asyncio.create_task(
        _asr_loop(sync_request_generator(request_sync_queue), websocket)
    )

    await asyncio.gather(feed_task, asr_task)

async def _asr_loop(generator: Generator, websocket: WebSocket):
    try:
        for chunk in generator:
            # If chunk is a string (Latin-1 encoded), convert to bytes
            if isinstance(chunk, str):
                audio_bytes = bytes(chunk, 'latin1')
            else:
                audio_bytes = chunk
            transcript, confidence = transcribe_service.transcribe(audio_bytes)
            payload = {
                "transcript": transcript,
                "confidence": confidence,
                "is_final": True  # Since the service is not streaming, always final
            }
            await websocket.send_json(payload)
    except Exception as e:
        logger.error(f"_asr_loop error: {e}")

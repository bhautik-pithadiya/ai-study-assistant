from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from google.cloud import speech_v1p1beta1 as speech
import asyncio
import subprocess
import shlex
from typing import AsyncGenerator, Generator
import queue # Import the standard synchronous queue
import logging # Import logging

router = APIRouter()
client = speech.SpeechClient()

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set logging level to INFO

# ---------- helpers ---------------------------------------------------------
# We no longer need a per-chunk webm_to_pcm function with the continuous piping approach
# async def webm_to_pcm(webm_chunk: bytes) -> bytes:
#     ...
# ---------------------------------------------------------------------------

@router.websocket("/stream")
async def stream_transcribe(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")

    # Start the FFmpeg subprocess for continuous transcoding
    cmd = (
        "ffmpeg -loglevel warning -i pipe:0 " # Use pipe:0 for input
        "-ac 1 -ar 48000 -f s16le pipe:1" # Use pipe:1 for output
    )
    ffmpeg_process = None
    try:
        ffmpeg_process = await asyncio.create_subprocess_exec(
            *shlex.split(cmd),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE # Capture stderr for potential error messages
        )
        logger.info("FFmpeg subprocess started.")

        # This queue is for receiving transcoded PCM chunks from FFmpeg stdout
        pcm_queue = asyncio.Queue()

        # Task to read transcoded PCM data from FFmpeg stdout and put into pcm_queue
        async def read_ffmpeg_stdout(stdout, async_queue: asyncio.Queue):
            logger.info("read_ffmpeg_stdout task started")
            chunk_size = 4096 # Read from FFmpeg stdout in chunks
            while True:
                # Read a chunk of transcoded PCM data from FFmpeg stdout
                pcm_chunk = await stdout.read(chunk_size)
                if not pcm_chunk:
                    logger.info("read_ffmpeg_stdout: FFmpeg stdout stream ended.")
                    break
                # Put processed PCM into the async queue
                # logger.debug(f"read_ffmpeg_stdout: Putting {len(pcm_chunk)} bytes into pcm_queue") # Use debug for verbose logging
                await async_queue.put(pcm_chunk)
            logger.info("read_ffmpeg_stdout task finished")

        # Start the task to read from FFmpeg stdout
        read_ffmpeg_task = asyncio.create_task(read_ffmpeg_stdout(ffmpeg_process.stdout, pcm_queue))
        
        # Task to read FFmpeg stderr (useful for debugging)
        async def read_ffmpeg_stderr(stderr):
            logger.info("read_ffmpeg_stderr task started")
            while True:
                line = await stderr.readline()
                if not line:
                    logger.info("read_ffmpeg_stderr: FFmpeg stderr stream ended.")
                    break
                logger.warning(f"FFmpeg stderr: {line.decode().strip()}")
            logger.info("read_ffmpeg_stderr task finished")

        read_stderr_task = asyncio.create_task(read_ffmpeg_stderr(ffmpeg_process.stderr))

        # speech-to-text streaming config
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=48000,
            language_code="en-US",
            model="latest_short"
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )

        # A synchronous queue to buffer requests for the Google client
        # This queue is thread-safe and used by the synchronous generator
        request_sync_queue = queue.Queue() 

        # Task to feed the synchronous request_sync_queue from the asynchronous pcm_queue
        async def feed_request_sync_queue(async_queue: asyncio.Queue, sync_queue: queue.Queue):
            logger.info("feed_request_sync_queue task started")
            while True:
                logger.info("feed_request_sync_queue: Waiting for item from pcm_queue")
                pcm_chunk = await async_queue.get()
                logger.info("feed_request_sync_queue: Got item from pcm_queue")
                if pcm_chunk is None: # Signal from read_ffmpeg_stdout that the stream is ending
                    sync_queue.put(None) # Signal end of stream to the sync generator
                    logger.info("feed_request_sync_queue: Put None into request_sync_queue, breaking")
                    break
                request = speech.StreamingRecognizeRequest(audio_content=pcm_chunk)
                logger.info("feed_request_sync_queue: Putting request into request_sync_queue")
                sync_queue.put(request)
                logger.info("feed_request_sync_queue: Put request into request_sync_queue")
            logger.info("feed_request_sync_queue task finished")

        # Start the feed task immediately
        feed_task = asyncio.create_task(feed_request_sync_queue(pcm_queue, request_sync_queue))

        # Synchronous generator to yield requests from the synchronous queue for the Google client
        def sync_request_generator(sync_queue: queue.Queue) -> Generator:
            logger.info("sync_request_generator started")
            while True:
                logger.info("sync_request_generator: Waiting for item from request_sync_queue")
                # This is a blocking get from a synchronous queue
                request = sync_queue.get()
                logger.info("sync_request_generator: Got item from request_sync_queue")
                if request is None:
                    logger.info("sync_request_generator: Got None, breaking")
                    break
                logger.info("sync_request_generator: Yielding request")
                yield request
            logger.info("sync_request_generator finished")

        # Delay the creation of the ASR task until the first audio data is processed
        asr_task = None # Initialize as None

        try:
            # Task to receive WebM chunks from the WebSocket and write to FFmpeg stdin
            async def write_to_ffmpeg_stdin(websocket: WebSocket, stdin):
                logger.info("write_to_ffmpeg_stdin task started")
                try:
                    while True:
                        logger.info("WebSocket: Waiting to receive bytes")
                        # receive webm/opus chunk from client
                        message = await websocket.receive_bytes()
                        logger.info(f"WebSocket: Received {len(message)} bytes")
                        # Write the received WebM chunk to FFmpeg stdin
                        stdin.write(message)
                        await stdin.drain() # Ensure data is written to the pipe
                        # logger.debug("write_to_ffmpeg_stdin: Wrote chunk to FFmpeg stdin") # Use debug for verbose logging
                except WebSocketDisconnect:
                    logger.info("write_to_ffmpeg_stdin: WebSocket disconnected.")
                except Exception as e:
                    logger.error(f"write_to_ffmpeg_stdin error: {e}")
                finally:
                    # Close FFmpeg stdin when WebSocket connection is closed or error occurs
                    if stdin: # Check if stdin is not None (it should be if process started)
                         stdin.close()
                         logger.info("write_to_ffmpeg_stdin: FFmpeg stdin closed.")
                    logger.info("write_to_ffmpeg_stdin task finished")
            
            # Start the task to write to FFmpeg stdin
            write_task = asyncio.create_task(write_to_ffmpeg_stdin(websocket, ffmpeg_process.stdin))

            # Wait for the write_task to complete (WebSocket disconnected or error)
            await write_task

        except Exception as e:
             logger.error(f"stream_transcribe main loop error: {e}")

    except Exception as e:
        logger.error(f"Error starting FFmpeg subprocess: {e}")
    finally:
        logger.info("WebSocket closing, starting cleanup.")
        
        # Signal the end of the PCM stream by putting None into pcm_queue.
        # This will signal feed_request_sync_queue to stop, which in turn
        # puts None into request_sync_queue, signaling sync_request_generator to stop.
        # This needs to happen regardless of how the try block exited.
        logger.info("WebSocket closing, putting None into pcm_queue")
        await pcm_queue.put(None)

        # Ensure FFmpeg process is terminated if it's still running
        if ffmpeg_process and ffmpeg_process.returncode is None:
            logger.info("Terminating FFmpeg process.")
            try:
                ffmpeg_process.terminate()
                await asyncio.wait_for(ffmpeg_process.wait(), timeout=5.0) # Wait for process to exit
                logger.info(f"FFmpeg process terminated with return code {ffmpeg_process.returncode}.")
            except asyncio.TimeoutError:
                logger.warning("FFmpeg process did not terminate gracefully, killing it.")
                ffmpeg_process.kill()
                await ffmpeg_process.wait()
                logger.info(f"FFmpeg process killed with return code {ffmpeg_process.returncode}.")
            except Exception as e:
                logger.error(f"Error terminating FFmpeg process: {e}")

        # Gather and wait for all background tasks to complete. Return exceptions.
        tasks_to_await = [feed_task, read_ffmpeg_task, read_stderr_task]
        if asr_task is not None:
             tasks_to_await.append(asr_task)

        logger.info(f"WebSocket closing, waiting for tasks: {[task.get_name() for task in tasks_to_await]}")
        results = await asyncio.gather(*tasks_to_await, return_exceptions=True)
        
        # Log any exceptions from the tasks
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task finished with exception: {result}")

        # Close the WebSocket connection
        # This is done at the very end after all cleanup
        try:
            await websocket.close()
            logger.info("WebSocket closed successfully.")
        except Exception as e:
            logger.error(f"Error closing WebSocket: {e}")


async def _asr_loop(generator: Generator, streaming_config, websocket: WebSocket):
    """
    Runs in its own task, consumes audio from a synchronous generator
    and pushes transcripts back to client.
    """
    logger.info("_asr_loop started")
    # Pass the websocket explicitly to allow sending close frames if needed in the future
    # For now, just use it for sending results

    try:
        # The Google client expects a synchronous iterable
        logger.info("_asr_loop: Calling client.streaming_recognize")
        responses = client.streaming_recognize(streaming_config, generator)
        logger.info("_asr_loop: Returned from client.streaming_recognize, starting iteration")

        # Iterate over the responses synchronously (as the client returns a synchronous iterator)
        for response in responses:
            # Check if the WebSocket is still connected before sending
            # This might prevent errors if the client disconnects while processing Google responses
            # if not websocket.client_state == 3: # State 3 is closed
            logger.info("_asr_loop: Got response from client")
            for result in response.results:
                alt = result.alternatives[0]
                payload = {
                    "transcript": alt.transcript,
                    "confidence": alt.confidence,
                    "is_final": result.is_final
                }
                # Send results back to the client asynchronously
                await websocket.send_json(payload)
                # logger.info(f"_asr_loop: Sent: {payload['transcript'][:50]}...") # Optional: for debugging
    except Exception as e:
        logger.error(f"_asr_loop error: {e}")
        # The exception is caught and logged, asyncio.gather in stream_transcribe handles waiting
    finally:
        logger.info("_asr_loop finished")
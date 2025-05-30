from google.cloud import speech

class TranscribeService:
    def __init__(self):
        self.client = speech.SpeechClient()

    def transcribe(self, audio_content: bytes) -> str:
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            # sample_rate_hertz=16000,
            language_code="en-US",
            model="latest_short",  # Chosen model
        )
        response = self.client.recognize(config=config, audio=audio)
        alternative = response.results[0].alternatives[0]
        return alternative.transcript,alternative.confidence
    
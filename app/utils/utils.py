import subprocess
import tempfile

def m4a_to_wav_bytes(m4a_bytes):
    # Write m4a to temp file
    with open("temp.m4a", "wb") as f:
        f.write(m4a_bytes)
    # Convert to wav using ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-i", "temp.m4a",
        "-ar", "16000", "-ac", "1", "-f", "wav", "temp.wav"
    ])
    # Read wav bytes
    with open("temp.wav", "rb") as f:
        wav_bytes = f.read()
    return wav_bytes



def m4a_to_wav_mono_bytes(m4a_bytes):
    with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as m4a_file:
        m4a_file.write(m4a_bytes)
        m4a_file.flush()
        m4a_path = m4a_file.name

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
        wav_path = wav_file.name

    # ffmpeg conversion
    subprocess.run([
        "ffmpeg", "-y", "-i", m4a_path,
        "-ar", "16000", "-ac", "1", "-f", "wav", wav_path
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Read the converted mono wav
    with open(wav_path, "rb") as f:
        wav_bytes = f.read()

    return wav_bytes

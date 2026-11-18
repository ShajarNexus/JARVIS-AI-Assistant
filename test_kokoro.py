
from kokoro_onnx import Kokoro
import soundfile as sf

MODEL_PATH = "models/tts/kokoro-v1.0.onnx"
VOICES_PATH = "models/tts/voices-v1.0.bin"

print("Loading Kokoro voice engine...")

kokoro = Kokoro(MODEL_PATH, VOICES_PATH)

text = (
    "Hello! I am Jarvis. "
    "It is a pleasure to meet you. "
    "How can I help you today?"
)

print("Generating speech...")

audio, sample_rate = kokoro.create(
    text,
    voice="af_river",
    speed=0.95,
    lang="en-us"
)

sf.write(
    "kokoro_test.wav",
    audio,
    sample_rate,
    subtype="PCM_16"
)

print("Success! Speech saved as kokoro_test.wav")

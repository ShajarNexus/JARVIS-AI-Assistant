
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from pathlib import Path


# Store the speech recognition model on D drive
BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models" / "speech"

SAMPLE_RATE = 16000
RECORD_SECONDS = 7


def main():

    print("\nLoading JARVIS speech recognition...")
    print("The first run will download the English model.")

    model = WhisperModel(
        "small.en",
        device="cpu",
        compute_type="int8",
        download_root=str(MODEL_DIR)
    )

    print("\nJARVIS speech recognition is ready!")

    input("\nPress ENTER and start speaking...")

    print("\nListening for 7 seconds...")

    recording = sd.rec(
        int(RECORD_SECONDS * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )

    sd.wait()

    audio_file = BASE_DIR / "test_recording.wav"

    sf.write(
        str(audio_file),
        recording,
        SAMPLE_RATE
    )

    print("\nUnderstanding your speech...")

    segments, info = model.transcribe(
        str(audio_file),
        language="en",
        beam_size=3,
        vad_filter=True
    )

    recognized_text = " ".join(
        segment.text.strip()
        for segment in segments
    )

    print("\n" + "=" * 45)
    print("JARVIS HEARD:")
    print(recognized_text if recognized_text else "No speech detected.")
    print("=" * 45)


if __name__ == "__main__":
    main()


import time

from app.speech_engine import jarvis_speech


print("\n================================")
print("       JARVIS VOICE TEST")
print("================================")
print("Speak in English.")
print("JARVIS will detect your speech.")
print("Press CTRL + C to stop.\n")

try:

    jarvis_speech.start()

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    print("\nStopping voice test...")

    jarvis_speech.stop()

    time.sleep(1)

    print("Test finished.")

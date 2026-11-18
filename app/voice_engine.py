
import threading
import queue

import sounddevice as sd
from kokoro_onnx import Kokoro


class JarvisVoice:

    def __init__(self):

        self.speech_queue = queue.Queue()

        # Kokoro model paths
        self.model_path = "models/tts/kokoro-v1.0.onnx"
        self.voices_path = "models/tts/voices-v1.0.bin"

        # Voice settings
        self.voice_name = "af_river"
        self.speed = 0.95

        # Background speech worker
        self.worker = threading.Thread(
            target=self._speech_worker,
            daemon=True
        )

        self.worker.start()

    def _speech_worker(self):

        kokoro = None

        try:

            print("Loading Kokoro voice engine...")

            kokoro = Kokoro(
                self.model_path,
                self.voices_path
            )

            print("Kokoro voice engine ready!")

            while True:

                text = self.speech_queue.get()

                try:

                    if text is None:
                        break

                    print("Generating JARVIS speech...")

                    audio, sample_rate = kokoro.create(
                        text,
                        voice=self.voice_name,
                        speed=self.speed,
                        lang="en-us"
                    )

                    sd.play(audio, sample_rate)
                    sd.wait()

                    print("Speech completed.")

                except Exception as error:

                    print("Voice playback error:", error)

                finally:

                    self.speech_queue.task_done()

        except Exception as error:

            print("Kokoro voice engine error:", error)

        finally:

            try:
                sd.stop()
            except Exception:
                pass

    def speak(self, text):

        if not text:
            return

        self.speech_queue.put(str(text))


# Global JARVIS voice instance
jarvis_voice = JarvisVoice()

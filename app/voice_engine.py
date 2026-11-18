
import threading
import queue

import sounddevice as sd
from kokoro_onnx import Kokoro


class JarvisVoice:

    def __init__(self):

        self.speech_queue = queue.Queue()

        self.model_path = "models/tts/kokoro-v1.0.onnx"
        self.voices_path = "models/tts/voices-v1.0.bin"

        self.voice_name = "af_river"
        self.speed = 0.95

        self.on_speech_finished = None

        self.is_speaking = False
        self.stop_requested = threading.Event()

        self.worker = threading.Thread(
            target=self._speech_worker,
            daemon=True
        )

        self.worker.start()

    # -----------------------------------------
    # 1. Speech worker
    # -----------------------------------------

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

                    if self.stop_requested.is_set():
                        continue

                    self.is_speaking = True

                    print("Generating JARVIS speech...")

                    audio, sample_rate = kokoro.create(
                        text,
                        voice=self.voice_name,
                        speed=self.speed,
                        lang="en-us"
                    )

                    if self.stop_requested.is_set():
                        continue

                    sd.play(audio, sample_rate)
                    sd.wait()

                    print("Speech completed.")

                except Exception as error:

                    print("Voice playback error:", error)

                finally:

                    self.is_speaking = False
                    self.speech_queue.task_done()

                    if self.on_speech_finished:

                        try:
                            self.on_speech_finished()

                        except Exception as error:
                            print("Speech callback error:", error)

        except Exception as error:

            print("Kokoro voice engine error:", error)

        finally:

            self.is_speaking = False

            try:
                sd.stop()
            except Exception:
                pass

    # -----------------------------------------
    # 2. Speak text
    # -----------------------------------------

    def speak(self, text):

        if not text:
            return

        self.stop_requested.clear()

        self.speech_queue.put(str(text))

    # -----------------------------------------
    # 3. Stop current speech and clear queue
    # -----------------------------------------

    def stop_speaking(self):

        print("Stopping JARVIS speech...")

        self.stop_requested.set()

        # Stop current audio playback immediately.
        try:
            sd.stop()
        except Exception as error:
            print("Audio stop error:", error)

        # Remove all pending speech.
        while True:

            try:
                self.speech_queue.get_nowait()
                self.speech_queue.task_done()

            except queue.Empty:
                break

        self.is_speaking = False

        print("JARVIS speech stopped.")

    # -----------------------------------------
    # 4. Stop voice engine when closing app
    # -----------------------------------------

    def shutdown(self):

        self.stop_speaking()

        self.speech_queue.put(None)


jarvis_voice = JarvisVoice()


import queue
import threading
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class JarvisSpeech:

    def __init__(self):

        self.model = None
        self.is_listening = False
        self.is_confirming = False

        # Normal speech callback
        self.on_text = None

        self.sample_rate = 16000
        self.block_duration = 0.1
        self.block_size = int(
            self.sample_rate * self.block_duration
        )

        self.silence_duration = 0.8
        self.min_speech_duration = 0.5
        self.max_speech_duration = 12.0

        self.energy_threshold = 0.012

        self.audio_queue = queue.Queue(maxsize=100)
        self.stop_event = threading.Event()

        self.worker = None
        self.confirmation_worker = None

    def _status(self, message):
        print("[JARVIS MIC]", message)

    def _audio_callback(
        self,
        indata,
        frames,
        time_info,
        status
    ):

        if status:
            print("Microphone status:", status)

        audio_chunk = indata[:, 0].copy()

        try:
            self.audio_queue.put_nowait(audio_chunk)

        except queue.Full:

            try:
                self.audio_queue.get_nowait()
                self.audio_queue.put_nowait(audio_chunk)

            except queue.Empty:
                pass

    def start(self):

        if self.is_listening or self.is_confirming:
            print("JARVIS microphone is already running.")
            return

        self.stop_event.clear()
        self.is_listening = True

        self.worker = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )

        self.worker.start()

    def stop(self, wait=True):

        if not self.is_listening:
            return

        self.stop_event.set()

        print("[JARVIS MIC] Stopping microphone...")

        if (
            wait
            and self.worker
            and self.worker.is_alive()
            and threading.current_thread() != self.worker
        ):
            self.worker.join(timeout=3)

    def _load_model(self):

        if self.model is None:

            self._status("Loading Faster-Whisper model...")

            self.model = WhisperModel(
                "small.en",
                device="cpu",
                compute_type="int8",
                download_root="models/speech"
            )

            self._status("Speech recognition ready.")

    def _transcribe(self, audio, notify=True):

        if len(audio) == 0:
            return None

        try:

            segments, info = self.model.transcribe(
                audio,
                language="en",
                beam_size=1,
                vad_filter=True,
                initial_prompt=(
                    "Jarvis is the name of an AI personal assistant. "
                    "The speaker is giving a short voice command."
                )
            )

            recognized_text = " ".join(
                segment.text.strip()
                for segment in segments
            ).strip()

            if recognized_text:

                print("\nYOU:", recognized_text)

                if notify and self.on_text:
                    self.on_text(recognized_text)

                return recognized_text

        except Exception as error:
            print("Speech recognition error:", error)

        return None

    def start_confirmation(self, on_result, timeout=8):

        """
        Listen for one short confirmation response.

        on_result receives:
            Recognized text, or None if no speech was detected.
        """

        if self.is_confirming:
            print("[JARVIS MIC] Confirmation is already active.")
            return

        # Stop continuous listening before opening another stream.
        if self.is_listening:
            self.stop(wait=True)

        if self.is_listening:
            print("[JARVIS MIC] Could not stop normal microphone.")
            on_result(None)
            return

        self.is_confirming = True

        self.confirmation_worker = threading.Thread(
            target=self._confirmation_loop,
            args=(on_result, timeout),
            daemon=True
        )

        self.confirmation_worker.start()

    def _confirmation_loop(self, on_result, timeout):

        confirmation_queue = queue.Queue(maxsize=100)

        def confirmation_audio_callback(
            indata,
            frames,
            time_info,
            status
        ):

            if status:
                print("Confirmation microphone status:", status)

            chunk = indata[:, 0].copy()

            try:
                confirmation_queue.put_nowait(chunk)

            except queue.Full:
                pass

        audio_buffer = []
        speech_started = False
        silence_blocks = 0

        silence_limit = int(
            self.silence_duration / self.block_duration
        )

        minimum_blocks = int(
            self.min_speech_duration / self.block_duration
        )

        maximum_blocks = int(
            6.0 / self.block_duration
        )

        recognized_text = None

        try:

            self._load_model()

            self._status(
                "Listening for confirmation. Say yes or no."
            )

            start_time = time.monotonic()

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.block_size,
                callback=confirmation_audio_callback
            ):

                while True:

                    elapsed = time.monotonic() - start_time

                    if elapsed >= timeout:
                        break

                    try:
                        chunk = confirmation_queue.get(
                            timeout=0.2
                        )

                    except queue.Empty:
                        continue

                    volume = np.sqrt(
                        np.mean(np.square(chunk))
                    )

                    if volume >= self.energy_threshold:

                        speech_started = True
                        silence_blocks = 0
                        audio_buffer.append(chunk)

                    elif speech_started:

                        audio_buffer.append(chunk)
                        silence_blocks += 1

                    finished_speaking = (
                        speech_started
                        and silence_blocks >= silence_limit
                    )

                    too_long = (
                        len(audio_buffer) >= maximum_blocks
                    )

                    if finished_speaking or too_long:

                        if len(audio_buffer) >= minimum_blocks:

                            self._status(
                                "Processing confirmation..."
                            )

                            audio = np.concatenate(
                                audio_buffer
                            ).astype(np.float32)

                            recognized_text = self._transcribe(
                                audio,
                                notify=False
                            )

                        break

            if recognized_text:
                self._status(
                    f"Confirmation heard: {recognized_text}"
                )
            else:
                self._status(
                    "No clear confirmation received."
                )

        except Exception as error:

            print(
                "[JARVIS MIC] Confirmation error:",
                error
            )

        finally:

            self.is_confirming = False

            try:
                on_result(recognized_text)
            except Exception as error:
                print(
                    "[JARVIS MIC] Confirmation callback error:",
                    error
                )

    def _listen_loop(self):

        try:

            self._load_model()

            if self.stop_event.is_set():
                return

            self.audio_queue = queue.Queue(maxsize=100)

            self._status(
                "Microphone active. Speak naturally."
            )

            audio_buffer = []
            speech_started = False
            silence_blocks = 0

            silence_limit = int(
                self.silence_duration / self.block_duration
            )

            minimum_blocks = int(
                self.min_speech_duration / self.block_duration
            )

            maximum_blocks = int(
                self.max_speech_duration / self.block_duration
            )

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.block_size,
                callback=self._audio_callback
            ):

                while not self.stop_event.is_set():

                    try:
                        chunk = self.audio_queue.get(
                            timeout=0.2
                        )

                    except queue.Empty:
                        continue

                    volume = np.sqrt(
                        np.mean(np.square(chunk))
                    )

                    if volume >= self.energy_threshold:

                        speech_started = True
                        silence_blocks = 0
                        audio_buffer.append(chunk)

                    elif speech_started:

                        audio_buffer.append(chunk)
                        silence_blocks += 1

                    should_transcribe = (
                        speech_started
                        and silence_blocks >= silence_limit
                    )

                    too_long = (
                        len(audio_buffer) >= maximum_blocks
                    )

                    if should_transcribe or too_long:

                        if len(audio_buffer) >= minimum_blocks:

                            self._status("Processing speech...")

                            audio = np.concatenate(
                                audio_buffer
                            ).astype(np.float32)

                            self._transcribe(audio)

                        audio_buffer = []
                        speech_started = False
                        silence_blocks = 0

                        if not self.stop_event.is_set():
                            self._status("Listening...")

        except Exception as error:

            print("Microphone error:", error)

        finally:

            self.is_listening = False
            self._status("Microphone stopped.")


jarvis_speech = JarvisSpeech()

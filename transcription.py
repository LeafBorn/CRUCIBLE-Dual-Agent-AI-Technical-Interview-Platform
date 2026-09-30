"""
Real-Time Transcription Module
==============================
Provides real-time speech-to-text transcription using faster-whisper and sounddevice.
Streams live transcripts as the candidate speaks and aggregates full answers.
"""

import sys
import time
import threading
import queue
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class RealtimeTranscriber:
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        """
        Initialize the Whisper model for real-time transcription.
        """
        print(f"⏳ Loading Whisper model ('{model_size}')...", end="", flush=True)
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            print(" ✅ Whisper ready!")
        except Exception as e:
            print(f"\n⚠️ Failed to load model '{model_size}' with {compute_type}: {e}")
            print("⏳ Falling back to default compute_type ('default')...")
            self.model = WhisperModel(model_size, device="cpu", compute_type="default")
            print(" ✅ Whisper ready (fallback)!")

        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 2.0  # seconds per processing slice
        self.silence_threshold = 0.008  # RMS threshold for voice activity

    def _is_silent(self, audio_np: np.ndarray) -> bool:
        """Check if audio block is below silence threshold."""
        if len(audio_np) == 0:
            return True
        rms = float(np.sqrt(np.mean(audio_np ** 2)))
        return bool(rms < self.silence_threshold)

    def record_answer(
        self,
        prompt: str = "\n🎙️  Speak your answer (Press ENTER when finished):\n",
        max_duration: int = 180,
        enable_silence_timeout: bool = False,
        silence_timeout_sec: float = 4.0
    ) -> str:
        """
        Record candidate speech with real-time live transcription.
        Returns the final consolidated transcribed answer string.
        """
        print(prompt)

        audio_queue = queue.Queue()
        stop_event = threading.Event()
        user_finished_event = threading.Event()

        collected_audio_blocks = []
        live_transcripts = []
        speech_detected = threading.Event()
        last_speech_time = [time.time()]

        chunk_samples = int(self.sample_rate * self.chunk_duration)

        # Worker for real-time incremental transcription
        def worker():
            buffer = np.array([], dtype=np.float32)
            while not stop_event.is_set():
                try:
                    block = audio_queue.get(timeout=0.2)
                except queue.Empty:
                    continue

                buffer = np.concatenate((buffer, block)) if len(buffer) > 0 else block

                if len(buffer) >= chunk_samples:
                    process_chunk = buffer[:chunk_samples]
                    buffer = buffer[chunk_samples:]

                    if not self._is_silent(process_chunk):
                        speech_detected.set()
                        last_speech_time[0] = time.time()
                        try:
                            segments, _ = self.model.transcribe(
                                process_chunk,
                                language="en",
                                beam_size=3,
                                vad_filter=True,
                                condition_on_previous_text=False
                            )
                            chunk_text = " ".join([seg.text.strip() for seg in segments if seg.text.strip()])
                            if chunk_text:
                                live_transcripts.append(chunk_text)
                                print(f"\r📝 [Live]: {' '.join(live_transcripts[-3:])}", end="", flush=True)
                        except Exception:
                            pass

                audio_queue.task_done()

        # sounddevice audio stream callback
        def audio_callback(indata, frames, time_info, status):
            if status:
                pass
            mono = indata[:, 0].copy()
            collected_audio_blocks.append(mono)
            audio_queue.put(mono)

        # Background listener for Enter key to stop recording
        def wait_for_enter():
            try:
                sys.stdin.readline()
            except Exception:
                pass
            user_finished_event.set()

        worker_thread = threading.Thread(target=worker, daemon=True)
        worker_thread.start()

        enter_thread = threading.Thread(target=wait_for_enter, daemon=True)
        enter_thread.start()

        start_time = time.time()

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
                blocksize=1024,
                callback=audio_callback
            ):
                while not user_finished_event.is_set():
                    elapsed = time.time() - start_time
                    if elapsed >= max_duration:
                        print(f"\n⏱️ Max recording duration ({max_duration}s) reached.")
                        break

                    # Optional silence timeout after speech began
                    if enable_silence_timeout and speech_detected.is_set():
                        if time.time() - last_speech_time[0] > silence_timeout_sec:
                            print(f"\n🤫 Silence detected for {silence_timeout_sec}s.")
                            break

                    time.sleep(0.1)

        except sd.PortAudioError as e:
            print(f"\n⚠️ Microphone error: {e}")
            print("⌨️  Falling back to keyboard text input...")
            manual_ans = input("\nYour Answer: ").strip()
            return manual_ans if manual_ans else "No answer provided"
        except Exception as e:
            print(f"\n⚠️ Audio recording error: {e}")
            manual_ans = input("\nYour Answer: ").strip()
            return manual_ans if manual_ans else "No answer provided"
        finally:
            stop_event.set()
            worker_thread.join(timeout=1.0)

        print("\n\n⚙️  Finalizing transcript...", flush=True)

        # Final high-accuracy transcription pass over the full recorded audio
        if collected_audio_blocks:
            full_audio = np.concatenate(collected_audio_blocks)
            if not self._is_silent(full_audio):
                try:
                    segments, _ = self.model.transcribe(
                        full_audio,
                        language="en",
                        beam_size=5,
                        vad_filter=True,
                        condition_on_previous_text=False
                    )
                    final_text = " ".join([seg.text.strip() for seg in segments if seg.text.strip()])
                    if final_text:
                        print(f"✅ Final Transcript: {final_text}")
                        return final_text
                except Exception as e:
                    print(f"⚠️ Full pass error ({e}), using live segments...")

        if live_transcripts:
            final_text = " ".join(live_transcripts)
            print(f"✅ Final Transcript: {final_text}")
            return final_text

        print("⚠️ No speech detected.")
        fallback = input("Enter your answer manually or press Enter to skip: ").strip()
        return fallback if fallback else "No answer provided"


# Singleton instance helper
_transcriber_instance = None

def get_transcriber(model_size: str = "base") -> RealtimeTranscriber:
    """Get or initialize the shared RealtimeTranscriber instance."""
    global _transcriber_instance
    if _transcriber_instance is None:
        _transcriber_instance = RealtimeTranscriber(model_size=model_size)
    return _transcriber_instance

def record_and_transcribe(prompt: str = "\n🎙️  Speak your answer (Press ENTER when finished):\n") -> str:
    """Convenience function to record and transcribe an answer."""
    transcriber = get_transcriber()
    return transcriber.record_answer(prompt=prompt)


if __name__ == "__main__":
    print("=" * 60)
    print("  🎤 Real-Time Transcription Test")
    print("=" * 60)
    transcriber = get_transcriber("base")
    answer = transcriber.record_answer()
    print("\n" + "=" * 60)
    print(f"Resulting Answer:\n{answer}")
    print("=" * 60)

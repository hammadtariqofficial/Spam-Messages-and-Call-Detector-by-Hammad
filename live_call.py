from __future__ import annotations

import threading
import time
from typing import Callable

import numpy as np

try:
    import speech_recognition as sr
except Exception:
    sr = None
try:
    import soundcard as sc
except Exception:
    sc = None


class LiveCallEngine:
    """Consent-based live PC-audio transcription and spam-risk analysis.

    ``microphone`` captures an input microphone. ``system`` captures a Windows
    speaker loopback by resolving the corresponding loopback microphone. Audio
    is processed in memory only; this class does not save audio to disk.
    SpeechRecognition's Google recognizer may require internet access.
    """

    def __init__(self, detector, on_transcript: Callable[[str], None],
                 on_result: Callable[[dict], None], on_status: Callable[[str], None]):
        self.detector = detector
        self.on_transcript = on_transcript
        self.on_result = on_result
        self.on_status = on_status
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.last_saved = 0.0
        self.recognizer = sr.Recognizer() if sr is not None else None

    @staticmethod
    def microphones():
        if sc is None:
            return []
        try:
            return [m.name for m in sc.all_microphones(include_loopback=False)]
        except Exception:
            return []

    @staticmethod
    def speakers():
        if sc is None:
            return []
        try:
            return [s.name for s in sc.all_speakers()]
        except Exception:
            return []

    def start(self, mode="microphone", device_name=None, chunk_seconds=4):
        if self.thread and self.thread.is_alive():
            return False
        if sc is None or sr is None or self.recognizer is None:
            self.on_status("Live Call requires SpeechRecognition and SoundCard support on this PC.")
            return False
        if mode not in {"microphone", "system"}:
            self.on_status("Invalid audio mode selected.")
            return False
        if not device_name:
            self.on_status("No audio device selected.")
            return False
        self.stop_event.clear()
        self.last_saved = 0.0
        self.thread = threading.Thread(
            target=self._run, args=(mode, device_name, max(1, int(chunk_seconds))), daemon=True
        )
        self.thread.start()
        return True

    def stop(self):
        self.stop_event.set()
        thread = self.thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=2.5)
        self.thread = None if not (thread and thread.is_alive()) else thread
        self.on_status("Stopped — no audio is being captured.")

    def _resolve_source(self, mode, device_name):
        if mode == "microphone":
            devices = sc.all_microphones(include_loopback=False)
            return next((d for d in devices if d.name == device_name), None)
        # SoundCard exposes loopback devices as microphones. Resolve the selected
        # speaker by name first, then find its loopback microphone by matching the
        # speaker name. This avoids attempting to record directly from a Speaker.
        speakers = sc.all_speakers()
        speaker = next((d for d in speakers if d.name == device_name), None)
        if speaker is None:
            return None
        loopbacks = sc.all_microphones(include_loopback=True)
        candidates = [m for m in loopbacks if getattr(m, 'isloopback', False) and m.name == speaker.name]
        if candidates:
            return candidates[0]
        candidates = [m for m in loopbacks if m.name == speaker.name or speaker.name in m.name or m.name in speaker.name]
        return candidates[0] if candidates else None

    def _run(self, mode, device_name, chunk_seconds):
        try:
            source = self._resolve_source(mode, device_name)
            if source is None:
                self.on_status("Selected audio device is unavailable or does not expose loopback capture.")
                return
            self.on_status("Listening to microphone…" if mode == "microphone" else "Listening to PC system audio (loopback)…")
            with source.recorder(samplerate=16000, channels=1) as rec:
                while not self.stop_event.is_set():
                    frames = rec.record(numframes=16000 * chunk_seconds)
                    if frames is None or len(frames) == 0:
                        continue
                    audio = np.asarray(frames).reshape(-1)
                    audio = np.clip(audio, -1, 1)
                    pcm = (audio * 32767).astype(np.int16).tobytes()
                    if len(pcm) < 16000:
                        continue
                    try:
                        data = sr.AudioData(pcm, 16000, 2)
                        text = self.recognizer.recognize_google(data).strip()
                    except sr.UnknownValueError:
                        self.on_status("Listening… (speech not recognized in this chunk)")
                        continue
                    except sr.RequestError as exc:
                        self.on_status(f"Speech-to-text service unavailable: {exc}")
                        if self.stop_event.wait(2):
                            break
                        continue
                    if not text or self.stop_event.is_set():
                        continue
                    self.on_transcript(text)
                    result = self.detector.analyze(text)
                    self.on_result(result)
                    now = time.time()
                    if result["risk_score"] >= 30 and now - self.last_saved >= 10:
                        try:
                            from detector import save_scan
                            save_scan(result)
                            self.last_saved = now
                        except Exception as exc:
                            self.on_status(f"Live result captured, but audit save failed: {exc}")
                    self.on_status(f"Live analysis: {result['classification']} • {result['risk_score']:.0f}% risk")
        except Exception as exc:
            self.on_status(f"Live call error: {exc}")

    def __del__(self):
        try:
            self.stop_event.set()
        except Exception:
            pass

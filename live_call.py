from __future__ import annotations
import threading, queue, time
from typing import Callable

import numpy as np

# Audio/STT are optional at runtime. The main detector must still start on a
# machine with a missing audio driver, no microphone, or a temporary STT issue.
try:
    import speech_recognition as sr
except Exception:
    sr = None
try:
    import soundcard as sc
except Exception:
    sc = None

class LiveCallEngine:
    """Consent-based live audio transcription + spam analysis bridge.

    MIC mode captures the selected microphone. SYSTEM mode captures the selected
    Windows speaker/loopback device when supported by the host. The engine never
    records or transmits audio to disk; short chunks are sent to the configured
    speech-to-text provider for transcription.
    """
    def __init__(self, detector, on_transcript: Callable[[str],None], on_result: Callable[[dict],None], on_status: Callable[[str],None]):
        self.detector=detector
        self.on_transcript=on_transcript
        self.on_result=on_result
        self.on_status=on_status
        self.stop_event=threading.Event()
        self.thread=None
        self.recognizer=sr.Recognizer()
        self.recognizer.dynamic_energy_threshold=True
        self.last_saved=0.0

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
        if sc is None or sr is None:
            self.on_status("Live Call requires the bundled audio/STT components.")
            return False
        self.stop_event.clear()
        self.thread=threading.Thread(target=self._run,args=(mode,device_name,chunk_seconds),daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self.on_status("Stopped — no audio is being captured.")

    def _run(self, mode, device_name, chunk_seconds):
        try:
            if mode == "system":
                devices=sc.all_speakers()
                device=next((x for x in devices if x.name==device_name), sc.default_speaker())
                source=device
                self.on_status("Listening to PC call audio (loopback)…")
            else:
                devices=sc.all_microphones(include_loopback=False)
                device=next((x for x in devices if x.name==device_name), sc.default_microphone())
                source=device
                self.on_status("Listening to microphone…")
            # 16 kHz mono PCM is a practical STT format.
            with source.recorder(samplerate=16000, channels=1) as rec:
                while not self.stop_event.is_set():
                    frames=rec.record(numframes=int(16000*chunk_seconds))
                    if frames is None or len(frames)==0:
                        continue
                    audio=np.asarray(frames).reshape(-1)
                    audio=np.clip(audio,-1,1)
                    pcm=(audio*32767).astype(np.int16).tobytes()
                    if len(pcm)<16000:
                        continue
                    try:
                        data=sr.AudioData(pcm,16000,2)
                        text=self.recognizer.recognize_google(data).strip()
                    except sr.UnknownValueError:
                        self.on_status("Listening… (speech not recognized in this chunk)")
                        continue
                    except sr.RequestError as e:
                        self.on_status(f"Speech-to-text service unavailable: {e}")
                        time.sleep(2)
                        continue
                    if not text:
                        continue
                    self.on_transcript(text)
                    result=self.detector.analyze(text)
                    self.on_result(result)
                    # Avoid flooding audit history during a long call.
                    now=time.time()
                    if result["risk_score"]>=30 and now-self.last_saved>=10:
                        try:
                            from detector import save_scan
                            save_scan(result); self.last_saved=now
                        except Exception:
                            pass
                    self.on_status(f"Live analysis: {result['classification']} • {result['risk_score']:.0f}% risk")
        except Exception as e:
            self.on_status(f"Live call error: {e}")

    def __del__(self):
        try: self.stop_event.set()
        except Exception: pass

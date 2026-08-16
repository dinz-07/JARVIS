import asyncio
import math
import os
import threading
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

MODEL_CHAT = "openai/gpt-oss-120b"
MODEL_STT = "whisper-large-v3-turbo"
MODEL_TTS = "canopylabs/orpheus-v1-english"
TTS_VOICE = "troy"
SAMPLE_RATE = 44100
RECORD_SECONDS = 5.0
BARGE_RATE = 16000
BARGE_BLOCK = 1600
BARGE_RMS = 0.02
BARGE_SUSTAIN = 5


class GroqEngine:
    def __init__(self):
        self.client = None
        self.history = []
        self.barge = False
        self._init_client()

    def _init_client(self):
        try:
            from groq import AsyncGroq

            key = os.environ.get("GROQ_API_KEY", "").strip()
            if key:
                self.client = AsyncGroq(api_key=key)
        except Exception:
            self.client = None

    @property
    def available(self):
        return self.client is not None

    async def stt(self, seconds=RECORD_SECONDS):
        frames = sd.rec(int(SAMPLE_RATE * seconds), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
        await asyncio.to_thread(sd.wait)
        tmp = ROOT / "voice_input.wav"
        with wave.open(str(tmp), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SAMPLE_RATE)
            f.writeframes(frames.tobytes())
        with open(tmp, "rb") as f:
            speech = await self.client.audio.transcriptions.create(
                file=f, model=MODEL_STT, prompt="Jarvis"
            )
        return (speech.text or "").strip()

    async def stt_bytes(self, wav_bytes):
        import io

        speech = await self.client.audio.transcriptions.create(
            file=("utterance.wav", io.BytesIO(wav_bytes)),
            model=MODEL_STT,
            prompt="Jarvis",
        )
        return (speech.text or "").strip()

    async def tts(self, text):
        speech = await self.client.audio.speech.create(
            input=text, model=MODEL_TTS, voice=TTS_VOICE, response_format="wav"
        )
        tmp = ROOT / "voice_output.wav"
        await speech.write_to_file(str(tmp))
        self.barge = False
        stop = threading.Event()
        player = threading.Thread(target=self._play, args=(tmp,), daemon=True)
        detector = threading.Thread(target=self._barge_detector, args=(stop,), daemon=True)
        player.start()
        detector.start()
        while player.is_alive():
            if stop.is_set():
                sd.stop()
                self.barge = True
                break
            await asyncio.sleep(0.05)

    def _play(self, path):
        try:
            with wave.open(str(path), "rb") as f:
                data = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16)
                sd.play(data, f.getframerate())
                sd.wait()
        except Exception:
            sd.stop()

    def _barge_detector(self, stop):
        try:
            from sounddevice import InputStream

            blocks = 0
            with InputStream(samplerate=BARGE_RATE, channels=1, dtype="float32", blocksize=BARGE_BLOCK) as stream:
                while not stop.is_set():
                    data, _ = stream.read(BARGE_BLOCK)
                    rms = math.sqrt(float(np.mean(np.square(data))))
                    if rms > BARGE_RMS:
                        blocks += 1
                    else:
                        blocks = 0
                    if blocks >= BARGE_SUSTAIN:
                        stop.set()
        except Exception:
            pass

    async def chat(self, text, system):
        if not self.history or self.history[0].get("role") != "system":
            self.history = [{"role": "system", "content": system}]
        self.history.append({"role": "user", "content": text})
        if len(self.history) > 12:
            self.history = [self.history[0]] + self.history[-10:]
        stream = await self.client.chat.completions.create(
            model=MODEL_CHAT, messages=self.history, stream=True, reasoning_effort="high"
        )
        result = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                result += delta
        self.history.append({"role": "assistant", "content": result})
        return result.strip()

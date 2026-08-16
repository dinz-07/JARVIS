import random

from app.state import LISTENING, SPEAKING, THINKING, IDLE

QUERIES = [
    "What is my system status?",
    "Run a threat scan.",
    "What's on my calendar today?",
    "Play some music.",
    "Open the weather module.",
    "Who are you?",
]


class VoiceManager:
    def __init__(self, app):
        self.app = app

    async def cycle(self):
        if self.app.state.voice_active:
            return
        self.app.state.voice_active = True
        state = self.app.state
        groq = self.app.groq
        try:
            while True:
                state.log("VOICE INPUT RECEIVED")
                state.set_state(LISTENING)
                self.app.voice_wave(True)
                query = ""
                if groq.available:
                    try:
                        query = await groq.stt()
                    except Exception as exc:
                        state.log("STT ERROR :: " + str(exc)[:80])
                else:
                    query = random.choice(QUERIES)
                self.app.voice_wave(False)
                if not query:
                    state.log("NO VOICE DETECTED")
                    break
                state.log("ANALYZING REQUEST")
                state.log("NEURAL PROCESSING :: " + query.upper()[:48])
                state.set_state(THINKING)
                response = await self.app.engine.process(query, voice=True)
                state.set_state(SPEAKING)
                state.log("RESPONSE GENERATED")
                self.app.hologram.show("— " + query, response)
                self.app.voice_wave(True)
                barged = False
                if groq.available:
                    try:
                        await groq.tts(response)
                        barged = groq.barge
                    except Exception as exc:
                        state.log("TTS ERROR :: " + str(exc)[:80])
                self.app.voice_wave(False)
                if barged:
                    state.log("BARGE-IN :: INTERRUPTED — LISTENING AGAIN")
                    continue
                state.log("TASK COMPLETE")
                break
        finally:
            state.set_state(IDLE)
            self.app.state.voice_active = False

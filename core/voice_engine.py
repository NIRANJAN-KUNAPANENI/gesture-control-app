import threading
import time
import logging

class VoiceEngine:
    """Background voice command listener for hybrid voice + gesture control."""

    def __init__(self, action_mapper=None, camera_thread=None):
        self.action_mapper = action_mapper
        self.camera_thread = camera_thread
        self.enabled = False
        self._running = False
        self._thread = None
        self.last_command = ""

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _listen_loop(self):
        """Try speech recognition if available, otherwise stay standby."""
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
        except Exception:
            # speech_recognition package not installed; fallback gracefully
            while self._running:
                time.sleep(1.0)
            return

        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1.0)

        while self._running:
            if not self.enabled:
                time.sleep(0.5)
                continue

            try:
                with microphone as source:
                    audio = recognizer.listen(source, timeout=3.0, phrase_time_limit=3.0)
                text = recognizer.recognize_google(audio).lower().strip()
                self.last_command = text
                self._process_command(text)
            except Exception:
                pass

    def _process_command(self, text: str):
        if "lock" in text and self.camera_thread:
            self.camera_thread.control_unlocked = False
        elif "unlock" in text and self.camera_thread:
            self.camera_thread.control_unlocked = True
        elif "mute" in text and self.action_mapper:
            self.action_mapper.execute("FIST")
        elif "play" in text or "pause" in text:
            if self.action_mapper:
                self.action_mapper.execute("OPEN_PALM")
        elif "next" in text:
            if self.action_mapper:
                self.action_mapper.execute("SWIPE_RIGHT")
        elif "previous" in text or "back" in text:
            if self.action_mapper:
                self.action_mapper.execute("SWIPE_LEFT")

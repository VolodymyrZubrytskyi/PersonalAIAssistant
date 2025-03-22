import alsaaudio
import pyaudio
import numpy as np
from vosk import Model, KaldiRecognizer
import json
from collections import deque

# Configuration
DEVICE_INDEX = 1  # Check your device index
RATE = 16000
CHUNK = 512  # smaller chunk for faster response
FORMAT = pyaudio.paInt16
THRESHOLD = 75  # Lower to capture fast speech
SILENCE_TIMEOUT = 1.0  # Slightly increased for accuracy
MODEL_PATH = "models/vosk-model-uk-v3"

# Initialize Vosk Model
model = Model(MODEL_PATH)

# PyAudio initialization
audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, input_device_index=DEVICE_INDEX,
                    frames_per_buffer=CHUNK)

print("Listening continuously. Press Ctrl+C to stop.")

def detect_voice(audio_chunk):
    audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
    volume = np.abs(audio_data).max()
    return volume > THRESHOLD

BUFFER_SECONDS = 1.5
pre_audio_buffer = deque(maxlen=int(BUFFER_SECONDS * RATE / CHUNK))

try:
    while True:
        frames = []
        silent_chunks = 0
        speaking = False

        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            pre_audio_buffer.append(data)

            if detect_voice(data):
                if not speaking:
                    print("🎙️ Voice detected! Recording...")
                    speaking = True
                    frames.extend(pre_audio_buffer)
                frames.append(data)
                silent_chunks = 0
            elif speaking:
                silent_chunks += 1
                frames.append(data)
                if silent_chunks >= int(SILENCE_TIMEOUT * RATE / CHUNK):
                    print("⏸️ Silence detected. Processing...")
                    break

        recognizer = KaldiRecognizer(model, RATE)
        recognizer.SetWords(True)

        audio_bytes = b''.join(frames)
        if recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(recognizer.Result())
        else:
            result = json.loads(recognizer.FinalResult())

        text = result.get('text', '').strip()
        if text:
            print(f"✅ Recognized: {text}")
        else:
            print("⚠️ Could not recognize speech clearly.")

except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
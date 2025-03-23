import numpy as np
from piper import PiperVoice
import sounddevice as sd

SPEAKER = 1
VOICE_MODEL_PATH = "voices/uk_UA-ukrainian_tts-medium.onnx"
VOICE_CONFIG_PATH = "voices/uk_UA-ukrainian_tts-medium.onnx.json"

voice = PiperVoice.load(VOICE_MODEL_PATH, config_path = VOICE_CONFIG_PATH)

def speak_text(text: str):
    stream = sd.OutputStream(samplerate=22050, channels=1, dtype='int16')
    stream.start()

    for audio_bytes in voice.synthesize_stream_raw(text, speaker_id = SPEAKER):
        int_data = np.frombuffer(audio_bytes, dtype=np.int16)
        stream.write(int_data)

    stream.stop()
    stream.close()

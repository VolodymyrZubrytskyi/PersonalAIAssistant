import subprocess
import os
import queue
import threading

SPEAKER = 2
VOICE_MODEL_PATH = "voices/uk_UA-ukrainian_tts-medium.onnx"
PIPER_PATH = os.path.join(os.path.dirname(__file__), "piper/piper")

speech_queue = queue.Queue()
speaking = threading.Event()

def speak_worker():
    while True:
        text = speech_queue.get()
        if text is None:
            break
        speak_text(text)
        speaking.clear()
        speech_queue.task_done()

def start_speaking():
    threading.Thread(target=speak_worker, daemon=True).start()

def enqueue_speech(text: str):
    speaking.set()
    speech_queue.put(text)

def speak_text(text: str):
    if not text.strip():
        print("Warning: Empty text received, skipping TTS.")
        return

    try:
        piper_process = subprocess.Popen(
            [PIPER_PATH, "--model", VOICE_MODEL_PATH, "--speaker", str(SPEAKER), "--output_file", "-"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        aplay_process = subprocess.Popen(["aplay"], stdin=piper_process.stdout, stderr=subprocess.PIPE)

        piper_process.stdin.write(text.encode('utf-8'))
        piper_process.stdin.close()

        piper_process.wait()
        aplay_process.wait()

        if piper_process.returncode != 0:
            stderr = piper_process.stderr.read().decode()
            raise Exception(f"Piper error: {stderr}")

        if aplay_process.returncode != 0:
            stderr = aplay_process.stderr.read().decode()
            raise Exception(f"aplay error: {stderr}")

    except Exception as e:
        print(f"Error while speaking text: {str(e)}")

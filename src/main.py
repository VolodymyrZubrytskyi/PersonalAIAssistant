import subprocess
import os
import queue
import threading
from speech_to_text import listen_and_recognize
from ai_chat import generate_ai_response_stream
from text_to_speech import enqueue_speech

# Configuration for Piper TTS
SPEAKER = 2
VOICE_MODEL_PATH = "voices/uk_UA-ukrainian_tts-medium.onnx"
PIPER_PATH = os.path.join(os.path.dirname(__file__), "piper/piper")

# Speech queue and threading
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
        # Start the Piper process
        piper_process = subprocess.Popen(
            [
                PIPER_PATH,
                "--model", VOICE_MODEL_PATH,
                "--speaker", str(SPEAKER),
                "--output_file", "-"
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Start the aplay process to play the output
        aplay_process = subprocess.Popen(
            ["aplay"],
            stdin=piper_process.stdout,
            stderr=subprocess.PIPE
        )

        # Encode the text to bytes and send it to Piper's stdin
        piper_process.stdin.write(text.encode('utf-8'))
        piper_process.stdin.close()

        # Wait for Piper and aplay to complete
        piper_process.wait()
        aplay_process.wait()

        # Check Piper process for errors
        if piper_process.returncode != 0:
            stderr = piper_process.stderr.read().decode()
            raise Exception(f"Piper error: {stderr}")

        # Check aplay process for errors
        if aplay_process.returncode != 0:
            stderr = aplay_process.stderr.read().decode()
            raise Exception(f"aplay error: {stderr}")

    except Exception as e:
        print(f"Error while speaking text: {str(e)}")

    finally:
        # Ensure both processes are properly terminated
        if piper_process.poll() is None:
            piper_process.terminate()
        if aplay_process.poll() is None:
            aplay_process.terminate()

def main():
    print("🎙️ Listening for your input...")
    user_text = listen_and_recognize()

    if user_text:
        print(f"✅ You said: {user_text}")
    else:
        print("⚠️ No recognizable speech detected.")
        return

    print("🤖 Generating AI response...")
    ai_stream = generate_ai_response_stream(user_text)

    accumulated_text = ""
    for text_chunk in ai_stream:
        print(f"🗨️ AI: {text_chunk}", end='', flush=True)
        accumulated_text += text_chunk + " "

        # Accumulate a complete sentence or a longer chunk before speaking
        if len(accumulated_text) >= 150 or any(punct in accumulated_text for punct in [".", "!", "?"]):
            print("\n🔊 Speaking AI response...")
            enqueue_speech(accumulated_text.strip())
            accumulated_text = ""

    # Speak any remaining text
    if accumulated_text.strip():
        print("\n🔊 Speaking final AI response...")
        enqueue_speech(accumulated_text.strip())

if __name__ == "__main__":
    try:
        start_speaking()
        while True:
            main()
    except KeyboardInterrupt:
        print("\n🛑 Program stopped.")
from speech_to_text import listen_and_recognize
from ai_chat import generate_ai_response_stream
from text_to_speech import speak_text

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
            speak_text(accumulated_text)
            accumulated_text = ""

if __name__ == "__main__":
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print("\n🛑 Program stopped.")
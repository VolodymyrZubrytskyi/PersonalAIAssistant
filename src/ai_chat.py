import subprocess

def generate_ai_response_stream(prompt: str):
    try:
        # Start the AI process
        process = subprocess.Popen(
            ["ollama", "run", "gemma3:4b"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Send the prompt to the AI model
        process.stdin.write(prompt + "\n")
        process.stdin.close()

        buffer = ""
        while True:
            # Read one character at a time for real-time streaming
            chunk = process.stdout.read(1)
            if not chunk:
                break
            buffer += chunk

            # Yield full sentences or large chunks to reduce interruptions
            if "." in buffer or "\n" in buffer:
                sentence = buffer.strip()
                buffer = ""
                yield sentence

        # Check for errors in the AI process
        stderr = process.stderr.read()
        if process.wait() != 0:
            raise Exception(f"AI generation failed: {stderr.strip()}")

    except Exception as e:
        print(f"Error during AI generation: {str(e)}")
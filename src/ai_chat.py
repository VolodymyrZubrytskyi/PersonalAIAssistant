import ollama

PROMPT = """
"""

def generate_ai_response_stream(user_prompt: str):
    try:
        response = ollama.chat(
            model='gemma3:4b',
            messages=[
                {'role': 'system', 'content': PROMPT},
                {'role': 'user', 'content': user_prompt}
            ],
            stream=True
        )

        sentence = ""
        for chunk in response:
            text = chunk['message']['content']
            sentence += text

            # Accumulate complete sentences or larger chunks
            if len(sentence) >= 150 or any(punct in sentence for punct in [".", "!", "?"]):
                yield sentence.strip()
                sentence = ""

        if sentence:
            yield sentence.strip()

    except Exception as e:
        print(f"Error during AI generation: {str(e)}")
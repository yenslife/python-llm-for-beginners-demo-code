import os
from base64 import b64encode, b64decode

from openai import OpenAI
from dotenv import load_dotenv
from rich import print

load_dotenv()  # Load environment variables from a .env file if present

client = OpenAI()
audio_path = "example.mp3"

# use gpt-4o-mini-audio-preview-2024-12-17 to test audio input and output
response = client.chat.completions.create(
    model="gpt-4o-mini-audio-preview-2024-12-17",
    modalities=["text", "audio"],
    messages=[
        {"role": "user", "content": [
            {
                "type": "text",
                "text": "用中文告訴我這段東西在講什麼"
            },
            {
                "type": "input_audio",
                "input_audio": {
                    "data": f"{b64encode(open(audio_path, 'rb').read()).decode()}",
                    "format": "mp3"
                }
            }
        ]}
    ],
    audio={
        "format": "mp3",
        "voice": "sage"
    }
)

audio_data = response.choices[0].message.audio.data
transcript = response.choices[0].message.audio.transcript

# decode the base64 audio data and save it to a file
with open("response.mp3", "wb") as f:
    f.write(b64decode(audio_data))

print(f"Transcript:{transcript}")

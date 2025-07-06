import os
import openai
import base64
import tempfile
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI

app = Flask(__name__, static_folder="static")
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        data = request.json
        audio_base64 = data["audio"]

        # Decode audio
        audio_data = base64.b64decode(audio_base64.split(",")[1])
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio.flush()
            audio_path = temp_audio.name

        # Whisper transcription
        with open(audio_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            question = transcript.text

        # GPT-4 response
        gpt = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant answering interview questions."},
                {"role": "user", "content": question}
            ]
        )

        return jsonify({"question": question, "answer": gpt.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

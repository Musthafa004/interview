import openai
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    data = request.json
    audio_base64 = data["audio"]
    
    audio_data = base64.b64decode(audio_base64.split(",")[1])
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        temp_audio.write(audio_data)
        temp_audio.flush()
        temp_audio_path = temp_audio.name

    audio_file = open(temp_audio_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    question = transcript["text"]

    gpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're an expert technical interviewer. Answer simply and clearly."},
            {"role": "user", "content": question}
        ]
    )

    answer = gpt_response["choices"][0]["message"]["content"]
    return jsonify({"question": question, "answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)

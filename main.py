import openai
import base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import tempfile

# 🔧 Create the Flask app and set static folder
app = Flask(__name__, static_folder="static")
CORS(app)

# 🔐 Set your OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ Route to serve the frontend (index.html)
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# 🎙️ Route to receive audio, transcribe, and return GPT answer
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    try:
        data = request.json
        audio_base64 = data["audio"]
        
        # Decode the audio data
        audio_data = base64.b64decode(audio_base64.split(",")[1])
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(audio_data)
            temp_audio.flush()
            temp_audio_path = temp_audio.name

        # Transcribe using Whisper
        with open(temp_audio_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            question = transcript["text"]

        # Use GPT to generate answer
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant answering interview questions clearly."},
                {"role": "user", "content": question}
            ]
        )

        answer = gpt_response["choices"][0]["message"]["content"]

        return jsonify({"question": question, "answer": answer})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 Start the Flask app on port 3000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
    

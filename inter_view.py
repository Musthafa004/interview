# interview_assistant.py

import streamlit as st
import openai
import numpy as np
import tempfile
import os
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings
import av
import queue

# Set OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]  # Use Streamlit secrets for safety

# UI Header
st.set_page_config(page_title="Interview Assistant", layout="centered")
st.title("🎤 Ahamed's Interview Assistant")
st.markdown("""
This app listens to the interviewer's voice (not yours), transcribes the question, and gives you a perfect answer to read.
Just speak normally — it will wait for the interviewer to ask and respond with a sentence-by-sentence guide. 🔁
""")

# Queue to collect audio
audio_q = queue.Queue()

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recording = []
        self.threshold = 1500  # Adjust for speaker separation

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        volume = np.abs(audio).mean()

        if volume > self.threshold:
            audio_q.put(audio.tobytes())

        return frame

# Start recording from mic
webrtc_streamer(key="mic",
                mode="SENDONLY",
                client_settings=ClientSettings(
                    media_stream_constraints={"audio": True, "video": False},
                    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                ),
                audio_processor_factory=AudioProcessor)

# Process when button clicked
if st.button("🧠 Process Interviewer's Question"):
    if audio_q.empty():
        st.warning("No audio detected. Try speaking a little louder or closer to mic.")
    else:
        # Save to temporary WAV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            while not audio_q.empty():
                f.write(audio_q.get())
            audio_path = f.name

        st.success("🎧 Audio recorded. Transcribing...")

        # Transcribe with Whisper API
        with open(audio_path, "rb") as af:
            transcript = openai.Audio.transcribe("whisper-1", af)
            question = transcript["text"]

        st.markdown(f"#### 🗣️ Detected Question:")
        st.info(question)

        # Get ChatGPT answer
        with st.spinner("Generating answer..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You're an expert helping with interviews. Answer clearly and professionally."},
                    {"role": "user", "content": f"{question}"}
                ]
            )
            answer = response["choices"][0]["message"]["content"]

        # Split answer into sentences for user to read
        sentences = answer.split(". ")
        st.markdown("### 📖 Read This Slowly:")
        for i, s in enumerate(sentences):
            st.markdown(f"**{i+1}.** {s.strip().rstrip('.')}.")

        os.remove(audio_path)

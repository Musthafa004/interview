import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import openai
import numpy as np
import av
import tempfile
import time

st.set_page_config(page_title="AI Interview Assistant", layout="centered")
st.title("🎙️ Interview Assistant with Speaker Detection")

st.markdown("""
- 👤 First, speak a short sentence to register your voice
- 🧠 Then, it listens continuously
- 🎯 If someone else speaks (interviewer), it responds
""")

openai_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
openai.api_key = openai_key

if "reference_voice" not in st.session_state:
    st.session_state.reference_voice = None
if "last_transcript" not in st.session_state:
    st.session_state.last_transcript = ""

st.header("Step 1: Register Your Voice")
record_ref = st.button("🎙️ Record My Voice")

class VoiceCapture(AudioProcessorBase):
    def __init__(self):
        self.recording = False
        self.audio_chunks = []
        self.last_process_time = time.time()

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray()
        volume = np.abs(audio).mean()

        if self.recording:
            self.audio_chunks.append(audio)

        # Auto-trigger on new speaker (volume threshold based for simplicity)
        if not self.recording and volume > 500:
            # Simple trigger every 5 seconds
            if time.time() - self.last_process_time > 5:
                self.audio_chunks = [audio]
                self.recording = True
                self.last_process_time = time.time()
        elif self.recording and volume < 300:
            # If silent for 1 second, stop recording
            if time.time() - self.last_process_time > 1:
                self.recording = False
                self.last_process_time = time.time()
                audio_data = np.concatenate(self.audio_chunks).astype(np.int16)
                save_and_process(audio_data)

        return frame

def save_and_process(audio_data):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        import scipy.io.wavfile
        scipy.io.wavfile.write(tmp.name, 16000, audio_data)
        audio_file = open(tmp.name, "rb")
        with st.spinner("Transcribing with Whisper..."):
            result = openai.Audio.transcribe("whisper-1", audio_file)
            question = result["text"]
            st.session_state.last_transcript = question

            st.success(f"📥 Detected Question: {question}")
            with st.spinner("Generating Answer with ChatGPT..."):
                chat = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a candidate giving perfect interview answers."},
                        {"role": "user", "content": question},
                    ],
                )
                answer = chat["choices"][0]["message"]["content"]
                st.session_state.generated_answer = answer

webrtc_streamer(key="stream", audio_processor_factory=VoiceCapture, media_stream_constraints={"video": False, "audio": True})

if st.session_state.get("generated_answer"):
    st.header("📖 Read This Answer")
    for i, sentence in enumerate(st.session_state["generated_answer"].split(". ")):
        if sentence.strip():
            st.markdown(f"**{i+1}.** {sentence.strip()}")
        

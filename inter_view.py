import streamlit as st
from streamlit_webrtc import webrtc_streamer
import openai
import av
import tempfile

st.set_page_config(page_title="Voice Interview Assistant", layout="centered")
st.title("🎙️ Voice-Based Interview Assistant (Online)")

st.markdown("""
- 🎧 Speak the interview question aloud
- 🧠 Whisper API transcribes it
- 🤖 ChatGPT generates a response
- 📖 You read it sentence-by-sentence
""")

# API Key input
openai_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")
openai.api_key = openai_key

# Audio recorder state
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

# Function to transcribe using Whisper API
def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp.seek(0)
        audio_file = open(tmp.name, "rb")
        result = openai.Audio.transcribe("whisper-1", audio_file)
        return result["text"]

# WebRTC audio recorder
st.subheader("🎤 Record Interviewer’s Question")
from streamlit_webrtc import AudioProcessorBase

class AudioRecorder(AudioProcessorBase):
    def __init__(self):
        self.buffer = b""
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().tobytes()
        st.session_state.audio_data = audio
        return frame

webrtc_streamer(key="audio", audio_processor_factory=AudioRecorder, media_stream_constraints={"video": False, "audio": True})

# Transcription
if st.session_state.audio_data and st.button("🔍 Transcribe Question"):
    with st.spinner("Transcribing..."):
        try:
            question = transcribe_audio(st.session_state.audio_data)
            st.session_state.question = question
            st.success(f"Detected Question: **{question}**")
        except Exception as e:
            st.error(f"Error: {e}")

# Generate answer
if st.session_state.get("question") and st.button("💬 Generate Answer"):
    with st.spinner("Generating answer from ChatGPT..."):
        try:
            chat = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional candidate giving crisp interview answers."},
                    {"role": "user", "content": st.session_state.question}
                ]
            )
            answer = chat["choices"][0]["message"]["content"]
            st.session_state.answer = answer
        except Exception as e:
            st.error(f"ChatGPT Error: {e}")

# Sentence display
if st.session_state.get("answer"):
    st.subheader("📖 Answer (Read Aloud)")
    for idx, sentence in enumerate(st.session_state.answer.split(". "), 1):
        if sentence.strip():
            st.markdown(f"**{idx}.** {sentence.strip()}")
    

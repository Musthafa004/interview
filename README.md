import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import whisper
import openai
import av

st.set_page_config(page_title="Voice Interview Assistant", layout="centered")

st.title("🎙️ Voice-Based Interview Assistant")
st.markdown("""
- 🎧 Speak the interview question aloud
- 🤖 ChatGPT gives an answer
- 📖 You read each sentence one by one
""")

# User inputs their OpenAI API key
openai_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

if not openai_key:
    st.warning("Please enter your OpenAI API key to proceed.")
    st.stop()

openai.api_key = openai_key
model = whisper.load_model("base")

class AudioProcessor(AudioProcessorBase):
    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio = frame.to_ndarray().flatten().astype("float32") / 32768.0
        result = model.transcribe(audio, language="en")
        if result["text"].strip():
            st.session_state["question"] = result["text"]
        return frame

st.subheader("🎤 Speak your Interview Question")

webrtc_streamer(
    key="interview",
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
    async_processing=True,
)

if "question" in st.session_state and st.session_state["question"]:
    st.success(f"Detected Question: {st.session_state['question']}")

    if st.button("💬 Generate Answer"):
        with st.spinner("Generating response..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You're a confident interview candidate. Give clear and concise answers."},
                        {"role": "user", "content": st.session_state["question"]}
                    ]
                )
                answer = response["choices"][0]["message"]["content"]
                st.session_state["answer"] = answer
            except Exception as e:
                st.error(f"Error: {e}")
                st.stop()

if "answer" in st.session_state:
    st.subheader("🗣️ Answer (Read Aloud):")
    for i, sentence in enumerate(st.session_state["answer"].split('. '), 1):
        if sentence.strip():
            st.markdown(f"**{i}.** {sentence.strip()}")
            

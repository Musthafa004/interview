import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings
import openai, numpy as np, tempfile, os, queue

st.set_page_config(page_title="Interview Assistant", layout="centered")
st.title("🎤 Ahamed's Voice Interview AI")
st.markdown("""
The app listens automatically for the interviewer's voice (not yours), transcribes it with Whisper API, gets ChatGPT's answer, and shows it sentence‑by‑sentence for you to read aloud — all without manual input!
""")

openai.api_key = st.secrets["OPENAI_API_KEY"]

audio_q = queue.Queue()

class Proc(AudioProcessorBase):
    def recv(self, frame):
        audio = frame.to_ndarray().flatten()
        vol = np.abs(audio).mean()
        if vol > 800:
            audio_q.put(frame.to_ndarray().tobytes())
        return frame

webrtc_streamer(key="mic",
    mode="SENDONLY",
    audio_processor_factory=Proc,
    client_settings=ClientSettings(
        media_stream_constraints={"audio": True, "video": False},
        rtc_configuration={"iceServers":[{"urls": ["stun:stun.l.google.com:19302"]}]},
    ),
)

if st.button("🔄 Process Latest Question"):
    if audio_q.empty():
        st.warning("No audio detected. Please speak the interviewer's question louder.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            while not audio_q.empty():
                f.write(audio_q.get())
            path = f.name

        st.success("🎧 Audio captured, transcribing…")
        with open(path, "rb") as af:
            text = openai.Audio.transcribe("whisper-1", af)["text"]
        st.markdown(f"#### 🗣️ Detected question:\n> {text}")

        st.success("⏳ Getting ChatGPT answer…")
        ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":"You are an interview coach giving professional concise answers."},
                {"role":"user","content":text}
            ],
        )["choices"][0]["message"]["content"]

        st.markdown("### 📖 Read this answer:")
        for idx, sent in enumerate(ans.split(". "), start=1):
            st.markdown(f"**{idx}.** {sent.strip().rstrip('.')}.")
        os.remove(path)
        

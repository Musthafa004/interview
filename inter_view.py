import streamlit as st
import openai
import tempfile

st.set_page_config(page_title="🎤 Interview Assistant", layout="centered")
st.title("🎤 Voice-Based Interview Assistant (100% Online)")

st.markdown("""
1. 🎙️ Record interviewer's voice (question)
2. 🧠 Transcribe with Whisper API
3. 🤖 Get ChatGPT answer
4. 📖 Read it sentence-by-sentence
""")

# API key input
openai_key = st.text_input("🔑 Enter your OpenAI API key", type="password")
openai.api_key = openai_key

# Upload or record audio
st.subheader("🎧 Step 1: Record Interviewer's Voice")
audio_file = st.file_uploader("Upload or record a voice question (WAV/MP3)", type=["wav", "mp3", "m4a"])

if audio_file is not None:
    with st.spinner("📝 Transcribing..."):
        try:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            question = transcript["text"]
            st.success(f"✅ Detected Question: **{question}**")
            st.session_state["question"] = question
        except Exception as e:
            st.error(f"❌ Transcription error: {e}")

# ChatGPT response
if st.session_state.get("question") and st.button("💬 Generate Answer"):
    with st.spinner("🤖 Generating ChatGPT Answer..."):
        try:
            chat = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional interview candidate. Keep answers clear and confident."},
                    {"role": "user", "content": st.session_state["question"]}
                ]
            )
            answer = chat.choices[0].message.content
            st.session_state["answer"] = answer
        except Exception as e:
            st.error(f"❌ ChatGPT error: {e}")

# Sentence-wise reading
if st.session_state.get("answer"):
    st.subheader("📖 Answer (Read Aloud)")
    for i, sentence in enumerate(st.session_state["answer"].split(". "), 1):
        if sentence.strip():
            st.markdown(f"**{i}.** {sentence.strip()}")

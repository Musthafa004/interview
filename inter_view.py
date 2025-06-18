import streamlit as st
import openai
import tempfile

st.title("🎙️ Interview Assistant (Voice-Based)")
st.info("Ask your interviewer to speak. I will listen and reply using ChatGPT. You can read it out loud.")

openai.api_key = st.secrets["OPENAI_API_KEY"]

audio_file = st.file_uploader("Record or upload your question", type=["wav", "mp3", "m4a"])

if audio_file:
    st.audio(audio_file)

    with st.spinner("Transcribing..."):
        audio_bytes = audio_file.read()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        whisper_response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=open(tmp_path, "rb")
        )

        question = whisper_response.text
        st.success(f"🎤 Interviewer Asked: {question}")

        with st.spinner("Generating answer..."):
            chat_response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You're helping someone answer interview questions naturally."},
                    {"role": "user", "content": question}
                ]
            )
            answer = chat_response.choices[0].message.content
            st.markdown("### ✅ Suggested Answer:")
            st.write(answer)
            

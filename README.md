# interview

import streamlit as st
import openai

st.set_page_config(page_title="FinalRound AI Clone", layout="centered")

st.title("🧠 FinalRound Interview Assistant")
st.markdown("""
This app simulates an interview scenario:
- You enter the interviewer's **question**
- ChatGPT gives a **clear, sentence-by-sentence answer**
- You can **read and practice** each sentence aloud
""")

openai_api = st.text_input("🔑 Enter your OpenAI API Key", type="password")

if openai_api:
    openai.api_key = openai_api
    question = st.text_input("🎤 Interviewer Question", placeholder="e.g., Tell me about yourself")

    if st.button("Generate Answer") and question:
        with st.spinner("Thinking like a pro candidate..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a confident candidate giving short and clear interview answers."},
                        {"role": "user", "content": question}
                    ]
                )
                answer = response["choices"][0]["message"]["content"]
                st.success("✅ Answer Ready! Speak it sentence by sentence below:")

                for idx, sentence in enumerate(answer.split('. '), 1):
                    if sentence.strip():
                        st.markdown(f"**{idx}.** {sentence.strip()}")

            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown("---")
st.caption("Made with ❤️ by Assistant")

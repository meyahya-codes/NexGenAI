import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation

st.set_page_config(page_title="NexGenAI Pro", page_icon="🚀", layout="wide")
st.title("🚀 NexGenAI Pro")
st.caption("ChatGPT Style - Unlimited PDF / PPTX / TXT")

with st.sidebar:
    st.header("📁 Upload")
    uploaded_files = st.file_uploader("Upload files", type=["pdf","pptx","txt"], accept_multiple_files=True, label_visibility="collapsed")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()
    st.info("Model: NexGenAI Pro - GPT-OSS 20B")

# --- GROQ CLIENT ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Missing GROQ_API_KEY in Secrets")
    st.stop()

api_key = str(st.secrets["GROQ_API_KEY"]).strip().replace('"','').replace("'","")
client = Groq(api_key=api_key)

def extract_text(files):
    text_data = ""
    for f in files:
        try:
            if f.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(f)
                for p in reader.pages:
                    t = p.extract_text()
                    if t: text_data += t + "\n"
            elif f.name.endswith(".pptx"):
                prs = Presentation(f)
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text:
                            text_data += shape.text + "\n"
            elif f.name.endswith(".txt"):
                text_data += f.read().decode("utf-8", errors="ignore") + "\n"
        except:
            pass
    return text_data

if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if uploaded_files:
    st.session_state.doc_text = extract_text(uploaded_files)
    st.sidebar.success(f"Loaded {len(uploaded_files)} files")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything..."):
    if not st.session_state.doc_text:
        st.warning("First upload a PDF/PPT from sidebar")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                context = st.session_state.doc_text[:15000]
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": f"You are NexGenAI Pro, created by jr.developer MR. Yahya. You are NOT from OpenAI, NOT ChatGPT. You were built by Yahya for NexGenAI startup. Never say OpenAI. Use this document to answer: {context}"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1024
                )
                answer = completion.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")

if not uploaded_files:
    st.info("👆 Upload PDF/PPT in sidebar to start")
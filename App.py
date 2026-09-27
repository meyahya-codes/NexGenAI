import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation
import io

st.set_page_config(page_title="NexGenAI Pro", page_icon="🚀", layout="wide")
st.title("🚀 NexGenAI Pro - Chat with ANY Document")

# --- Sidebar ---
with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded_files = st.file_uploader("PDF, PPTX, TXT", type=["pdf","pptx","txt"], accept_multiple_files=True)
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.caption("⚡ Powered by Llama 3.3 70B (Groq)")

# --- Load Groq Client ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Please add GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

# --- Function to read files ---
def extract_text(files):
    all_text = ""
    for file in files:
        if file.name.endswith(".pdf"):
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                all_text += page.extract_text() + "\n"
        elif file.name.endswith(".pptx"):
            prs = Presentation(file)
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        all_text += shape.text + "\n"
        elif file.name.endswith(".txt"):
            all_text += file.read().decode("utf-8") + "\n"
    return all_text

# --- Session State for ChatGPT Style ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if uploaded_files:
    with st.spinner("Reading your unlimited slides..."):
        st.session_state.doc_text = extract_text(uploaded_files)
    st.sidebar.success(f"Loaded {len(uploaded_files)} files - {len(st.session_state.doc_text)} chars")

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input (like ChatGPT) ---
if prompt := st.chat_input("Ask anything about your documents..."):
    if not st.session_state.doc_text:
        st.warning("Please upload PDF/PPT first!")
    else:
        # User message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI Answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                system_prompt = f"You are NexGenAI. Answer based on this document context:\n\n{st.session_state.doc_text[:15000]}\n\nIf answer not in document, use your general knowledge but mention it."

                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    model="llama-3.3-70b-versatile",
                    temperature=0.7,
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

if not uploaded_files:
    st.info("👆 Upload PDF or PPT in sidebar to start chatting like ChatGPT!")
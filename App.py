import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation

st.set_page_config(page_title="NexGenAI Pro", page_icon="🚀", layout="wide")
st.title("🚀 NexGenAI Pro - Chat with ANY Document")
st.caption("⚡ Unlimited PDF / PPT / TXT + ChatGPT Style")

# --- Sidebar ---
with st.sidebar:
    st.header("📁 Upload Documents")
    uploaded_files = st.file_uploader("PDF, PPTX, TXT", type=["pdf","pptx","txt"], accept_multiple_files=True)
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    model="llama3-70b-8192",

# --- Load Groq Client ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

api_key = st.secrets["GROQ_API_KEY"].strip().replace('"','').replace("'","")
client = Groq(api_key=api_key)

# --- Function to read files ---
def extract_text(files):
    all_text = ""
    for file in files:
        try:
            if file.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        all_text += text + "\n"
            elif file.name.endswith(".pptx"):
                prs = Presentation(file)
                for slide in prs.slides:
                    for shape in slide.shapes:
                        if hasattr(shape, "text") and shape.text:
                            all_text += shape.text + "\n"
            elif file.name.endswith(".txt"):
                all_text += file.read().decode("utf-8", errors="ignore") + "\n"
        except Exception as e:
            st.sidebar.error(f"Error in {file.name}: {e}")
    return all_text

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if uploaded_files:
    with st.spinner("Reading your files..."):
        st.session_state.doc_text = extract_text(uploaded_files)
    st.sidebar.success(f"Loaded {len(uploaded_files)} files")

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input (like ChatGPT) ---
if prompt := st.chat_input("Ask anything about your documents..."):
    if not st.session_state.doc_text:
        st.warning("Please upload PDF/PPT first from sidebar!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("NexGenAI is thinking..."):
                try:
                    system_prompt = f"You are NexGenAI Pro. Answer from this document:\n\n{st.session_state.doc_text[:20000]}\n\nIf not in document, use your own knowledge."
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        model="llama-3.3-70b-versatile",
                        temperature=0.6,
                    )
                    response = chat_completion.choices[0].message.content
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Groq Error: {e}")

if not uploaded_files and not st.session_state.messages:
    st.info("👆 Upload PDF or PPT in sidebar to start chatting like ChatGPT - Unlimited slides supported!")
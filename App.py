import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation
from datetime import datetime

st.set_page_config(page_title="NexGenAI Pro", page_icon="🚀", layout="wide")

# --- CUSTOM CSS FOR PRO LOOK ---
st.markdown("""
<style>
.big-title {font-size:38px; font-weight:800; color:#00FFAB;}
.small {color:gray;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown('<div class="big-title">🚀 NexGenAI</div>', unsafe_allow_html=True)
    st.caption("AI Assistant Pro")
    st.divider()

    st.header("📁 Upload Document")
    uploaded_files = st.file_uploader("PDF, PPTX, TXT", type=["pdf","pptx","txt"], accept_multiple_files=True, label_visibility="collapsed")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

    st.divider()
    st.success(f"Model: GPT-OSS 20B (Groq)")
    if uploaded_files:
        st.info(f"✅ {len(uploaded_files)} file(s) loaded")

    st.divider()
    st.header("👨‍💻 About Developer")
    st.markdown("""
    **Mr. Yahya**
    Jr. Developer | AI Enthusiast
    Founder of **NexGenAI Pro**

    📧 Email: `meyahya.codes@gmail.com`
    💻 GitHub: `github.com/meyahya-codes`
    🌐 Project: `nexgenai-pro.streamlit.app`

    Passionate about building AI tools for everyone.
    """)
    st.divider()
    st.caption(f"© {datetime.now().year} NexGenAI Pro. All rights reserved.")

# --- GROQ CLIENT ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY in Streamlit Secrets")
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

# --- MAIN HEADER ---
col1, col2 = st.columns([1,5])
with col1:
    st.markdown("# 🚀")
with col2:
    st.title("NexGenAI Pro")
    st.caption("Your Personal AI - Chat with Docs or Just Chat like ChatGPT")

# --- SHOW HISTORY ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT - WORKS ALWAYS ---
if prompt := st.chat_input("Ask anything about your docs or general..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("NexGenAI is thinking..."):
            try:
                if st.session_state.doc_text:
                    context = st.session_state.doc_text[:15000]
                    system_prompt = f"""You are NexGenAI, a powerful AI assistant created by Jr. Developer Mr. Yahya.
                    - If asked 'who are you': Say 'I am NexGenAI, a next-generation AI assistant built by Jr. Developer Mr. Yahya.'
                    - If asked 'who built you': Say 'I was built by Jr. Developer Mr. Yahya, founder of NexGenAI Pro. I am NOT from OpenAI.'
                    - Never say you are from OpenAI, Google, or Meta. You are NexGenAI.
                    - Developer Email: meyahya.codes@gmail.com, GitHub: github.com/meyahya-codes
                    - Use this DOCUMENT to answer: {context}
                    """
                else:
                    system_prompt = """You are NexGenAI, a powerful AI assistant created by Jr. Developer Mr. Yahya.
                    - If asked 'who are you': Say 'I am NexGenAI, a next-generation AI assistant built by Jr. Developer Mr. Yahya.'
                    - If asked 'who built you': Say 'I was built by Jr. Developer Mr. Yahya, founder of NexGenAI Pro. Email: meyahya.codes@gmail.com, GitHub: meyahya-codes. I am NOT from OpenAI.'
                    - Never claim OpenAI. You are NexGenAI Pro.
                    - Answer helpfully like ChatGPT.
                    """

                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1200
                )
                answer = completion.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")

if not st.session_state.messages:
    st.info("👋 Hi! I'm NexGenAI built by Mr. Yahya. Upload a doc OR just ask anything!")
import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation

st.set_page_config(page_title="NexGenAI Pro", page_icon="🚀", layout="centered")

# --- HIDE STREAMLIT BRANDING - ONLY YOUR BRANDING ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ONLY FOR YOU ---
with st.sidebar:
    st.markdown("## 🚀 NexGenAI Pro")
    st.caption("by Mr. Yahya")
    st.divider()

    st.markdown("### 📁 Upload Doc")
    uploaded_files = st.file_uploader("", type=["pdf","pptx","txt"], accept_multiple_files=True, label_visibility="collapsed")

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

    st.divider()
    st.markdown("### 👨‍💻 Developer")
    st.markdown("""
    **Mr. Yahya**
    Jr. Developer & Founder

    📧 yahyakhan782522@gmail.com
    💻 github.com/meyahya-codes
    """)

# --- API KEY ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()
api_key = str(st.secrets["GROQ_API_KEY"]).strip().replace('"','').replace("'","")
client = Groq(api_key=api_key)

def extract_text(files):
    txt = ""
    for f in files:
        try:
            if f.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(f)
                for p in reader.pages:
                    t = p.extract_text()
                    if t: txt += t + "\n"
            elif f.name.endswith(".pptx"):
                prs = Presentation(f)
                for slide in prs.slides:
                    for sh in slide.shapes:
                        if hasattr(sh,"text") and sh.text: txt+=sh.text+"\n"
            else:
                txt+=f.read().decode("utf-8", errors="ignore")+"\n"
        except: pass
    return txt

if "messages" not in st.session_state: st.session_state.messages=[]
if "doc_text" not in st.session_state: st.session_state.doc_text=""

if uploaded_files:
    st.session_state.doc_text = extract_text(uploaded_files)

# --- MAIN ---
st.title("🚀 NexGenAI Pro")
st.caption("Ask anything - With or without document")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                doc = st.session_state.doc_text[:12000] if st.session_state.doc_text else ""
                if doc:
                    sys = f"You are NexGenAI, built by Jr. Developer Mr. Yahya (yahyakhan782522@gmail.com, github.com/meyahya-codes). You are NOT OpenAI. If asked who are you: I am NexGenAI. If asked who built you: Built by Jr. Developer Mr. Yahya. Answer using doc: {doc}"
                else:
                    sys = "You are NexGenAI, built by Jr. Developer Mr. Yahya, Email: yahyakhan782522@gmail.com, GitHub: meyahya-codes. If asked who are you: I am NexGenAI, a next-gen AI assistant. If asked who built you: Built by Jr. Developer Mr. Yahya. You are NOT from OpenAI. Answer helpfully."

                res = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":sys},{"role":"user","content":prompt}],
                    temperature=0.7, max_tokens=1200
                )
                ans = res.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","content":ans})
            except Exception as e:
                st.error(f"Error: {e}")

if not st.session_state.messages:
    st.info("👋 I'm NexGenAI Pro, built by Mr. Yahya. Upload file or just chat!")
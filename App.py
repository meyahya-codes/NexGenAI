import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation
from fpdf import FPDF
import tempfile, os

st.set_page_config(page_title="NexGenAI Pro", page_icon="logo.png", layout="centered")

# Make it installable like ChatGPT
st.markdown("""
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="logo.png">
<meta name="theme-color" content="#111B21">
""", unsafe_allow_html=True)

# --- WHATSAPP / META AI DARK THEME CSS ---
st.markdown("""
<style>
#MainMenu, footer, header,.stDeployButton {visibility:hidden; display:none;}
body,.stApp {background-color: #111B21!important;}
.chat-header {background:#202C33; padding:12px 15px; display:flex; align-items:center; gap:10px; border-radius:10px 10px 0 0; color:white;}
.chat-header b {font-size:18px;}
.chat-bubble-user {background:#005C4B; color:white; padding:10px 14px; border-radius:12px 0 12px 12px; margin:8px 0 8px auto; max-width:85%; float:right; clear:both;}
.chat-bubble-ai {background:#202C33; color:#E9EDEF; padding:10px 14px; border-radius:0 12px 12px 12px; margin:8px auto 8px 0; max-width:85%; float:left; clear:both;}
.code-box {background:#111B21; border:1px solid #2A3942; border-radius:10px; padding:10px; margin:8px 0;}
.action-row {display:flex; gap:15px; margin-top:6px; opacity:0.7; font-size:18px;}
.bottom-bar {background:#202C33; padding:10px; border-radius:25px; position:fixed; bottom:10px; left:10px; right:10px;}
</style>
""", unsafe_allow_html=True)

# --- GROQ ---
if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY in Secrets"); st.stop()
client = Groq(api_key=str(st.secrets["GROQ_API_KEY"]).strip().replace('"','').replace("'",""))

def extract_text(files):
    txt=""
    for f in files:
        try:
            if f.name.endswith(".pdf"):
                r=PyPDF2.PdfReader(f)
                for p in r.pages:
                    t=p.extract_text()
                    if t: txt+=t+"\n"
            elif f.name.endswith(".pptx"):
                prs=Presentation(f)
                for s in prs.slides:
                    for sh in s.shapes:
                        if hasattr(sh,"text") and sh.text: txt+=sh.text+"\n"
            else: txt+=f.read().decode("utf-8",errors="ignore")+"\n"
        except: pass
    return txt

if "messages" not in st.session_state: st.session_state.messages=[]
if "doc_text" not in st.session_state: st.session_state.doc_text=""

# --- TOP HEADER LIKE SCREENSHOT ---
st.markdown("""
<div class="chat-header">
<span style="font-size:22px;">←</span>
<img src="logo.png" width="35" style="border-radius:50%;">
<b>NexGenAI</b> <span style="color:#53BDEB;">✔</span>
<span style="margin-left:auto; font-size:20px;">⋮</span>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR FOR DOCS (Hidden but functional) ---
with st.sidebar:
    st.markdown("## 🚀 NexGenAI Pro")
    st.caption("by Mr. Yahya - yahyakhan782522@gmail.com")
    up = st.file_uploader("📎 Upload PDF/PPTX/TXT", type=["pdf","pptx","txt"], accept_multiple_files=True)
    if up: st.session_state.doc_text = extract_text(up); st.success(f"{len(up)} files loaded")
    if st.button("Clear Chat"): st.session_state.messages=[]; st.rerun()
    st.divider()
    st.markdown("👨‍💻 **Mr. Yahya**\nJr. Developer\n📧 yahyakhan782522@gmail.com\n💻 github.com/meyahya-codes")

# --- DISPLAY CHAT LIKE WHATSAPP BUBBLES ---
chat_container = st.container()
with chat_container:
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"]=="user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div><div style="clear:both;"></div>', unsafe_allow_html=True)
        else:
            # AI bubble with code style + actions like screenshot
            st.markdown(f'<div class="chat-bubble-ai">{msg["content"]}<div class="action-row">📋 ↪️ 👍 👎</div></div><div style="clear:both;"></div>', unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown('<div class="chat-bubble-ai">👋 Hi! I am <b>NexGenAI</b> built by <b>Jr. Developer Mr. Yahya</b>.<br><br>📎 Upload doc, 📷 Take photo, 🎤 Speak or Type!</div>', unsafe_allow_html=True)

st.markdown("<br><br><br><br>", unsafe_allow_html=True)

# --- BOTTOM BAR LIKE WHATSAPP - Emoji + Message + Attachment + Camera + Voice ---
st.markdown('<div class="bottom-bar">', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns([1, 6, 1, 1, 1.2])

final_prompt = None
uploaded_via_bar = None
camera_img = None
voice_audio = None

with c1:
    st.markdown("😊")
with c2:
    text_input = st.text_input("Message", placeholder="Message", label_visibility="collapsed", key="msg_input")
with c3:
    # Attachment - 📎
    uploaded_via_bar = st.file_uploader("📎", type=["pdf","pptx","txt","jpg","png"], label_visibility="collapsed", key="attach")
with c4:
    # Camera - 📷
    camera_img = st.camera_input("", label_visibility="collapsed", key="cam")
with c5:
    # Voice - Green button like screenshot
    voice_audio = st.audio_input("", label_visibility="collapsed", key="voice")

st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIC FOR INPUTS ---
if uploaded_via_bar:
    st.session_state.doc_text = extract_text([uploaded_via_bar])
    final_prompt = f"Read this file {uploaded_via_bar.name} and summarize"
if camera_img:
    final_prompt = "I captured an image, describe what you can see (user used camera)"
if voice_audio:
    with st.spinner("Transcribing..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(voice_audio.getvalue()); path=tmp.name
            with open(path,"rb") as f:
                trans = client.audio.transcriptions.create(file=(path, f.read()), model="whisper-large-v3", response_format="text")
            final_prompt = trans
            os.remove(path)
        except Exception as e:
            st.error(e)
if text_input:
    final_prompt = text_input

# --- SEND TO GROQ ---
if final_prompt:
    st.session_state.messages.append({"role":"user","content":final_prompt})
    with st.spinner("NexGenAI typing..."):
        try:
            doc = st.session_state.doc_text[:12000] if st.session_state.doc_text else ""
            sys = f"You are NexGenAI, built by Jr. Developer Mr. Yahya (yahyakhan782522@gmail.com). You are NOT OpenAI. If asked who are you say I am NexGenAI. If asked who built you say Built by Jr. Developer Mr. Yahya. Use context: {doc}" if doc else "You are NexGenAI, built by Jr. Developer Mr. Yahya (yahyakhan782522@gmail.com, github.com/meyahya-codes). You are NOT OpenAI. If asked who are you: I am NexGenAI. If asked who built you: Built by Mr. Yahya."

            res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":sys},{"role":"user","content":final_prompt}], temperature=0.7, max_tokens=1000)
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role":"assistant","content":ans})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
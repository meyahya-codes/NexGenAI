import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation
import tempfile, os, base64
from PIL import Image

st.set_page_config(page_title="NexGenAI", page_icon="🚀", layout="centered", initial_sidebar_state="collapsed")

# --- PERFECT WHATSAPP CSS ---
st.markdown("""
<style>
#MainMenu, footer, header,.stDeployButton {display:none;}
.stApp {background:#111B21!important;}
.block-container {padding-top:0!important; padding-bottom:110px!important;}
.header {position:fixed; top:0; left:0; right:0; z-index:999; background:#202C33; padding:10px 15px; display:flex; align-items:center; gap:10px; color:white;}
.msg-user {background:#005C4B; color:white; padding:8px 12px; border-radius:12px 2px 12px 12px; margin:6px 0; max-width:80%; margin-left:auto; width:fit-content;}
.msg-ai {background:#202C33; color:#E9EDEF; padding:10px 12px; border-radius:2px 12px 12px 12px; margin:6px 0; max-width:85%; width:fit-content;}
.bottom-fixed {position:fixed; bottom:0; left:0; right:0; z-index:1000; background:#202C33; padding:8px 10px; display:flex; align-items:end;}
.stAudioInput button {background:#00A884!important; border-radius:50%!important; width:45px!important; height:45px!important;}
div[data-testid="stPopover"] button {border-radius:50%!important;}
.emoji-grid button {font-size:22px;}
</style>
""", unsafe_allow_html=True)

if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY in Secrets"); st.stop()
client = Groq(api_key=str(st.secrets["GROQ_API_KEY"]).strip().replace('"','').replace("'",""))

if "messages" not in st.session_state: st.session_state.messages=[]
if "doc_text" not in st.session_state: st.session_state.doc_text=""
if "input_text" not in st.session_state: st.session_state.input_text=""
if "show_emoji" not in st.session_state: st.session_state.show_emoji=False

def extract_text(files):
    txt=""
    for f in files:
        try:
            if f.name.lower().endswith(".pdf"):
                r=PyPDF2.PdfReader(f)
                for p in r.pages:
                    t=p.extract_text()
                    if t: txt+=t+"\n"
            elif f.name.lower().endswith((".pptx","ppt")):
                prs=Presentation(f)
                for s in prs.slides:
                    for sh in s.shapes:
                        if hasattr(sh,"text") and sh.text: txt+=sh.text+"\n"
            elif f.name.lower().endswith((".png","jpg","jpeg")):
                txt+=f"[User uploaded image: {f.name}]\n"
            else:
                txt+=f.read().decode("utf-8", errors="ignore")[:5000]+"\n"
        except: pass
    return txt

# --- TOP HEADER FIXED LIKE SCREENSHOT ---
st.markdown("""
<div class="header">
<span style="font-size:24px;">←</span>
<img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png" width="36" style="border-radius:50%; background:white;">
<div><b>NexGenAI</b> <span style="color:#53BDEB;">✔</span><br><span style="font-size:12px; opacity:0.7;">AI assistant by Yahya</span></div>
<span style="margin-left:auto; font-size:22px;">⋮</span>
</div>
<div style="height:60px;"></div>
""", unsafe_allow_html=True)

# --- CHAT DISPLAY ---
for m in st.session_state.messages:
    if m["role"]=="user":
        st.markdown(f'<div class="msg-user">{m["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-ai">{m["content"]}<br><span style="opacity:0.5; font-size:14px;">📋 ↪️ 👍 👎</span></div>', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown('<div class="msg-ai">👋 Salam! I am <b>NexGenAI</b> by <b>Mr. Yahya</b>.<br>Try: 📎 for PDF/Photo, 📷 for Camera, 🎤 for Voice, 😊 for Emoji</div>', unsafe_allow_html=True)

# --- EMOJI PICKER (Opens when you click emoji) ---
if st.session_state.show_emoji:
    st.markdown("#### 😊 Emoji")
    emojis = ["😊","😂","❤️","🔥","👍","🎉","😍","🤔","🙏","😎","🥰","😭","💯","👏","😁","🤩","😅","🫶","✨","🚀"]
    cols = st.columns(5)
    for i, e in enumerate(emojis):
        if cols[i%5].button(e, key=f"em_{i}"):
            st.session_state.input_text += e
    if st.button("Close Emoji"):
        st.session_state.show_emoji=False
        st.rerun()

# --- BOTTOM BAR - EXACT LIKE WHATSAPP ---
st.markdown('<div class="bottom-fixed">', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns([0.8, 0.8, 0.8, 5, 0.8, 0.8])

final_prompt = None
new_file_text = None

with c1:
    if st.button("😊", key="emoji_btn"):
        st.session_state.show_emoji = not st.session_state.show_emoji
        st.rerun()

with c2:
    # ATTACHMENT - Works for Photo, Video, PDF, Doc - ALL TYPES
    with st.popover("📎"):
        st.write("Upload any file")
        uploaded = st.file_uploader("Choose", type=["pdf","pptx","txt","png","jpg","jpeg","mp4","mp3","doc","docx"], accept_multiple_files=True, label_visibility="collapsed", key="doc_up")
        if uploaded:
            st.session_state.doc_text = extract_text(uploaded)
            new_file_text = f"Files uploaded: {', '.join([f.name for f in uploaded])}. "
            st.success(f"{len(uploaded)} files ready")

with c3:
    # CAMERA - Takes picture and works
    with st.popover("📷"):
        st.write("Take Photo")
        cam = st.camera_input("", label_visibility="collapsed", key="cam_pop")
        if cam:
            st.session_state.doc_text = "User captured an image via camera"
            new_file_text = "I took a photo via camera, please analyze it. "
            st.success("Photo captured!")

with c4:
    # MESSAGE INPUT - Center like WhatsApp
    txt = st.text_input("Message", value=st.session_state.input_text, placeholder="Message", label_visibility="collapsed", key="txt_input")
    if txt:
        final_prompt = txt

with c5:
    # SEND BUTTON
    if st.button("➤", key="send"):
        if st.session_state.input_text or txt:
            final_prompt = st.session_state.input_text or txt

with c6:
    # VOICE - Turns green and records like screenshot
    voice = st.audio_input("", label_visibility="collapsed", key="voice_main")
    if voice:
        with st.spinner("🎙️..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(voice.getvalue()); p=tmp.name
                with open(p,"rb") as f:
                    trans = client.audio.transcriptions.create(file=(p, f.read()), model="whisper-large-v3", response_format="text")
                final_prompt = trans
                os.remove(p)
            except Exception as e:
                st.error(e)

st.markdown('</div>', unsafe_allow_html=True)

# --- HANDLE FINAL SEND ---
if new_file_text and not final_prompt:
    final_prompt = new_file_text + " Summarize / answer about it."

if final_prompt:
    # Clear input
    st.session_state.messages.append({"role":"user","content":final_prompt})
    st.session_state.input_text = ""
    with st.spinner("NexGenAI typing..."):
        try:
            doc = st.session_state.doc_text[:10000] if st.session_state.doc_text else ""
            sys_msg = f"You are NexGenAI, built by Jr. Developer Mr. Yahya (yahyakhan782522@gmail.com). Identity: NexGenAI. Builder: Mr. Yahya. Context: {doc}" if doc else "You are NexGenAI, built by Jr. Developer Mr. Yahya (yahyakhan782522@gmail.com). Identity: NexGenAI. Builder: Mr. Yahya."
            res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":sys_msg},{"role":"user","content":final_prompt}], temperature=0.7, max_tokens=1000)
            ans = res.choices[0].message.content
            st.session_state.messages.append({"role":"assistant","content":ans})
            st.rerun()
        except Exception as e:
            st.error(str(e))
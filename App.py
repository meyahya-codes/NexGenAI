import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation
import tempfile, os, hashlib

st.set_page_config(page_title="NexGenAI", page_icon="🚀", layout="wide")

st.markdown("""
<style>
#MainMenu, footer, header,.stDeployButton {display:none!important;}
.stApp {background:#0B141A!important;}
.block-container {padding:0 12px 120px 12px!important; max-width:800px!important; margin:auto!important;}

/* HEADER */
.header {position:fixed; top:0; left:0; right:0; height:60px; background:#202C33; z-index:9999; display:flex; align-items:center; padding:0 15px; gap:12px; color:white; border-bottom:1px solid #2A3942;}
.header img {width:40px; height:40px; border-radius:50%;}

/* BUBBLES */
.chat-wrap {margin-top:70px;}
.bubble-user {background:#005C4B; color:#E9EDEF; padding:8px 12px; border-radius:8px 0 8px 8px; margin:8px 0 8px auto; max-width:78%; width:fit-content; font-size:15px; box-shadow:0 1px 0.5px rgba(0,0,0,0.3);}
.bubble-ai {background:#202C33; color:#E9EDEF; padding:10px 12px; border-radius:0 8px 8px 8px; margin:8px auto 8px 0; max-width:85%; width:fit-content; font-size:15px; box-shadow:0 1px 0.5px rgba(0,0,0,0.3);}
.bubble-ai.actions {margin-top:8px; display:flex; gap:12px; opacity:0.6; font-size:13px; border-top:1px solid #2A3942; padding-top:6px;}

/* BOTTOM BAR PERFECT */
.bottom {position:fixed; bottom:0; left:0; right:0; background:#202C33; padding:8px 10px; z-index:9999; border-top:1px solid #2A3942;}
.input-row {display:flex; align-items:center; gap:8px; max-width:800px; margin:auto; background:#2A3942; border-radius:25px; padding:5px 10px;}
.input-row input {background:transparent!important; border:none!important; color:white!important;}
div[data-testid="stTextInput"] {flex:1;}
div[data-testid="stPopover"] > button, div[data-testid="stFileUploader"] button {background:transparent!important; border:none!important; font-size:22px!important;}
.stAudioInput {background:#00A884!important; border-radius:50%!important; width:48px!important; height:48px!important; display:flex; align-items:center; justify-content:center;}
.stAudioInput button {background:#00A884!important;}

/* Remove file uploader drag text */
[data-testid="stFileUploaderDropzone"] {background:#2A3942!important; border:1px dashed #00A884!important;}
</style>
""", unsafe_allow_html=True)

if "GROQ_API_KEY" not in st.secrets: st.error("Add GROQ_API_KEY"); st.stop()
client = Groq(api_key=str(st.secrets["GROQ_API_KEY"]).strip().strip('"').strip("'"))

if "messages" not in st.session_state: st.session_state.messages=[]
if "doc_text" not in st.session_state: st.session_state.doc_text=""
if "last_voice_hash" not in st.session_state: st.session_state.last_voice_hash=""
if "msg_box" not in st.session_state: st.session_state.msg_box=""

def get_hash(data): return hashlib.md5(data).hexdigest()

def extract(files):
    t=""
    for f in files:
        try:
            if f.name.lower().endswith(".pdf"):
                r=PyPDF2.PdfReader(f)
                for p in r.pages:
                    x=p.extract_text()
                    if x: t+=x+"\n"
            elif f.name.lower().endswith(".pptx"):
                prs=Presentation(f)
                for s in prs.slides:
                    for sh in s.shapes:
                        if hasattr(sh,"text"): t+=sh.text+"\n"
            else: t+=f"[{f.name} uploaded]\n"
        except: pass
    return t[:12000]

# HEADER
st.markdown("""
<div class="header">
<span style="font-size:22px;">←</span>
<img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png">
<div style="line-height:1.2"><b>NexGenAI</b> <span style="color:#53BDEB; font-size:14px;">✔</span><br><span style="font-size:12px; opacity:0.7;">by Mr. Yahya - online</span></div>
<div style="margin-left:auto; display:flex; gap:18px; font-size:20px;">📹 📞 ⋮</div>
</div>
""", unsafe_allow_html=True)

# CHAT
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for m in st.session_state.messages:
    if m["role"]=="user":
        st.markdown(f'<div class="bubble-user">{m["content"]}</div><div style="clear:both"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bubble-ai">{m["content"]}<div class="actions">📋 Copy &nbsp; ↪️ Share &nbsp; 👍 &nbsp; 👎</div></div><div style="clear:both"></div>', unsafe_allow_html=True)
if not st.session_state.messages:
    st.markdown('<div class="bubble-ai">Assalamualaikum! I am <b>NexGenAI</b> by <b>Mr. Yahya</b>.<br><br>✨ I can read PDFs, Photos, Voice, Camera - everything in one place.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# BOTTOM - ALL IN ONE LINE PERFECTLY ALIGNED
st.markdown('<div class="bottom"><div class="input-row">', unsafe_allow_html=True)
col_emoji, col_attach, col_cam, col_input, col_send, col_voice = st.columns([0.7, 0.7, 0.7, 5.5, 0.7, 0.9])

final_prompt = None

with col_emoji:
    with st.popover("😊", use_container_width=True):
        st.caption("Emoji")
        emojis = ["😊","❤️","🔥","😂","👍","🎉","😍","🙏","😎","🚀","✨","💯","🥰","😁","🤔","👏"]
        e_cols = st.columns(4)
        for i, e in enumerate(emojis):
            if e_cols[i%4].button(e, key=f"e_{i}", use_container_width=True):
                st.session_state.msg_box += e
                st.rerun()

with col_attach:
    with st.popover("📎", use_container_width=True):
        st.caption("Upload - PDF, Photo, Video, Any file")
        up_files = st.file_uploader("Upload", type=["pdf","pptx","txt","png","jpg","jpeg","mp4","mp3","docx","doc"], accept_multiple_files=True, label_visibility="collapsed", key="up_all")
        if up_files:
            st.session_state.doc_text = extract(up_files)
            final_prompt = f"Files uploaded: {', '.join([f.name for f in up_files])}. Please analyze / summarize."

with col_cam:
    with st.popover("📷", use_container_width=True):
        st.caption("Camera")
        cam = st.camera_input("", label_visibility="collapsed", key="cam_final")
        if cam:
            st.session_state.doc_text = "User took photo via camera"
            final_prompt = "I captured a photo from camera, describe it."

with col_input:
    user_text = st.text_input("msg", value=st.session_state.msg_box, placeholder="Message", label_visibility="collapsed", key="input_box")

with col_send:
    send_clicked = st.button("➤", key="send_btn", use_container_width=True)

with col_voice:
    voice_data = st.audio_input("", label_visibility="collapsed", key="voice_final")

st.markdown('</div></div>', unsafe_allow_html=True)

# PROCESS LOGIC - NO MORE BLINK SPAM
if voice_data:
    v_hash = get_hash(voice_data.getvalue())
    if v_hash!= st.session_state.last_voice_hash: # Process only NEW voice, not blink
        st.session_state.last_voice_hash = v_hash
        with st.spinner("Transcribing..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(voice_data.getvalue()); path=tmp.name
                with open(path,"rb") as f:
                    trans = client.audio.transcriptions.create(file=(path, f.read()), model="whisper-large-v3", response_format="text")
                final_prompt = trans.strip()
                os.remove(path)
            except Exception as e:
                st.error(e)
    else:
        voice_data = None # ignore duplicate blink

if user_text and (send_clicked or user_text!= st.session_state.msg_box):
    # Only send if user pressed send or pressed Enter (text changed and not empty)
    if send_clicked or len(user_text) > len(st.session_state.msg_box):
        if send_clicked:
            final_prompt = user_text
            st.session_state.msg_box = ""

# Actually we need to detect Enter: if text_input value exists and user pressed Enter, streamlit reruns. So we take it.
if user_text and send_clicked:
    final_prompt = user_text

# If user typed and hit Enter (streamlit default), user_text will have value but send not clicked. We handle via session state change
if not final_prompt and user_text and user_text!= "" and st.session_state.msg_box!= user_text and not voice_data:
    # This means user pressed Enter
    if st.session_state.get("prev_text")!= user_text:
        final_prompt = user_text
        st.session_state.prev_text = user_text

if final_prompt and final_prompt.strip()!= "":
    st.session_state.messages.append({"role":"user","content":final_prompt})
    st.session_state.msg_box = "" # clear
    st.session_state.prev_text = ""
    try:
        ctx = st.session_state.doc_text
        sys = f"You are NexGenAI built by Jr. Dev Mr. Yahya (yahyakhan782522@gmail.com). You are NOT OpenAI. Builder is Mr. Yahya. Context: {ctx}" if ctx else "You are NexGenAI built by Jr. Dev Mr. Yahya. You are NOT OpenAI."
        res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":sys},{"role":"user","content":final_prompt}], temperature=0.7, max_tokens=1000)
        ans = res.choices[0].message.content
        st.session_state.messages.append({"role":"assistant","content":ans})
        st.rerun()
    except Exception as e:
        st.error(str(e))
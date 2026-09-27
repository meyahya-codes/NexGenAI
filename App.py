import streamlit as st
from groq import Groq
import PyPDF2, tempfile, os, hashlib

st.set_page_config(page_title="NexGenAI", page_icon="🚀", layout="centered")
st.markdown("""
<style>
#MainMenu,footer,header,.stDeployButton{display:none;}
.stApp{background:#0B141A!important;}
.block-container{padding-bottom:100px!important; max-width:800px!important;}

/* ONE BOX STYLE */
.chat-box{
background:#202C33; border-radius:28px; padding:6px 8px;
display:flex; align-items:center; gap:2px;
position:fixed; bottom:12px; left:50%; transform:translateX(-50%);
width:95%; max-width:800px; z-index:9999;
box-shadow:0 4px 20px rgba(0,0,0,0.5);
}
.chat-box button{background:transparent!important; border:none!important; font-size:22px!important; padding:0 4px!important;}
.chat-box [data-testid="stTextInput"] input{background:transparent!important; border:none!important; color:white!important; font-size:16px!important;}
.chat-box [data-testid="stTextInput"]{flex:1;}
.stAudioInput{width:42px!important; height:42px!important; background:#00A884!important; border-radius:50%!important;}
.b-user{background:#005C4B; color:white; padding:8px 12px; border-radius:12px 0 12px 12px; margin:8px 0 8px auto; max-width:80%; width:fit-content; float:right; clear:both;}
.b-ai{background:#202C33; color:#E9EDEF; padding:10px 12px; border-radius:0 12px 12px 12px; margin:8px 0; max-width:85%; width:fit-content; float:left; clear:both;}
</style>
""", unsafe_allow_html=True)

client = Groq(api_key=str(st.secrets["GROQ_API_KEY"]).strip().strip('"').strip("'"))
if "messages" not in st.session_state: st.session_state.messages=[]
if "doc_text" not in st.session_state: st.session_state.doc_text=""
if "last_hash" not in st.session_state: st.session_state.last_hash=""

def extract(files):
    t=""
    for f in files:
        try:
            if f.name.endswith(".pdf"):
                r=PyPDF2.PdfReader(f)
                for p in r.pages:
                    x=p.extract_text()
                    if x: t+=x+"\n"
        except: pass
    return t[:10000]

# HEADER
st.markdown('<div style="background:#202C33; padding:12px; display:flex; gap:10px; align-items:center; color:white; position:fixed; top:0; left:0; right:0; z-index:999; border-bottom:1px solid #2A3942;"><span>←</span> <img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png" width="35" style="border-radius:50%;"> <b>NexGenAI ✔</b></div><div style="height:65px;"></div>', unsafe_allow_html=True)

# CHAT
for m in st.session_state.messages:
    cls="b-user" if m["role"]=="user" else "b-ai"
    st.markdown(f'<div class="{cls}">{m["content"]}</div><div style="clear:both"></div>', unsafe_allow_html=True)

st.markdown('<div style="height:80px;"></div>', unsafe_allow_html=True)

# --- ONE BOX WITH ALL INSIDE ---
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns([0.8,0.8,0.8,4.5,1])

final=None

with c1:
    with st.popover("😊", use_container_width=True):
        for e in ["😊","❤️","🔥","😂","👍","🎉","😍","🙏"]:
            if st.button(e, key=f"e{e}"):
                st.session_state.msg = st.session_state.get("msg","")+e

with c2:
    with st.popover("📎", use_container_width=True):
        ups = st.file_uploader("", type=["pdf","png","jpg","jpeg","mp4","mp3","docx"], accept_multiple_files=True, label_visibility="collapsed")
        if ups:
            st.session_state.doc_text = extract(ups)
            final = f"File: {ups[0].name} - analyze it"

with c3:
    with st.popover("📷", use_container_width=True):
        cam = st.camera_input("", label_visibility="collapsed")
        if cam:
            final = "Photo from camera - describe it"

with c4:
    txt = st.text_input("", placeholder="Message", label_visibility="collapsed", key="msg")
    if txt: final = txt

with c5:
    voice = st.audio_input("", label_visibility="collapsed")
    if voice:
        h = hashlib.md5(voice.getvalue()).hexdigest()
        if h!= st.session_state.last_hash:
            st.session_state.last_hash = h
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(voice.getvalue()); p=tmp.name
            with open(p,"rb") as f:
                tr = client.audio.transcriptions.create(file=(p,f.read()), model="whisper-large-v3", response_format="text")
            final = tr
            os.remove(p)

st.markdown('</div>', unsafe_allow_html=True)

if final:
    st.session_state.messages.append({"role":"user","content":final})
    sys = f"You are NexGenAI by Mr. Yahya. Context: {st.session_state.doc_text}" if st.session_state.doc_text else "You are NexGenAI by Mr. Yahya."
    res = client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":sys},{"role":"user","content":final}], max_tokens=800)
    st.session_state.messages.append({"role":"assistant","content":res.choices[0].message.content})
    st.rerun()
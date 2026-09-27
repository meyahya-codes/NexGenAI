import streamlit as st
from groq import Groq
import PyPDF2, hashlib, tempfile, os
from pptx import Presentation
from datetime import datetime

st.set_page_config(page_title="NexGenAI Pro", page_icon="🚀", layout="wide")

# --- BEAUTIFUL REALISTIC CSS ---
st.markdown("""
<style>
#MainMenu,footer,header,.stDeployButton{display:none;}
.stApp{background:#0B141A!important;}
.block-container{padding-top:10px!important; padding-bottom:110px!important; max-width:850px!important;}
[data-testid="stSidebar"]{background:#111B21!important; border-right:1px solid #2A3942;}
.b-user{background:#005C4B; color:#E9EDEF; padding:9px 13px; border-radius:12px 0 12px 12px; margin:8px 0 8px auto; max-width:78%; width:fit-content; float:right; clear:both; font-size:15px; box-shadow:0 1px 2px rgba(0,0,0,0.3);}
.b-ai{background:#202C33; color:#E9EDEF; padding:11px 14px; border-radius:0 12px 12px 12px; margin:8px 0; max-width:85%; width:fit-content; float:left; clear:both; font-size:15px; line-height:1.5; box-shadow:0 1px 2px rgba(0,0,0,0.3);}
.bottom-box{position:fixed; bottom:14px; left:50%; transform:translateX(-50%); width:94%; max-width:780px; background:#202C33; border-radius:26px; padding:7px 10px; display:flex; align-items:center; z-index:9999; box-shadow:0 6px 30px rgba(0,0,0,0.5); border:1px solid #2A3942;}
.stAudioInput{width:44px!important; height:44px!important; background:#00A884!important; border-radius:50%!important;}
</style>
""", unsafe_allow_html=True)

client = Groq(api_key=str(st.secrets["GROQ_API_KEY"]).strip().strip('"').strip("'"))

if "messages" not in st.session_state: st.session_state.messages=[]
if "doc_text" not in st.session_state: st.session_state.doc_text=""
if "last_hash" not in st.session_state: st.session_state.last_hash=""
if "file_list" not in st.session_state: st.session_state.file_list=[]

def extract(files):
    t=""; names=[]
    for f in files:
        names.append(f.name)
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
                        if hasattr(sh,"text") and sh.text: t+=sh.text+"\n"
            elif f.name.lower().endswith((".txt","py","js","csv")):
                t+=f.getvalue().decode("utf-8", errors="ignore")[:5000]+"\n"
            else:
                t+=f"[{f.name} image/video uploaded]\n"
        except: pass
    st.session_state.file_list = names
    return t[:15000]

# --- SIDEBAR - ABOUT, HISTORY, HOW TO USE ---
with st.sidebar:
    st.markdown("### 🚀 NexGenAI Pro")
    st.caption("AI Assistant by Mr. Yahya")
    st.divider()

    st.markdown("#### 👨‍💻 About Developer")
    st.markdown("""
    **Jr. Developer Mr. Yahya**
    - 📧 yahyakhan782522@gmail.com
    - 💻 GitHub: meyahya-codes
    - 🌍 Peshawar, Pakistan
    - 🛠️ Built with Groq + Streamlit
    """)

    st.divider()
    st.markdown("#### 📜 Chat History")
    if st.session_state.messages:
        for i, m in enumerate(st.session_state.messages[-6:]):
            role = "You" if m["role"]=="user" else "AI"
            st.caption(f"{i+1}. {role}: {m['content'][:40]}...")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages=[]
            st.session_state.doc_text=""
            st.session_state.file_list=[]
            st.rerun()
    else:
        st.caption("No history yet")

    st.divider()
    st.markdown("#### 📖 How to Use")
    st.markdown("""
    1. 😊 **Emoji** - Click to add emoji
    2. 📎 **Upload** - PDF, PPT, Photo, Video, Any file (unlimited)
    3. 📷 **Camera** - Take photo directly
    4. 🎤 **Voice** - Speak, auto transcribes
    5. 💬 **Ask** - Type any question
    """)

    if st.session_state.file_list:
        st.divider()
        st.markdown("#### 📂 Uploaded Files")
        for f in st.session_state.file_list:
            st.caption(f"📄 {f}")

    st.divider()
    st.markdown("<center>Made with ❤️ and ☕ by <b>Mr. Yahya</b><br><small>NexGenAI v2.0 • 2026</small></center>", unsafe_allow_html=True)

# --- MAIN CHAT HEADER ---
st.markdown("""
<div style="background:#202C33; padding:12px 18px; border-radius:12px; display:flex; align-items:center; gap:12px; color:white; margin-bottom:15px;">
<img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png" width="38" style="border-radius:50%; background:white;">
<div><b>NexGenAI</b> <span style="color:#53BDEB;">✔</span><br><span style="font-size:12px; opacity:0.7;">AI Assistant • Online • Groq Powered</span></div>
<div style="margin-left:auto; font-size:12px; opacity:0.6;">{}</div>
</div>
""".format(datetime.now().strftime("%d %b %I:%M %p")), unsafe_allow_html=True)

# CHAT BUBBLES
if not st.session_state.messages:
    st.markdown("""
    <div class="b-ai">
    <b>Assalamualaikum! 👋 I am NexGenAI</b><br><br>
    I can help you with:<br>
    • 📄 Read PDFs, PPTs, Docs<br>
    • 🖼️ Analyze Photos<br>
    • 🎤 Voice Messages<br>
    • 💻 Code & Study<br><br>
    <i>Try: "Who are you?" or upload a file from 📎</i>
    </div><div style="clear:both"></div>
    """, unsafe_allow_html=True)

for m in st.session_state.messages:
    cls = "b-user" if m["role"]=="user" else "b-ai"
    time = datetime.now().strftime("%I:%M %p")
    st.markdown(f'<div class="{cls}">{m["content"]}<br><span style="font-size:10px; opacity:0.6; float:right; margin-top:4px;">{time} ✓✓</span></div><div style="clear:both"></div>', unsafe_allow_html=True)

st.markdown('<div style="height:90px;"></div>', unsafe_allow_html=True)

# --- ONE ROUNDED BOX BOTTOM ---
st.markdown('<div class="bottom-box">', unsafe_allow_html=True)
c1,c2,c3,c4,c5 = st.columns([0.7,0.7,0.7,5,1])

final_prompt = None

with c1:
    with st.popover("😊"):
        st.write("**Emoji**")
        grid = ["😊","❤️","🔥","😂","👍","🎉","😍","🙏","😎","🚀","✨","💯","🥰","😭","🤔","👏","💪","🫶"]
        cols = st.columns(4)
        for i,e in enumerate(grid):
            if cols[i%4].button(e, key=f"emo_{i}"):
                st.session_state["msg_input"] = st.session_state.get("msg_input","") + e
                st.rerun()

with c2:
    with st.popover("📎"):
        st.markdown("**📂 Upload Files (Unlimited)**")
        st.caption("PDF, PPTX, Images, Videos, Docs - Any type")
        files = st.file_uploader("Drag & Drop or Browse", type=["pdf","pptx","ppt","png","jpg","jpeg","mp4","mp3","txt","docx","doc","csv","py"], accept_multiple_files=True, label_visibility="collapsed", key="uploader")
        if files:
            st.session_state.doc_text = extract(files)
            st.success(f"✅ {len(files)} file(s) loaded!")
            for f in files: st.caption(f"📄 {f.name} - {round(f.size/1024,1)} KB")
            final_prompt = f"I uploaded {len(files)} files: {', '.join([f.name for f in files])}. Please summarize and be ready to answer questions."

with c3:
    with st.popover("📷"):
        st.markdown("**📷 Camera**")
        cam = st.camera_input("Take photo", label_visibility="collapsed")
        if cam:
            st.session_state.doc_text = "User captured photo via camera"
            final_prompt = "I took a photo via camera, please describe what you see."

with c4:
    txt = st.text_input("msg_input", placeholder="Message", label_visibility="collapsed", key="msg_input")

with c5:
    voice = st.audio_input("", label_visibility="collapsed")
    if voice:
        h = hashlib.md5(voice.getvalue()).hexdigest()
        if h!= st.session_state.last_hash:
            st.session_state.last_hash = h
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(voice.getvalue()); path=tmp.name
            with open(path,"rb") as f:
                tr = client.audio.transcriptions.create(file=(path, f.read()), model="whisper-large-v3", response_format="text")
            final_prompt = tr.strip()
            os.remove(path)

st.markdown('</div>', unsafe_allow_html=True)

# SEND LOGIC - NO INFINITE LOOP
if txt and st.session_state.get("send_trig"):
    final_prompt = txt

col_s1, col_s2 = st.columns([6,1])
with col_s2:
    if st.button("➤ Send", use_container_width=True, key="send_btn"):
        if txt: final_prompt = txt
        st.session_state["send_trig"] = True

# --- HANDLE MESSAGE ---
if final_prompt and final_prompt.strip():
    low = final_prompt.lower()

    # Direct canned answers - prevents loop bug
    if low.strip() in ["who are you","who are you?","who r u","whats your name","tum kaun ho"] or "who are you" in low:
        st.session_state.messages.append({"role":"user","content":final_prompt})
        st.session_state.messages.append({"role":"assistant","content":"I am **NexGenAI Pro** 🚀\n\nBuilt with ❤️ and ☕ by **Jr. Developer Mr. Yahya**\n\n📧 yahyakhan782522@gmail.com\n💻 github.com/meyahya-codes\n\nI can read PDFs, analyze photos, transcribe voice & help with studies!"})
        st.rerun()
    elif "who built you" in low or "who made you" in low or "kisne banaya" in low:
        st.session_state.messages.append({"role":"user","content":final_prompt})
        st.session_state.messages.append({"role":"assistant","content":"I was built by **Mr. Yahya** - Jr. Developer from Peshawar, Pakistan 🇵🇰\n\nMade with ❤️ and ☕"})
        st.rerun()
    else:
        st.session_state.messages.append({"role":"user","content":final_prompt})
        try:
            context = st.session_state.doc_text[:12000]
            sys_prompt = f"You are NexGenAI Pro by Mr. Yahya. Be helpful, short, accurate. Never loop. Context files: {context}" if context else "You are NexGenAI Pro by Mr. Yahya. Be helpful, short, accurate. Never loop. If asked who are you, say NexGenAI by Mr. Yahya."
            res = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role":"system","content":sys_prompt},{"role":"user","content":final_prompt}],
                max_tokens=600,
                temperature=0.6,
            )
            ans = res.choices[0].message.content[:2000]
            st.session_state.messages.append({"role":"assistant","content":ans})
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
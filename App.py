import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation
from fpdf import FPDF
import tempfile, os

st.set_page_config(page_title="NexGenAI Pro", page_icon="🚀", layout="centered")
st.markdown("<style>#MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}.stDeployButton{display:none;}.voice-box{border:1px solid #333; border-radius:12px; padding:10px;}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🚀 NexGenAI Pro")
    st.caption("by Mr. Yahya")
    st.divider()
    st.markdown("### 📁 Upload Doc")
    uploaded_files = st.file_uploader("", type=["pdf","pptx","txt"], accept_multiple_files=True, label_visibility="collapsed")
    st.divider()
    if st.session_state.get("messages"):
        def create_pdf():
            pdf=FPDF(); pdf.add_page(); pdf.set_font("Arial",size=11)
            pdf.cell(0,10,"NexGenAI Pro - Chat History",ln=True,align='C'); pdf.ln(5)
            for m in st.session_state.messages:
                role="You" if m["role"]=="user" else "NexGenAI"
                txt=m["content"].encode('latin-1','replace').decode('latin-1')
                pdf.multi_cell(0,7,f"{role}: {txt}"); pdf.ln(3)
            return pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 Download Chat PDF", data=create_pdf(), file_name="NexGenAI_Chat.pdf", mime="application/pdf", use_container_width=True)
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages=[]; st.session_state.doc_text=""; st.rerun()
    st.divider()
    st.markdown("**Mr. Yahya**\n📧 yahyakhan782522@gmail.com\n💻 github.com/meyahya-codes")

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
if uploaded_files: st.session_state.doc_text=extract_text(uploaded_files)

st.title("🚀 NexGenAI Pro")
st.caption("ChatGPT Style - Type or Speak")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

# --- CHATGPT STYLE INPUT AREA ---
st.markdown("---")
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("🎙️ **Voice**")
    audio_value = st.audio_input("", label_visibility="collapsed")
with col2:
    st.markdown("⌨️ **Type**")
    text_prompt = st.chat_input("Ask anything...")

final_prompt = None

# Voice logic
if audio_value:
    with st.spinner("🎙️ Listening..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_value.getvalue()); tmp_path=tmp.name
            with open(tmp_path,"rb") as f:
                transcription = client.audio.transcriptions.create(file=(tmp_path, f.read()), model="whisper-large-v3", response_format="text")
            final_prompt = transcription
            os.remove(tmp_path)
            st.toast(f"You said: {final_prompt}")
        except Exception as e:
            st.error(f"Voice error: {e}")

if text_prompt: final_prompt = text_prompt

if final_prompt:
    st.session_state.messages.append({"role":"user","content":final_prompt})
    with st.chat_message("user"): st.markdown(final_prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            doc=st.session_state.doc_text[:12000] if st.session_state.doc_text else ""
            sys=f"You are NexGenAI, built by Jr. Dev Mr. Yahya (yahyakhan782522@gmail.com). You are NOT OpenAI. Context: {doc}" if doc else "You are NexGenAI, built by Jr. Dev Mr. Yahya (yahyakhan782522@gmail.com, github.com/meyahya-codes). You are NOT OpenAI."
            res=client.chat.completions.create(model="openai/gpt-oss-20b", messages=[{"role":"system","content":sys},{"role":"user","content":final_prompt}], temperature=0.7, max_tokens=1200)
            ans=res.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role":"assistant","content":ans})
            st.rerun()
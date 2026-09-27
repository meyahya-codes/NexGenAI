import streamlit as st
from groq import Groq
import PyPDF2
from pptx import Presentation
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="NexGenAI Pro", page_icon="🚀", layout="centered")

st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
.stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🚀 NexGenAI Pro")
    st.caption("by Mr. Yahya")
    st.divider()
    st.markdown("### 📁 Upload Doc")
    uploaded_files = st.file_uploader("", type=["pdf","pptx","txt"], accept_multiple_files=True, label_visibility="collapsed")

    st.markdown("### 🎙️ Voice Input")
    audio_value = st.audio_input("Record your question")

    st.divider()
    # Download Chat as PDF
    def create_chat_pdf():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="NexGenAI Pro - Chat History", ln=True, align='C')
        pdf.cell(200, 10, txt="Built by Mr. Yahya | yahyakhan782522@gmail.com", ln=True, align='C')
        pdf.ln(10)
        for msg in st.session_state.messages:
            role = "You" if msg["role"]=="user" else "NexGenAI"
            # clean emojis for pdf
            content = msg["content"].encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 8, f"{role}: {content}")
            pdf.ln(4)
        return pdf.output(dest='S').encode('latin-1')

    if st.session_state.get("messages"):
        pdf_bytes = create_chat_pdf()
        st.download_button("📥 Download Chat as PDF", data=pdf_bytes, file_name="NexGenAI_Chat.pdf", mime="application/pdf", use_container_width=True)

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

    st.divider()
    st.markdown("### 👨‍💻 Developer")
    st.markdown("**Mr. Yahya**\nJr. Dev & Founder\n\n📧 yahyakhan78252@gmail.com\n💻 github.com/meyahya-codes")

if "GROQ_API_KEY" not in st.secrets:
    st.error("Add GROQ_API_KEY in Secrets")
    st.stop()

client = Groq(api_key=str(st.secrets["GROQ_API_KEY"]).strip().replace('"','').replace("'",""))

def extract_text(files):
    txt=""
    for f in files:
        try:
            if f.name.endswith(".pdf"):
                reader=PyPDF2.PdfReader(f)
                for p in reader.pages:
                    t=p.extract_text()
                    if t: txt+=t+"\n"
            elif f.name.endswith(".pptx"):
                prs=Presentation(f)
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

st.title("🚀 NexGenAI Pro")
st.caption("Chat, Voice, Docs - All in one")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle Voice Input
prompt_from_voice = None
if audio_value:
    with st.spinner("Transcribing voice..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_value.getvalue())
                tmp_path = tmp.name

            with open(tmp_path, "rb") as file:
                transcription = client.audio.transcriptions.create(
                    file=(tmp_path, file.read()),
                    model="whisper-large-v3",
                    response_format="text"
                )
            prompt_from_voice = transcription
            os.remove(tmp_path)
            st.success(f"You said: {prompt_from_voice}")
        except Exception as e:
            st.error(f"Voice Error: {e}")

final_prompt = None
if prompt_from_voice:
    final_prompt = prompt_from_voice
if p := st.chat_input("Ask or use voice recorder in sidebar..."):
    final_prompt = p

if final_prompt:
    st.session_state.messages.append({"role":"user","content":final_prompt})
    with st.chat_message("user"): st.markdown(final_prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                doc = st.session_state.doc_text[:12000] if st.session_state.doc_text else ""
                sys = f"You are NexGenAI, built by Jr. Developer Mr. Yahya (yahyakhan782522@gmail.com). You are NOT OpenAI. If asked who are you: I am NexGenAI. If asked who built you: Built by Jr. Dev Mr. Yahya. Context: {doc}" if doc else "You are NexGenAI, built by Jr. Dev Mr. Yahya (yahyakhan782522@gmail.com, github.com/meyahya-codes). You are NOT OpenAI. If asked who are you: I am NexGenAI. If asked who built you: Built by Jr. Dev Mr. Yahya."

                res = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[{"role":"system","content":sys},{"role":"user","content":final_prompt}],
                    temperature=0.7, max_tokens=1200
                )
                ans=res.choices[0].message.content
                st.markdown(ans)
                st.session_state.messages.append({"role":"assistant","content":ans})
            except Exception as e:
                st.error(f"Error: {e}")

if not st.session_state.messages:
    st.info("👋 Hi! I'm NexGenAI by Mr. Yahya. Type or Speak from sidebar!")
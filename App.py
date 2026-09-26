import streamlit as st
from google import genai
import PyPDF2
import datetime

st.set_page_config(page_title="NexGenAI Pro", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .developer-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; color: white;}
    .developer-card a {color: #FFEB3B; text-decoration: none; font-weight: bold;}
    .contact-btn {display: inline-block; background: white; color: #764ba2 !important; padding: 6px 14px; border-radius: 20px; margin: 4px; font-size: 13px;}
    .guide-box {background: #262730; padding: 12px; border-radius: 10px; border-left: 4px solid #667eea;}
</style>
""", unsafe_allow_html=True)

# --- SECURE API KEY - 100% SAFE FOR GITHUB ---
api_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.secrets.get("general", {}).get("GEMINI_API_KEY", "")
except:
    api_key = ""

if not api_key:
    st.warning("⚠️ API Key not found! Add it in Streamlit Secrets")

# Only create client if key exists
client = None
if api_key:
    client = genai.Client(api_key="")

# --- SESSION HISTORY ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# --- SIDEBAR ---
with st.sidebar:
    try:
        st.image("logo.png", width=130)
    except:
        st.title("🧠 NexGenAI Pro")
    
    st.markdown("---")
    st.subheader("📚 Chat History (ChatGPT Style)")
    if st.session_state.chat_history:
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            title = chat['question'][:32]
            if st.button(f"💬 {title}", key=f"h_{i}", use_container_width=True):
                st.session_state.current_answer = chat['answer']
                st.session_state.current_question = chat['question']
        st.markdown("---")
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_answer = ""
            st.rerun()
        all_text = "\n\n---\n\n".join([f"Q: {c['question']}\nA: {c['answer']}\nTime:{c['time']}" for c in st.session_state.chat_history])
        st.download_button("📥 Download All History", all_text, "history.txt")
    else:
        st.info("No history yet. Start chatting!")

    st.markdown("---")
    st.subheader("📖 How to Use This App")
    st.markdown("""
    <div class='guide-box'>
    <b>1.</b> Upload any PDF (books, notes)<br>
    <b>2.</b> Ask: "Make 10 slides" / "Summarize"<br>
    <b>3.</b> Get instant AI result<br>
    <b>4.</b> History auto-saves on left<br>
    <b>5.</b> Click old chat to retrieve anytime
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("👨‍💻 About The Developer")
    st.markdown("""
    <div class='developer-card'>
    <h3>Yahya Khan</h3>
    <p><b>🎓 BCS Student</b><br>
    AI Developer | EdTech Creator<br>
    Making AI accessible for Pakistani students.</p>
    <p>
    <a class='contact-btn' href='mailto:yahyakhan78252@gmail.com'>📧 Email</a>
    <a class='contact-btn' href='https://wa.me/923431578252' target='_blank'>💬 WhatsApp</a>
    <a class='contact-btn' href='https://github.com/meyahya-codes' target='_blank'>💻 GitHub</a>
    </p>
    <p style='font-size:12px; margin-top:12px; line-height:1.5'>
    📧 yahyakhan78252@gmail.com<br>
    📱 03431578252<br>
    💻 github.com/meyahya-codes<br>
    📍 Manki, KPK, Pakistan
    </p>
    </div>
    """, unsafe_allow_html=True)
    st.caption("© 2026 NexGenAI | Built by Yahya")

# --- MAIN APP ---
st.title("🚀 NexGenAI - AI Presentation Assistant")
st.caption("Chat with your PDFs like ChatGPT + Auto History Save")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")
with col2:
    question = st.text_area("❓ Your Question", height=140, placeholder="Ex: Create 10 slides with titles & bullet points from this PDF")

pdf_text = ""
if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    for p in reader.pages:
        pdf_text += (p.extract_text() or "") + "\n"
    st.success(f"✅ Loaded: {uploaded_file.name} | {len(reader.pages)} pages | {len(pdf_text)} chars")

    if st.button("✨ Generate Answer", type="primary", use_container_width=True):
        if not api_key or not client:
            st.error("API Key missing! Go to Streamlit Cloud > App > Settings > Secrets and add GEMINI_API_KEY")
        elif not question.strip():
            st.warning("Please type your question!")
        else:
            with st.spinner("🤖 NexGenAI is thinking..."):
                try:
                    prompt = f"PDF Content:\n{pdf_text[:15000]}\n\nUser Task: {question}\n\nGive professional, well-formatted answer with headings, bullets, emojis."
                    response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
                    ans = response.text
                    
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": ans,
                        "time": datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                        "pdf": uploaded_file.name
                    })
                    st.session_state.current_answer = ans
                    st.session_state.current_question = question
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("Check your GEMINI_API_KEY in Streamlit Secrets is correct")
else:
    st.info("👋 Upload a PDF to start. You can ask for slides, summary, quiz, etc.")

if st.session_state.current_answer:
    st.markdown("---")
    st.subheader(f"Answer: {st.session_state.current_question}")
    st.markdown(st.session_state.current_answer)
    st.download_button("📥 Download This Answer", st.session_state.current_answer, file_name="answer.txt")

st.markdown("---")
st.markdown("<center>© 2026 NexGenAI | Made with ❤️ by Yahya Khan - BCS Student</center>", unsafe_allow_html=True)
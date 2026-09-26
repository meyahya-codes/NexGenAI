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

api_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = ""

client = None
if api_key:
    client = genai.Client(api_key=api_key)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""
if "current_question" not in st.session_state:
    st.session_state.current_question = ""

with st.sidebar:
    st.title("🧠 NexGenAI Pro")
    st.markdown("---")
    st.subheader("📚 Chat History")
    if st.session_state.chat_history:
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            title = chat['question'][:32]
            if st.button(f"💬 {title}", key=f"h_{i}", use_container_width=True):
                st.session_state.current_answer = chat['answer']
                st.session_state.current_question = chat['question']
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.info("No history yet")

    st.markdown("---")
    st.subheader("📖 How to Use")
    st.markdown("<div class='guide-box'>1. Upload PDF<br>2. Ask question<br>3. Get AI answer<br>4. History auto-saves</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("👨‍💻 About The Developer")
    st.markdown("""
    <div class='developer-card'>
    <h3>Yahya Khan</h3>
    <p><b>🎓 BCS Student</b><br>AI Developer</p>
    <p>
    <a class='contact-btn' href='mailto:yahyakhan78252@gmail.com'>📧 Email</a>
    <a class='contact-btn' href='https://wa.me/923431578252' target='_blank'>💬 WhatsApp</a>
    <a class='contact-btn' href='https://github.com/meyahya-codes' target='_blank'>💻 GitHub</a>
    </p>
    <p style='font-size:12px'>📧 yahyakhan78252@gmail.com<br>📱 03431578252<br>📍 Manki, KPK</p>
    </div>
    """, unsafe_allow_html=True)

st.title("🚀 NexGenAI")
st.caption("Chat with PDFs like ChatGPT")

col1, col2 = st.columns(2)
with col1:
    uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")
with col2:
    question = st.text_area("❓ Your Question", height=140, placeholder="Make 10 slides / Summarize")

pdf_text = ""
if uploaded_file:
    reader = PyPDF2.PdfReader(uploaded_file)
    for p in reader.pages:
        pdf_text += (p.extract_text() or "") + "\n"
    st.success(f"✅ Loaded {len(reader.pages)} pages")

    if st.button("✨ Generate Answer", type="primary", use_container_width=True):
        if not client:
            st.error("Add GEMINI_API_KEY in Streamlit Secrets!")
        elif not question.strip():
            st.warning("Type question!")
        else:
            with st.spinner("Thinking..."):
                try:
                    prompt = f"PDF:\n{pdf_text[:15000]}\n\nTask: {question}\nGive formatted answer"
                    # LINE 115 - FIXED MODEL NAME HERE
                    response = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                    ans = response.text
                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": ans,
                        "time": datetime.datetime.now().strftime("%d-%m %H:%M"),
                        "pdf": uploaded_file.name
                    })
                    st.session_state.current_answer = ans
                    st.session_state.current_question = question
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

if st.session_state.current_answer:
    st.markdown("---")
    st.subheader(f"Answer: {st.session_state.current_question}")
    st.markdown(st.session_state.current_answer)
    st.download_button("📥 Download", st.session_state.current_answer, "answer.txt")
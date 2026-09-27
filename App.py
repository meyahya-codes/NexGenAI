import streamlit as st
import os
from groq import Groq
import PyPDF2
from pptx import Presentation
from PIL import Image

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NexGenAI - by Yahya",
    page_icon="logo.png" if os.path.exists("logo.png") else "🤖",
    layout="wide"
)

# --- CSS - NAVBAR + ONE BOX ---
st.markdown("""
<style>
.navbar {
    background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
    padding: 12px 20px;
    border-radius: 12px;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}
.navbar b { font-size: 22px; }
.chat-box { border-radius: 15px; }
</style>
<div class="navbar">
    <b>🤖 NexGenAI</b>
    <span>Built by Yahya | Realistic AI Assistant</span>
</div>
""", unsafe_allow_html=True)

# --- GROQ CLIENT ---
client = Groq(api_key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"))

# --- SYSTEM PROMPT - CONCISE ---
SYSTEM_PROMPT = """
You are NexGenAI, created and built by Yahya.
Rules:
1. Be concise, to-the-point, no extra talk.
2. Answer in user's language (Urdu/Hindi/English).
3. Never say you are Meta AI, Llama, ChatGPT. You are NexGenAI by Yahya.
4. For who are you: Reply only "I am NexGenAI built by Yahya."
5. No long intro, give direct solution.
"""

# --- SIDEBAR - ABOUT + SETTINGS ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=120)
    st.title("About NexGenAI")
    st.markdown("""
    **NexGenAI** is a realistic AI assistant built by **Yahya**.

    **Features:**
    - 📄 PDF, PPTX, Images support
    - 🎙️ Voice + 📷 Camera
    - ⚡ Fast Groq Llama 3.1
    - 💬 One-Box Chat

    ---
    **Developer:** Yahya Khan
    """)
    st.markdown("---")
    st.caption("Made with ❤️ & ☕ by Yahya")

    uploaded_file = st.file_uploader("Upload PDF/PPTX/Image", type=["pdf","pptx","png","jpg","jpeg"])
    file_text = ""
    if uploaded_file:
        if uploaded_file.name.endswith(".pdf"):
            pdf = PyPDF2.PdfReader(uploaded_file)
            file_text = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
        elif uploaded_file.name.endswith(".pptx"):
            prs = Presentation(uploaded_file)
            file_text = "\n".join([shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, "text")])
        elif uploaded_file.type.startswith("image"):
            file_text = "[Image uploaded - describe it]"

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! I am NexGenAI by Yahya. How can I help?"}]

# --- DISPLAY CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- CHAT INPUT - ONE BOX ONLY ---
if prompt := st.chat_input("Ask anything..."):

    # HARD OVERRIDE - LOOP FIX 100%
    low = prompt.lower()
    if any(q in low for q in ["who are you", "who r u", "tum kon ho", "ap kon ho", "aap kaun ho", "who made you"]):
        bot_reply = "I am NexGenAI, built by Yahya. How can I help you today?"
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.rerun()

    # Normal flow
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            if file_text:
                messages.append({"role": "system", "content": f"File content:\n{file_text[:4000]}"})

            for m in st.session_state.messages[-6:]: # last 6 for memory
                messages.append(m)

            try:
                completion = client.chat.completions.create(
    model="openai/gpt-oss-20b",  # <-- YE FINAL HAI, 100% WORKING
    messages=messages,
    temperature=0.3,
    max_tokens=600
)
                reply = completion.choices[0].message.content
            except Exception as e:
                reply = f"Error: {e}. Check GROQ_API_KEY in Streamlit Secrets."

            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
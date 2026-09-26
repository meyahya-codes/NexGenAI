import streamlit as st
from PyPDF2 import PdfReader
import os
from pptx import Presentation
from pptx.util import Inches
from google import genai

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NexGenAI Pro",
    page_icon="🤖",
    layout="centered"
)
st.image("logo.png", width=250)

# --- BEAUTIFUL CSS ---
st.markdown("""
<style>
   .main { background-color: #0a0a0a; }
   .stButton>button {
        background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%);
        color: white; border-radius: 12px; height: 50px;
        font-weight: bold; font-size: 16px; width: 100%;
        border: none;
    }
   .stFileUploader { border: 2px dashed #6a11cb; border-radius: 15px; padding: 10px; }
    h1 { background: linear-gradient(90deg, #6a11cb, #2575fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("# 🤖 NexGenAI Pro")
st.markdown("### Your Slide Brain - Ask from PDF & Generate PPT")
st.markdown("---")

# --- API KEY ---
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Please add GEMINI_API_KEY in Streamlit Secrets")
    st.stop()

client = genai.Client(api_key=api_key)

# --- UPLOAD ---
uploaded_file = st.file_uploader("📤 Upload your slide PDF", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    st.success(f"✅ PDF Loaded! {len(reader.pages)} pages")
    st.info(f"📄 {len(text)} characters extracted")

    # --- ASK ---
    st.markdown("### 💬 Ask anything from your slides")
    question = st.text_input("Example: Summarize this PDF in 5 points", placeholder="What is this PDF about?")

    if question:
        with st.spinner("🤖 NexGenAI is thinking..."):
            prompt = f"Based on this PDF content:\n\n{text[:15000]}\n\nQuestion: {question}\nAnswer clearly:"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            answer = response.text
            st.markdown("### ✨ Answer:")
            st.write(answer)

            # --- CREATE PPT BUTTON ---
            st.markdown("---")
            if st.button("📥 Generate Professional PPT from Answer"):
                prs = Presentation()
                # Title Slide
                slide = prs.slides.add_slide(prs.slide_layouts[0])
                slide.shapes.title.text = "NexGenAI Generated Presentation"
                slide.placeholders[1].text = "Powered by Yahya - NexGenAI Pro"

                # Content Slides - split answer into points
                for para in answer.split('\n'):
                    if len(para.strip()) > 20:
                        slide = prs.slides.add_slide(prs.slide_layouts[1])
                        slide.shapes.title.text = para[:80]
                        slide.placeholders[1].text = para

                pptx_path = "NexGenAI_Presentation.pptx"
                prs.save(pptx_path)
                with open(pptx_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download PPT Now",
                        f,
                        file_name="NexGenAI_Slides.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    )
                st.balloons()
else:
    st.warning("👆 Please upload a PDF first to start.")
    st.markdown("**Features:**")
    st.markdown("- 📚 Ask any question from PDF\n- 🎨 Pro UI\n- 📥 Generate PPT in 1 click\n- 📱 Works on Mobile")
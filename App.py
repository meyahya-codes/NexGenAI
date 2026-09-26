import streamlit as st
from google import genai
from PyPDF2 import PdfReader

st.set_page_config(page_title="NexGenAI", page_icon="🤖", layout="centered")
st.title("🤖 NexGenAI")
st.subheader("Your Slide Brain - Ask from PDF")

API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

uploaded_file = st.file_uploader("Upload your slide PDF", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    slide_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            slide_text += text + "\n"
    
    st.success(f"PDF Read: {len(slide_text)} characters")
    
    question = st.text_input("Ask anything from your slides:")
    
    if question:
        with st.spinner("NexGenAI is thinking..."):
            prompt = f"""
            You are NexGenAI, a helpful teacher.
            Slide Text: {slide_text[:15000]}
            Question: {question}
            Rules:
            1. First try to answer from Slide Text. If found, start with "✅ From Your Slides:".
            2. If NOT found in slides, start with "⚠️ Not in your slides, but here's general knowledge:" and then answer.
            3. Give easy explanation with bullet points.
            4. At the end add 2 related questions student can ask.
            """
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt
            )
            st.markdown("### 🧠 Answer:")
            st.write(response.text)
            
            with st.expander("📄 See what I read from PDF"):
                st.write(slide_text[:4000])
else:
    st.info("Please upload a PDF first to start.")
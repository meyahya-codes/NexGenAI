import streamlit as st
import PyPDF2
from transformers import pipeline

st.set_page_config(page_title="NexGenAI - Free Unlimited")

@st.cache_resource
def load_ai():
    # Small, fast model - runs free on Streamlit Cloud
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_ai()

st.title("NexGenAI - Unlimited Free ♾️")
st.write("No API Key | No Limit | No 429 Error")

pdf_file = st.file_uploader("Upload PDF", type="pdf")
question = st.text_input("What you want? (summary, slides, quiz)")

if pdf_file and question:
    # Read PDF
    reader = PyPDF2.PdfReader(pdf_file)
    pdf_text = ""
    for page in reader.pages:
        pdf_text += page.extract_text() or ""

    st.write(f"PDF Read: {len(pdf_text)} chars")

    # Chunk text (BART only takes 1024 tokens)
    chunk = pdf_text[:3000]

    with st.spinner("AI thinking... (Free local model)"):
        if "summary" in question.lower():
            result = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
            ans = result[0]['summary_text']
        else:
            # For quiz/slides - use simple logic
            result = summarizer(chunk, max_length=250, min_length=80, do_sample=False)
            ans = f"**Based on your PDF:**\n\n{result[0]['summary_text']}\n\n---\n\n**Task: {question}**\n\n{chunk[:800]}..."

    st.success("Done - Unlimited!")
    st.write(ans)
import streamlit as st
import PyPDF2

st.set_page_config(page_title="NexGenAI", page_icon="🤖")
st.title("🤖 NexGenAI - Unlimited Free")

pdf = st.file_uploader("Upload PDF", type="pdf")

if pdf:
    reader = PyPDF2.PdfReader(pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    st.success(f"PDF Loaded! {len(text)} characters")
    
    with st.expander("See PDF Text"):
        st.write(text[:5000])

    question = st.text_input("Ask anything about PDF:")

    if question:
        sentences = text.split('.')
        keywords = question.lower().split()
        relevant = []
        for sent in sentences:
            if any(k in sent.lower() for k in keywords):
                relevant.append(sent)
        
        if relevant:
            st.subheader("Answer:")
            for r in relevant[:5]:
                st.write("- " + r.strip() + ".")
        else:
            st.warning("No direct match. Showing summary:")
            st.write(text[:1000] + "...")

    st.caption("⚡ Ultra Fast | 100% Free | No API Key | No Limits")
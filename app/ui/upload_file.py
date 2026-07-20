import streamlit as st
import requests
from guardrail import insurance_guardrail

# Header
st.set_page_config(
    page_title="Insurance AI Assistant",
    layout="wide"
)

st.title("Insurance RAG Assistant")


# Upload document in Vector DB
uploaded_file = st.file_uploader(
"Upload Insurance Document",
type=["pdf", "docx", "txt"]
)

#with st.sidebar:
#
#   st.header("📄 Document Upload")
#
#   uploaded_file = st.file_uploader(
#       "Upload Insurance Document",
#       type=["pdf", "docx", "txt"]
#   )

if uploaded_file:
        st.success("Document uploaded successfully")

        # Optional: save uploaded file name
        st.session_state.uploaded_filename = uploaded_file.name


if uploaded_file:
    st.success("Document uploaded successfully")

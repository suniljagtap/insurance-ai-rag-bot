import streamlit as st
import requests
import json

st.markdown(
    """
    <style>
    .stAppDeployButton {
        visibility: hidden;
        display: none;
    }
    header {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Set page configuration
st.set_page_config(page_title="Insurance Chatbot", page_icon="🚀", layout="centered")
st.title("🤖 AI-Powered Insurance Chatbot")

# Navigation Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Chatbot View", "File Upload View"])


# Page: Chatbot View Interface
if page == "Chatbot View":

    CHAT_API_URL = "http://localhost:8000/api/v1/user/query"

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Capture user prompt
    if prompt := st.chat_input("What is on your mind?"):
        # Display and save user message
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Call FastAPI backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = requests.post(CHAT_API_URL, json={"query": prompt})
                    if response.status_code == 200:
                        bot_response = response.json().get("response")
                        # st.write(bot_response)
                        data = json.loads(bot_response)

                        if data["answer"] == "Not applicable.":
                            st.warning("⚠️ No applicable answer found for this query.")
                        else:
                            st.success(data["answer"])

                        if data["citations"]:
                            for citation in data["citations"]:
                                st.caption(
                                    f"Source Location: Page {citation['page']} - {citation['question']}"
                                )
                        else:
                            st.text("No citations")

                        st.session_state.messages.append(
                            {"role": "assistant", "content": data}
                        )
                    else:
                        st.error(
                            "Failed to connect to FastAPI backend. Check if server is up and running."
                        )
                except Exception as e:
                    st.error(f"Error: {e}")


# Page: File Upload View Interface
elif page == "File Upload View":
    st.header("File Uploader")

    # Restrict the file uploader to PDF files
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.success(f"File Selected: {uploaded_file.name}")

        if st.button("Upload File"):
            UPLOAD_API_URL = "http://localhost:8000/api/v1/admin/upload"

            # Prepare the file payload for form-data transmission
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                )
            }

            with st.spinner("Uploading..."):
                try:
                    # Send the POST request
                    response = requests.post(UPLOAD_API_URL, files=files)

                    # Handle API Exceptions and Successes
                    if response.status_code == 201:
                        st.success("File successfully uploaded!")
                        st.json(response.json())
                    else:
                        error_msg = response.json().get("detail", "File upload failed")
                        st.error(f"Error {response.status_code}: {error_msg}")

                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the server. Check server status.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")

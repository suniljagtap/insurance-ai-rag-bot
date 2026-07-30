import streamlit as st
import requests
import json
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu

st.markdown(
    """
    <style>
    .stAppDeployButton {
        visibility: hidden;
        display: none;
    }
    .fixed-header {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 1000;
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e6e6e6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Set page configuration
st.set_page_config(
    page_title="Insurance Chatbot",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state=375,
)
st.title("🤖 AI-Powered Insurance Chatbot")

QUERY_API_URL = "http://localhost:8000/api/v1/user/chat"
CLAIM_QUERY_API_URL = "http://localhost:8000/api/v1/user/chat"
UPLOAD_API_URL = "http://localhost:8000/api/v1/admin/upload"


# Navigation Sidebar
with st.sidebar:
    page = option_menu(
        menu_title="Insurance Assistant",
        options=["Chatbot", "File Upload"],
        icons=["chat-dots", "cloud-upload"],
        default_index=0,
    )

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state["claim_details_input"] = ""
        st.rerun()

    claim_json = st.text_area(
        "Enter claim details (optional)", key="claim_details_input"
    )


# Page: Chatbot View Interface
if page == "Chatbot":

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        # st.session_state.session_id
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    query = st.chat_input("Enter your query", key="query_only")
    if query:
        with st.chat_message("user"):
            st.write(query)

        st.session_state.messages.append({"role": "user", "content": query})

    if query:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    if claim_json and claim_json.strip():
                        try:
                            claim_data = json.loads(claim_json)
                        except json.JSONDecodeError:
                            st.error("Invalid JSON provided.")
                            st.stop()

                        payload = {
                            # "session_id": st.session_state.session_id,
                            "query": query,
                            "claim_details": claim_data,
                            "chat_history": st.session_state.messages,
                        }
                        # Call FastAPI backend
                        # st.write("Claim details being sent:")

                    else:
                        payload = {
                            # "session_id": st.session_state.session_id,
                            "query": query,
                            "chat_history": st.session_state.messages,
                        }
                        # st.write("Just query being sent:")

                    # Call FastAPI backend
                    response = requests.post(QUERY_API_URL, json=payload, timeout=60)

                    if response.status_code == 200:
                        bot_response = response.json().get("response")
                        try:
                            data = (
                                json.loads(bot_response)
                                if isinstance(bot_response, str)
                                else bot_response
                            )
                        except json.JSONDecodeError:
                            st.error("Invalid response received from API.")
                            st.stop()

                        if data.get("answer") == "Not applicable.":
                            st.warning("⚠️ No applicable answer found for this query.")
                        else:
                            st.success(data["answer"])

                        if data.get("citations"):
                            # inline_citation = ", ".join(my_list)
                            # inline_citation = ""
                            # for citation in data["citations"]:
                            #     inline_citation = ", ".join(
                            #         f"Page {citation['page']} - {citation['question']}"
                            #     )
                            #     # st.caption(
                            #     #     f"Page {citation['page']} - {citation['question']}"
                            #     # )
                            # if inline_citation:
                            #     st.caption(f"Source: {inline_citation}")

                            st.caption("Source:")
                            for citation in data["citations"]:
                                st.caption(
                                    f"Page {citation['page']} - {citation['question']}"
                                )

                        st.session_state.messages.append(
                            {"role": "assistant", "content": data["answer"]}
                        )
                    else:
                        st.error(
                            "Service is temporarily unavailable, please try again later."
                        )
                except requests.exceptions.Timeout:
                    st.error("Request timed out, please try again later.")
                    st.stop()
                except requests.exceptions.ConnectionError:
                    st.error(
                        "Service is temporarily unavailable, please try again later."
                    )
                    st.stop()
                except requests.exceptions.RequestException as e:
                    st.error(
                        "Service is temporarily unavailable, please try again later."
                    )
                    st.stop()
                except Exception as e:
                    st.error(
                        "Service is temporarily unavailable, please try again later."
                    )
                    st.stop()


# Page: File Upload View Interface
elif page == "File Upload":
    st.header("File Uploader")

    # Restrict the file uploader to PDF files
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.success(f"File Selected: {uploaded_file.name}")

        if st.button("Upload File"):

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
                    # Call FastAPI backend
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
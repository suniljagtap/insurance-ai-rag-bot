import streamlit as st
import requests
from guardrail import insurance_guardrail

# Header
st.set_page_config(
    page_title="Insurance AI Assistant",
    layout="wide"
)

st.title("Insurance RAG Assistant")


# Chat control

col1, col2 = st.columns(2)


with col1:
    if st.button("▶ Start Chat"):
        st.session_state.messages = []
        st.session_state.chat_started = True


with col2:
    if st.button("⏹ Stop Chat"):
        st.session_state.chat_started = False



# Initialize session variables

if "messages" not in st.session_state:
    st.session_state.messages = []


if "chat_started" not in st.session_state:
    st.session_state.chat_started = False



# Display previous messages

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])



# Chat input

if st.session_state.chat_started:


    question = st.chat_input(
        "Ask insurance related questions..."
    )


    if question:


        # Store user message

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # ======================================
        # INSURANCE GUARDRAIL CHECK
        # ======================================

        guardrail_result = insurance_guardrail(question)



        if guardrail_result["allowed"]:


            # Debug (remove in production)
            st.info(
                f"Guardrail Passed: {guardrail_result['matched']}"
            )


            # Only insurance questions call FastAPI

            response = requests.post(
                "http://localhost:8000/chat",
                json={
                    "question": question
                }
            )


            answer = response.json()["answer"]



        else:


            # ======================================
            # BLOCK NON INSURANCE QUESTIONS
            # NO FASTAPI CALL
            # NO LLM CALL
            # ======================================

            answer = """
❌ I can only help with insurance related questions.

I can assist with:

• Insurance policies
• Claims
• Claim eligibility
• Claim documents
• Coverage details
• Premiums
• Motor insurance
• Health insurance
• Claim settlement
• IRDAI guidelines
"""



        # Store assistant response

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        st.rerun()



else:

    st.warning("Chat is stopped")


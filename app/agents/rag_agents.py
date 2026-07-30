import os
from typing import Any
from app.prompts.prompts import INSURANCE_AGENT_SYS_PROMPT
from app.tools.tools import search_tools


from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

# Load the environment variables
load_dotenv()


# Initialize the model and bind to the agent
# Setting temperature to 0 guarantees reliable, deterministic tool calling choices
model = ChatOpenAI(model="gpt-5.5", temperature=0)


# Insurance Agent - Analyze query and call appropriate search tool
def run_insurance_agent(
    query: str,
    json_data: dict[str, Any] | None = None,
    chat_history: list | None = None,
):
    # Build configuration for the tool calling agent
    insurance_agent = create_agent(
        model=model,
        tools=search_tools,
        system_prompt=INSURANCE_AGENT_SYS_PROMPT,
    )

    # Execute query using invoke method
    try:
        if json_data is None:
            json_data = {}
            msg_content = f"""
                        User query: {query}
                        """
        else:
            msg_content = f"""
                        Claim details: {json_data}
                        User query: {query}
                        """
        messages = chat_history.copy() if chat_history else []
        messages.append({"role": "user", "content": msg_content})

        query_output = insurance_agent.invoke({"messages": messages})

        return query_output["messages"][-1].content
    except Exception as e:
        print(f"Exception details::: {e}")
        return f"Exception details::: {e}"


if __name__ == "__main__":

    # chitchat = "Hi, how are you?"
    # hybrid_query = """Is this motor insurance claim eligible for coverage under Policy #POL-00234 given the reported incident?"""
    # vector_query = """Is a motor insurance claim eligible for coverage if the policy is active?"""
    fts_query = """What happens when a claim is submitted against a lapsed or inactive policy?"""
    user_query = fts_query

    result = run_insurance_agent(user_query)
    print("==== OUTPUT RESULT ====")
    print(result)


# uv run python -m app.agents.rag_agents

from dotenv import load_dotenv
from langgraph.checkpoint import memory
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st

llm = ChatOpenAI(model="gpt-5.4-mini", streaming=True)

if "memory" not in st.session_state:
    st.session_state.memory = MemorySaver()
    st.session_state.history = []



search_tool = TavilySearch(max_results=5)

st.subheader("Q&A Bot with Streaming")
for message in st.session_state.history:
    role = message["role"]
    content = message["content"]
    if content:
        st.chat_message(role).markdown(content)

query = st.chat_input("Ask a question about the world!")
st.session_state.history.append({"role": "user", "content": query})
agent = create_agent(
    model=llm, 
    tools = [search_tool],
    checkpointer=st.session_state.memory,
    system_prompt=query
    )

if query:
    st.chat_message("user").markdown(query)
    
    response = agent.stream({"messages": [{"role": "user", "content": query}]}, {"configurable": {"thread_id": "robin"}}, stream_mode="messages")

    ai_container = st.chat_message("assistant")
    with ai_container:
        chunkMsg = st.empty()

        message = ""

        for chunk in response:
            message += chunk[0].content
            chunkMsg.write(message)

        st.session_state.history.append({"role": "assistant", "content": message})













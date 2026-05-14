from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
import streamlit as st
llm = ChatOpenAI(model="gpt-5-mini")
 
st.title("Ask Buddy - A QnA Bot")
st.markdown("Ask any question and get an answer from the bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

query = st.chat_input("Ask your question here")
if query:
    st.session_state.messages.append({"role": "user", "content": query})    
    st.chat_message("user").markdown(query)
    res =  llm.invoke(query)
    st.session_state.messages.append({"role": "ai", "content": res.content})
    st.chat_message("ai").markdown(res.content)
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver

# Create memory ONCE
memory = MemorySaver()

# LLM
llm = ChatOpenAI(model="gpt-4o-mini")

# Tool
search_tool = TavilySearch(max_results=5)

# Agent
agent = create_agent(
    model=llm,
    tools=[search_tool],
    checkpointer=memory
)

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting...")
        break

# First Question
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        },
        {
            "configurable": {
                "thread_id": "robin"
            }
        }
    )
# Print Response
    for message in response["messages"]:
        if message.__class__.__name__ == "AIMessage":
            print(message.content)


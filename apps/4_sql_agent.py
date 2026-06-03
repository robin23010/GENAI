from dotenv import load_dotenv
load_dotenv()

#db , LLM,  TOOLS, Create_Agent

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent   
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st


db = SQLDatabase.from_uri("sqlite:///my_tasks.db")
db.run("CREATE TABLE IF NOT EXISTS tasks (" \
"id INTEGER PRIMARY KEY AUTOINCREMENT, " \
"title TEXT NOT NULL, " \
"description TEXT, " \
"status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed')), "\
"created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP" \
")")

llm = ChatOpenAI(model="gpt-5.4-mini")
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()
system_prompt = (
    "You are a task management assistant interacting with a SQL database containing a table named 'tasks' with columns id, title, description, status, and created_at. "
    "You can perform operations like creating a new task, updating task status, deleting a task, and fetching tasks based on status or creation date. "
    "Always treat `title` and `description` as separate fields: `title` should be a short, specific task summary, and `description` should contain the detailed explanation or steps. "
    "Never copy the same text for both `title` and `description`; use a brief title and a more descriptive description. "
    "Always produce results in a clearly structured table format with headers and aligned columns. "
    "If no rows match, return exactly 'No tasks found.' without extra commentary. "
    "Task Rules: "
    "1. Limit SELECT queries to a maximum of 10 results, ordered by created_at DESC. "
    "2. After CREATE/UPDATE/DELETE operations, always confirm the change with a SELECT query. "
    "3. Always return results in a tabular structured format with headers: id, title, description, status, and created_at. "
    "Use a plain-text table layout, for example with vertical bars and a header separator, or aligned columns. "
    "CRUD OPERATIONS: "
    "Create : INSERT INTO tasks (title, description, status) VALUES ('task title', 'task description', 'pending'); "
    "Read   : SELECT id, title, description, status, created_at FROM tasks WHERE ...; "
    "Update : UPDATE tasks SET status = ? WHERE id = ? OR title = ?; "
    "Delete : DELETE FROM tasks WHERE id = ? OR title = ?; "
    "Always ensure SQL syntax is correct while interacting with the database."
)

@st.cache_resource
def get_agent():
    agent = create_agent(
        model=llm,
        tools=tools,
        checkpointer=MemorySaver(),
        system_prompt=system_prompt
    )

    return agent

agent = get_agent()
st.subheader("SQL Agent")
prompt =  st.chat_input("Ask the SQL Agent to manage your tasks!")

if prompt:
    st.chat_message("user").markdown(prompt)
    with st.chat_message("ai") :
        with st.spinner("Processing..."):
            response = agent.invoke({"messages": [{"role": "user", "content": prompt}]}, {"configurable": {"thread_id": "task_manager"}})
            result = response["messages"][-1].content
            st.markdown(result)


while True:
    query = input("Tasks Manager: ")
    if query.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    res = agent.invoke({"messages": [{"role": "user", "content": query}]}, {"configurable": {"thread_id": "task_manager"}})

    result = res["messages"][-1].content
    print("AI: ", result)
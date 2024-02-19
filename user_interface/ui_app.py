import autogen
import panel as pn
import openai
import os
import time
import autogen,openai
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb
import os
import threading
import json

rag_file_path = "../llama_index/llama_index_RAG_file.txt"

openai.api_key = "..."
openai.api_base = "http://127.0.0.1:5000/v1"

config_list = [
    {
        "api_key": "...",
        "api_base": "http://127.0.0.1:5000/v1",
        "api_type": "openai",    
    } 
]
local_llm_config = {"config_list": config_list,
              "seed":44,
              "request_timeout": 800,
              "max_retry_period": 50,
              "retry_wait_time": 10,
              "temperature": 0.1}

def file_is_ready(filepath):
    """Check if the file exists and is not empty."""
    return os.path.exists(filepath)

def wait_for_file(filepath, check_interval=30):
    """Wait for a file to be ready with a check interval."""
    while True:
        if file_is_ready(filepath):
            return True
        else:
            chat_interface.send(f"Waiting for Rag file to be ready. Checking again in {check_interval} seconds.", user="System", respond=False)

        time.sleep(check_interval)



user_proxy = RetrieveUserProxyAgent(
    name="ragproxyagent",
    max_consecutive_auto_reply=3,
    retrieve_config={
        "task": "code",
        "docs_path": rag_file_path,
        "custom_text_types": ["mdx"],
        "embedding_model": "all-mpnet-base-v2",
        "get_or_create": True, 
    },
    code_execution_config=False, 
)

engineer = RetrieveAssistantAgent(
        name="Engineer",
        llm_config=local_llm_config,
        system_message='''Engineer. You write python code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify.
    Do not ask others to copy and paste the result.Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
'''
    )


groupchat = autogen.GroupChat(agents=[user_proxy, engineer], messages=[], max_round=5)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=local_llm_config)

avatar = {user_proxy.name:"👨‍💼", engineer.name:"👩‍💻"}

def print_messages(recipient, messages, sender, config):

    #chat_interface.send(messages[-1]['content'], user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
    print(f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}")
    
    if all(key in messages[-1] for key in ['name']):
        chat_interface.send(messages[-1]['content'], user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
    else:
        chat_interface.send(messages[-1]['content'], user='SecretGuy', avatar='🥷', respond=False)

    return False, None  # required to ensure the agent communication flow continues

user_proxy.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
)

engineer.register_reply(
    [autogen.Agent, None],
    reply_func=print_messages, 
    config={"callback": None},
) 

pn.extension(design="material")


def callback(contents: str, user: str, instance: pn.chat.ChatInterface):
    #saving user query

    user_query_data = {'user_query': contents}
    with open('user_data.txt', 'w') as file:
        json.dump(user_query_data, file)
    # Proceed with initiating chat with the user query
     # Wait for the RAG file to be ready
    if wait_for_file(rag_file_path):
        # Proceed with initiating chat with the user query
        user_proxy.initiate_chat(manager, problem=contents)
    else:
        chat_interface.send("Timeout waiting for the RAG file to be ready. Please check the file generation process.", user="System", respond=False)

    
chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send("Send a message!", user="System", respond=False)
chat_interface.servable()
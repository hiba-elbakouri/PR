#Import all the dependencies
import json
import time
from pathlib import Path
from llama_index import download_loader
import os 



# Defining user_query
user_data_path = '../user_interface/user_data.txt'

# check file existence function
def check_file_existence(path):
    return os.path.exists(path)

def file_check_loop():
  while not check_file_existence(user_data_path):
    print("user_query File not found. Checking again in 30 seconds ...")
    time.sleep(30)


file_check_loop()

def user_query_define():
  with open(user_data_path, 'r') as file:
    data = json.load(file)
    user_query = data['user_query']
    return user_query

user_query = user_query_define()
#user_query = {'user_query': user_query}
# Defining path of RAG file
directory_path = '../llama_index'
#Loading source file to do RAG on 

# Download csv file reader 
SimpleCSVReader = download_loader("SimpleCSVReader")
loader = SimpleCSVReader(encoding="utf-8")
documents = loader.load_data(file=Path('../database/FIXX.csv'))

import torch
from transformers import BitsAndBytesConfig
from llama_index.prompts import PromptTemplate
from llama_index.llms import HuggingFaceLLM


quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)


def messages_to_prompt(messages):
  prompt = ""
  for message in messages:
    if message.role == 'system':
      prompt += f"<|system|>\n{message.content}</s>\n"
    elif message.role == 'user':
      prompt += f"<|user|>\n{message.content}</s>\n"
    elif message.role == 'assistant':
      prompt += f"<|assistant|>\n{message.content}</s>\n"

  # ensure we start with a system prompt, insert blank if needed
  if not prompt.startswith("<|system|>\n"):
    prompt = "<|system|>\n</s>\n" + prompt

  # add final assistant prompt
  prompt = prompt + "<|assistant|>\n"

  return prompt


llm = HuggingFaceLLM(
    model_name="HuggingFaceH4/zephyr-7b-alpha",
    tokenizer_name="HuggingFaceH4/zephyr-7b-alpha",
    query_wrapper_prompt=PromptTemplate("<|system|>\n</s>\n<|user|>\n{query_str}</s>\n<|assistant|>\n"),
    context_window=3900,
    max_new_tokens=2000,
    model_kwargs={"quantization_config": quantization_config},
    # tokenizer_kwargs={},
    generate_kwargs={"do_sample":True,"temperature": 0.7, "top_k": 50, "top_p": 0.95},
    messages_to_prompt=messages_to_prompt,
    device_map="auto",
)


from llama_index import ServiceContext

service_context = ServiceContext.from_defaults(llm=llm, embed_model="local:BAAI/bge-small-en-v1.5")

from llama_index import VectorStoreIndex

vector_index = VectorStoreIndex.from_documents(documents, service_context=service_context)

from llama_index import SummaryIndex

summary_index = SummaryIndex.from_documents(documents, service_context=service_context)

from llama_index.response.notebook_utils import display_response

import logging
import sys

import nest_asyncio

nest_asyncio.apply()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

vector_query_engine = vector_index.as_query_engine(response_mode="compact")


from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.tools import QueryEngineTool, ToolMetadata
from llama_index.query_engine import SubQuestionQueryEngine
from llama_index.callbacks import CallbackManager, LlamaDebugHandler
from llama_index import ServiceContext
from llama_index.tools import QueryEngineTool, ToolMetadata

"""### Setup sub question query engine"""

query_engine_tools = [
    QueryEngineTool(
        query_engine=vector_query_engine,
        metadata=ToolMetadata(
            name="documents",
            description="nl",
        ),
    ),
]

query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
    service_context=service_context,
    use_async=True,
)


"""### Run queries"""
response_text = str(query_engine.query(user_query))

file_path = os.path.join(directory_path, 'llama_index_RAG_file.txt')


# Check if the file already exists, and delete it if it does
if os.path.exists(file_path):
    os.remove(file_path)

# Write the response to a new file in the specified directory
with open(file_path, 'w') as file:
    file.write(response_text)


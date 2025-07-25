# backend/config.py
from dotenv import load_dotenv
import os
from openai import OpenAI
from ollama import Client

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

client_llama = Client(host='http://192.168.50.214:11435')
model_llama = 'llama3.1:8b'

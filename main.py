from utils.scraper import scrape_chat_logs
from utils.gpt_interface import analyze_chat_log
from dotenv import load_dotenv
import os

# Load API Key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Sample URL (replace with real one)
url = input("Enter chat log URL: ")
chat_log = scrape_chat_logs(url)

# Load prompt
with open("prompts/default_prompt.txt", "r") as f:
    system_prompt = f.read()

# Analyze with GPT
response = analyze_chat_log(chat_log, system_prompt, openai_api_key)
print("\n--- GPT Response ---\n")
print(response)

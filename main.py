"""
main.py – simple CLI

• Prompts for the chat-page URL.
• Lets the user choose Guest-login or Account-login.
• USERNAME / PASSWORD are hard-coded below for the account path.
"""

from utils.scraper import scrape_chat_logs
from utils.gpt_interface import analyze_chat_log
from openai import OpenAI
from dotenv import load_dotenv
import os

# ─────────────────── account credentials ───────────────────
USERNAME = "leonjliu2016@gmail.com"
PASSWORD = "seeunishot"                  # ← replace with your own

# ─────────────────── OpenAI client ──────────────────────────
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ─────────────────── interactive input ─────────────────────
url = input("Enter chat-page URL: ").strip()

print("[1] Guest login")
print("[2] Account login (uses hard-coded credentials above)")
choice = input("Choose login method (1/2): ").strip()
guest = (choice != "2")

# ─────────────────── scrape chat ───────────────────────────
chat_log = scrape_chat_logs(
    url=url,
    use_selenium=True,          # must be True for any login flow
    guest_login=guest,
    username=None if guest else USERNAME,
    password=None if guest else PASSWORD,
)

print("\n─── Raw Chat Log ───\n")
print(chat_log)

# ─────────────────── analyse with GPT ──────────────────────
with open("prompts/default_prompt.txt", encoding="utf-8") as fh:
    system_prompt = fh.read()

analysis = analyze_chat_log(chat_log, system_prompt, client.api_key)

print("\n─── GPT Response ───\n")
print(analysis)

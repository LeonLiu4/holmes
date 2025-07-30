import requests
from bs4 import BeautifulSoup

def scrape_chat_logs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    chat_entries = soup.find_all('div', class_='message')  # Adjust to real classes
    chat_log = ""

    for entry in chat_entries:
        user = entry.find('span', class_='username')
        message = entry.find('div', class_='text')
        if user and message:
            chat_log += f"{user.text.strip()}: {message.text.strip()}\n"

    return chat_log.strip()

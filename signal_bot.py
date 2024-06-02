import requests
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio

# Telegram bot token and chat ID
BOT_TOKEN = '7358319503:AAFHpaaIUjE6HZqp0uhOLQ6PX64yx5P0gIw'
CHAT_ID = '2101583689'

# URL to scrape
URL = 'https://tgstat.ru/en/channel/@biz_hist'

# Initialize the bot
bot = Bot(token=BOT_TOKEN)

# Global variable to store the last elements seen in the previous check
last_seen_elements = []

# Function to get current elements from the page
def get_current_elements():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(URL, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all elements with class name "post-text"
        text_elements = soup.find_all('div', class_='post-text')
        # Filter out unwanted elements
        filtered_elements = []
        for element in text_elements:
            text = element.get_text().strip()
            if text and not text.startswith("Post #") and "Photo" not in text:
                filtered_elements.append(text)
        return filtered_elements
    else:
        print("Failed to access the page:", response.status_code)
        return []

# Function to send elements to Telegram
async def send_elements_to_telegram(elements):
    # Reverse the order of elements to maintain correct order
    for element in reversed(elements):
        await bot.send_message(chat_id=CHAT_ID, text=element)

# Function to check for updates and send them to Telegram
async def check_for_updates():
    global last_seen_elements
    while True:
        current_elements = get_current_elements()
        new_elements = [element for element in current_elements if element not in last_seen_elements]
        if new_elements:
            await send_elements_to_telegram(new_elements)
        else:
            print("No updates found.")
        # Update last_seen_elements with the current elements
        last_seen_elements = current_elements
        await asyncio.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    # Run the update checking task
    loop = asyncio.get_event_loop()
    loop.run_until_complete(check_for_updates())

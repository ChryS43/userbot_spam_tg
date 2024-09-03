import logging
import time
import os
from pyrogram import Client, errors
from dotenv import load_dotenv
from pyrogram.types import ChatMember


# Load environment variables
load_dotenv()

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")
DELAY_BETWEEN_MESSAGES = int(os.getenv("DELAY_BETWEEN_MESSAGES", 60))
DELAY_BETWEEN_GROUPS = int(os.getenv("DELAY_BETWEEN_GROUPS", 10))
CYCLE_DELAY = int(os.getenv("CYCLE_DELAY", 300))  # Delay between each cycle in seconds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("telegram_bot.log"), logging.StreamHandler()]
)

def load_file(file_path):
    """Load text from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def load_groups(file_path):
    """Load a list of groups from a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]

def is_member(client, group):
    """Check if the bot is a member of the group."""
    try:
        member_status = client.get_chat_member(group, "me")  # 'me' refers to the current user/bot
        if member_status.is_member:
            return True
        else:
            return False
    except errors.UserNotParticipant:
        return False
    except Exception as e:
        logging.error(f"Error checking membership for {group}: {e}")
        return False
    return False

def join_groups(client, groups):
    """Join groups from a list."""
    for group in groups:
        try:
            if not is_member(client, group):
                logging.info(f"Joining group: {group}")
                client.join_chat(group)
                logging.info(f"Successfully joined: {group}")
                time.sleep(DELAY_BETWEEN_GROUPS)
            else:
                logging.info(f"Already a member of: {group}")
        except errors.FloodWait as e:
            logging.warning(f"FloodWait error. Waiting for {e.value} seconds.")
            time.sleep(e.value)
        except Exception as e:
            logging.error(f"Error joining group {group}: {e}")

def send_messages(client, groups, message):
    """Send a message to all groups."""
    for group in groups:
        if group:
            try:
                logging.info(f"Sending message to group: {group}")
                client.send_message(group, message)
                logging.info(f"Message sent to group: {group}")
                time.sleep(DELAY_BETWEEN_MESSAGES)
            except errors.FloodWait as e:
                logging.warning(f"FloodWait error. Waiting for {e.value} seconds.")
                time.sleep(e.value)
            except Exception as e:
                logging.error(f"Error sending message to {group}: {e}")
        else:
            continue

def main():
    # Load group list and message from text files
    groups = load_groups("groups.txt")
    message = load_file("message.txt")

    # Initialize Pyrogram Client
    app = Client(SESSION_NAME, api_id=API_ID, api_hash=API_HASH)

    with app:
        logging.info("Bot started")
        # Join groups only once
        join_groups(app, groups)
        
        # Infinite loop to keep sending messages
        while True:
            send_messages(app, groups, message)
            logging.info(f"Waiting for {CYCLE_DELAY} seconds before the next cycle.")
            time.sleep(CYCLE_DELAY)  # Wait before next cycle of sending messages

if __name__ == "__main__":
    main()

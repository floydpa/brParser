# Dump a channel from Telegram into a JSON format compatible with Telegram Desktop's import feature.

from dotenv import load_dotenv
load_dotenv()  # This looks for a .env file and loads it into os.environ

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from telethon import TelegramClient

# Configuration matching your account variables
API_ID = int(os.environ.get("TG_API_ID", 1234567))
API_HASH = os.environ.get("TG_API_HASH", "your_api_hash_here")
CHANNEL_TARGET = os.environ.get("TG_CHANNEL_TARGET", "Turn Of Foot - Mainline") 

# Output directory for raw text and metadata JSON files
OUTPUT_DIR = Path('parser_input')
START_DATE_FILTER = datetime(2025, 12, 24, tzinfo=timezone.utc)

async def generate_regression_suite():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    async with TelegramClient('test_suite_session', API_ID, API_HASH) as client:
        print("Connecting to Telegram account...")
        
        # Pull dialogues to natively extract the precise channel channel peer
        channel = None
        async for dialog in client.iter_dialogs():
            if dialog.name == CHANNEL_TARGET:
                channel = dialog.entity
                break
                
        if not channel:
            raise ValueError(f"Could not locate channel named: '{CHANNEL_TARGET}'")
            
        print(f"Connected to '{channel.title}'. Generating text files directly...")
        count = 0
        
        async for message in client.iter_messages(channel):
            # Terminate historical iterations when boundary hits
            if START_DATE_FILTER and message.date < START_DATE_FILTER:
                print(f"Reached historical boundary limit ({message.date.isoformat()}). Stopping loop.")
                break

            # Skip unneeded chatty noise or system messages that have no content
            clean_text = message.raw_text or ""
            if not clean_text.strip():
                continue

            # Format timestamp strings to match datetime.fromisoformat requirements
            date_str = message.date.strftime("%Y-%m-%dT%H:%M:%S")
            file_id = f"{message.date.strftime('%Y%m%d_%H%M')}_{message.id}"
            
            # 1. Structure individual minimal meta parameters for your live event framework
            meta_payload = {
                "id": message.id,
                "date": date_str
            }
            
            # 2. Output paired metadata JSON file
            json_filepath = OUTPUT_DIR / f"{file_id}.json"
            with open(json_filepath, 'w', encoding='utf-8') as json_f:
                json.dump(meta_payload, json_f, indent=4, ensure_ascii=False)
                
            # 3. Output raw text content file
            txt_filepath = OUTPUT_DIR / f"{file_id}.txt"
            txt_filepath.write_text(clean_text, encoding='utf-8')
            
            count += 1
            if count % 50 == 0:
                print(f"Written {count} raw test files...")

        print(f"\nSuccessfully generated {count} test cases inside '{OUTPUT_DIR}/'.")
        print("You can now run 'python tof_parser.py' directly to test your parser.")

if __name__ == '__main__':
    asyncio.run(generate_regression_suite())

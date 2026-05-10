import json
import os
from pathlib import Path
from datetime import datetime

# Config based on README
INPUT_FILE = Path('result.json')  # Symbolic link to telegram_exports/file.json
OUTPUT_DIR = Path('tip_messages')
TARGET_CHANNEL = 'Turn Of Foot - Mainline'
START_DATE = datetime(2025, 12, 25)

def extract():
    OUTPUT_DIR.mkdir(exist_ok=True)
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found. Ensure symbolic link is set.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chats = data.get('chats', {}).get('list', [])
    target_chat = next((c for c in chats if c.get('name') == TARGET_CHANNEL), None)
    
    if not target_chat:
        print(f"Error: Channel '{TARGET_CHANNEL}' not found in JSON.")
        return

    count = 0
    for msg in target_chat.get('messages', []):
        raw_date = msg.get('date', '')
        if not raw_date: continue
        
        msg_dt = datetime.fromisoformat(raw_date)
        if msg_dt < START_DATE: continue

        entities = msg.get('text_entities', [])
        if len(entities) < 2: continue

        # Header check: Bold/Underline + Double Newline
        if entities[0].get('type') in ['bold', 'underline'] and \
           entities[1].get('text', '').startswith('\n\n'):
            
            file_id = f"{msg_dt.strftime('%Y%m%d_%H%M')}_{msg.get('id')}"
            
            # Save JSON
            with open(OUTPUT_DIR / f"{file_id}.json", 'w', encoding='utf-8') as f:
                json.dump(msg, f, indent=4, ensure_ascii=False)
            
            # Save TXT
            full_text = "".join([e.get('text', '') for e in entities])
            (OUTPUT_DIR / f"{file_id}.txt").write_text(full_text, encoding='utf-8')
            count += 1

    print(f"Extracted {count} messages to {OUTPUT_DIR}")

if __name__ == "__main__":
    extract()

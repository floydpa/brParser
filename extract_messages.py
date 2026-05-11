import json
from pathlib import Path
from datetime import datetime

# CONFIGURATION
INPUT_FILE = Path('result.json')  # Symbolic link to telegram_exports/file.json
OUTPUT_DIR = Path('tip_messages')
TARGET_CHANNEL = 'Turn Of Foot - Mainline'
START_DATE = datetime(2025, 12, 24)

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

        # --- Updated Filter Logic for "Boundary" Newlines ---
        first = entities[0]
        second = entities[1]

        # Check if the first block is a styled header
        is_header = first.get('type') in ['bold', 'underline']
        
        # 1. Clean the boundary text of horizontal spaces (keep newlines)
        # We take the end of the first and start of the second
        header_end = first.get('text', '').rstrip(' ')
        body_start = second.get('text', '').lstrip(' ')
        
        # 2. Combine them and check for at least 2 newlines
        boundary_text = header_end[-2:] + body_start[:2]
        has_double_newline = boundary_text.count('\n') >= 2

        if is_header and has_double_newline:
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

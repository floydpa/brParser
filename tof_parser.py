import re
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

@dataclass
class DraftBet:
    ID: str
    tipSent: str
    tipSummary: str
    raceDate: str
    racecourse: str
    raceTime: str
    horse: str
    tipster: str
    stakePts: float
    betType: str
    advisedOdds: str
    advisedPlaces: str

class TurnOfFootParser:
    def __init__(self, input_dir='parser_input', output_dir='parser_output'):
        self.input_path = Path(input_dir)
        self.output_path = Path(output_dir)
        self.output_path.mkdir(exist_ok=True)

    def run(self):
        txt_files = sorted(self.input_path.glob('*.txt'))
        for txt_file in txt_files:
            print(f"Processing: {txt_file.name}")
            json_file = txt_file.with_suffix('.json')
            if not json_file.exists():
                print(f"  [!] Missing {json_file.name}, skipping.")
                continue

            with open(json_file, 'r', encoding='utf-8') as f:
                msg_data = json.load(f)
            
            content = txt_file.read_text(encoding='utf-8')
            # Now returns a list of tuples: (DraftBet object, filename_string)
            bets_with_filenames = self.parse_message(content, msg_data)
            
            for bet, filename in bets_with_filenames:
                output_file = self.output_path / f"{filename}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(bet), f, indent=2, ensure_ascii=False)
            
            print("-" * 50)

    def parse_message(self, text, msg_metadata):
        lines = [l.strip() for l in text.replace("\u00A0", " ").splitlines() if l.strip()]
        msg_id = msg_metadata.get('id')
        sent_dt = datetime.fromisoformat(msg_metadata.get('date'))
        
        results = []
        current_course = ""
        global_bet_count = 1

        for line in lines:
            if re.match(r"^[A-Za-z][A-Za-z\s]+$", line):
                current_course = line
                continue
            
            # parse_line returns (DraftBet, Filename) tuples
            parsed_batch = self.parse_line(line, current_course, sent_dt, msg_id, global_bet_count)
            for bet_obj, filename in parsed_batch:
                results.append((bet_obj, filename))
                print(f"  {bet_obj.tipSummary}")
                global_bet_count += 1
        
        return results

    def parse_line(self, line, course, sent_dt, msg_id, start_count):
        pattern = r"^(?P<time>\d{1,2}[.:]\d{2})\s*-\s*(?P<horses>.+?)\s+(?P<stake>\d+(\.\d+)?)pt\s+(?P<type>win|e/w|ew)\s+(?P<odds>.+)$"
        match = re.search(pattern, line, re.IGNORECASE)
        if not match: return []

        raw_time = match.group("time").replace('.', ':')
        horses = [h.strip() for h in match.group("horses").split(",")]
        raw_odds_blob = match.group("odds")
        
        # 1. Extract places
        place_match = re.search(r"with\s+(\d+)\s+places?", raw_odds_blob, re.IGNORECASE)
        places = place_match.group(1) if place_match else ""
        
        # 2. Clean human chatter for the Summary
        chatter_phrases = ["generally", "if you can nab it", "if you're quick"]
        summary_odds_blob = re.sub(r"\s+with\s+\d+\s+places?(?:\s+around)?", "", raw_odds_blob, flags=re.IGNORECASE).strip()
        for phrase in chatter_phrases:
            summary_odds_blob = re.sub(rf"\s*{phrase}", "", summary_odds_blob, flags=re.IGNORECASE)

        # 3. Logic to separate Summary Odds from Strict JSON Odds
        if len(horses) > 1 and "," in summary_odds_blob:
            # Multi-horse: split by comma as before
            odds_segments = [o.strip() for o in summary_odds_blob.split(",")]
        else:
            # Single horse: keep the whole cleaned string for summary
            odds_segments = [summary_odds_blob]

        # Time/Date logic
        race_h, race_m = map(int, raw_time.split(':'))
        display_time_h = race_h + 12 if race_h < 11 else race_h
        race_dt = sent_dt
        if display_time_h < sent_dt.hour or (display_time_h == sent_dt.hour and race_m < sent_dt.minute):
            race_dt += timedelta(days=1)

        bet_type = "E/W" if "ew" in match.group("type").lower() or "e/w" in match.group("type").lower() else "Win"
        stake_val = float(match.group("stake"))
        stake_str = f"{int(stake_val) if stake_val.is_integer() else stake_val}pt"

        batch = []
        for i, horse in enumerate(horses):
            # The odds string as it appears in the summary
            summary_odds = odds_segments[i] if i < len(odds_segments) else odds_segments[-1]
            
            # --- STRICT ODDS EXTRACTION FOR JSON ---
            # Looks for things like 7/4, 10/1, or 5.5
            strict_odds_match = re.search(r"(\d+/\d+|\d+\.\d+|\d+)", summary_odds)
            advised_odds = strict_odds_match.group(1) if strict_odds_match else summary_odds

            # Construct Summary
            summary = f"{course} {display_time_h:02}:{race_m:02}|{horse}|{stake_str} {bet_type.lower()} @ {summary_odds}"
            if places: summary += f" with {places} places"

            current_count = start_count + i
            bet = DraftBet(
                ID = f"{msg_id}_{current_count}",
                tipSent = sent_dt.strftime('%Y-%m-%d %H:%M'),
                tipSummary = summary,
                raceDate = race_dt.strftime('%d/%m/%Y'),
                racecourse = course,
                raceTime = f"{display_time_h:02}:{race_m:02}",
                horse = horse,
                tipster = "TOF",
                stakePts = stake_val,
                betType = bet_type,
                advisedOdds = advised_odds, # This is now the strict "7/4"
                advisedPlaces = places
            )
            filename = f"{sent_dt.strftime('%Y%m%d_%H%M')}_{msg_id}_{current_count}"
            batch.append((bet, filename))
        return batch

if __name__ == "__main__":
    parser = TurnOfFootParser()
    parser.run()


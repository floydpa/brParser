# brParser

This Python application processes a manual export of messages from a Telegram tipping service.
Individual message files are created for each message from the tipster, where each message can contain multiple bets.
Each message is then parsed to break it down into individual draft bets that can be processed by a later workflow.

As the parser processes each tip message it will output a summary log of each tip and finally a separator line to denote end of message.
Example as follows:

Processing: 20260507_0830_7008.txt
  Chester 15:05|Illinois|0.5pt ew @ 5/1
  Chester 15:40|Strength Of Spirit|0.5pt ew @ 5/1 with 4 places
  Windsor 16:00|Stintino Sunset|0.5pt ew @ 13/2
  Southwell 20:30|Bintaryana|1pt win @ 13/8
--------------------------------------------------

Directories found here are as follows:

telegram_exports
----------------
Contains YYYYMMDD_result.json files from a Telegram DataExport.
The result.json file in the project directory is a symbolic link to one of these files.
This result.json file is then used as input to the process that extracts all the messages containing tips.

tip_messages
------------
Contains all the JSON and TXT output files resulting from processing result.json to split into individual messages (by extract_messages.py)
Each individual tip message has two files - the original JSON message and the TXT equivalent for the parser.

parser_input
------------
Files (both JSON and TXT) can be moved here from the tip_messages directory after manual checking.
When the parser is run it will process all TXT files contained in this directory.

parser_output
-------------
Contains all the output JSON files created by the parser based on the original input TXT files.
For each TXT file processed by the parser one draft bet JSON file will be created per tip contained in the TXT input message.
i.e. one input tip message can result in one or more draft bet files being created.
The files will have the format YYYYMMDD_HHMM_<telegram_msg_id>_<count>
Where:
<telegram_msg_id> is the 'id' value from the Telegram message.
<count> is an integer starting at 1, incremented for each horse tipped within the same Telegram message.

draft_bets
----------
JSON draft bet files can be moved here from the parser_output directory after manual checking.
These files will be used as input files for testing the FastAPI service that records each bet as a row in a Google Sheet.
This is actually a symbolic link to a directory in another project where these files will be used as input.

Draft bet JSON files will be created as follows:

{
  "ID": "<telegram_msg_id>_<count>",
  "tipSent": "<timestamp>",
  "msgTipSummary": "<message_tip_summary>",
  "tipSummary": "<parsed_tip_summary>",
  "raceDate": "06/05/2026",
  "racecourse": "Chester",
  "raceTime": "14:05",
  "horse": "Supido",
  "tipster": "TOF",
  "stakePts": 0.5,
  "betType": "E/W",
  "advisedOdds": "6/1",
  "advisedPlaces": "4"
}

Where:
<telegram_msg_id> is the 'id' value from the Telegram message.
<count> is an integer starting at 1, incremented for each horse tipped within the same Telegram message.
<timestamp> is the date and time the Telegram message was sent in the format 'YYYY-MM-DD HH:MM'
<tip_summary> is in the format of these examples:
  Chester 15:05 - Illinois 0.5pt ew @ 5/1
  Chester 15:40 - Strength Of Spirit 0.5pt ew @ 5/1 with 4 places
  Windsor 16:00 - Stintino Sunset 0.5pt ew @ 13/2
  Southwell 20:30 - Bintaryana 1pt win @ 13/8
Note that stakePts should either be an integer like 1 or 2 or have the minimum decimal places and will be followed by 'pt' to signify points.
Only if the tip contains a value for advisedPlaces will the summary contain the string " with N places" at the end.

The 'tipSummary' string is something to aid the testing process as it provides a quick visual summary of the bet to be placed.

Note that the raceDate should be set to the date of the Telegram message unless the raceTime is before the time of the message in which case it should be assumed that the tip relates to the next day's racing.

Bulk upload
-----------
1) Dump messages from Telegram as a Data extract. This will give a result.json file.
2) In extract_messages.py change the start date in the message filter if needed.
3) Use extract_messages.py to process result.json. 
4) This will create a pair of files (JSON and TXT) for each tip (in tip_messages)
5) Move one or more pairs of files to the parser_input directory
6) Run tof_parser.py to process input files creating one JSON file per tip in parser_output
7) Move parser_input files to tests/fixtures/input as regression test input
8) Copy parser_output files to tests/fixtures/expected as regress test expected files
9) Move parser output files to draft_bets folder to be used to populate the Google Sheet

Regression test suite
---------------------
The test suite is under tests/fixtures.
The input directory holds the set of input files.
The expected directory holds the set of expected output files (draft bets)
To run the tests, go to the terminal and run 'pytest'.

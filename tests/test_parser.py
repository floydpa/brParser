import sys
from pathlib import Path

# Add the parent directory (project root) to the Python path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
import json
from tof_parser import TurnOfFootParser

# Define paths
FIXTURE_INPUT = Path('tests/fixtures/input')
FIXTURE_EXPECTED = Path('tests/fixtures/expected')
FIXTURE_OUTPUT = Path('tests/fixtures/output')  # For storing actual outputs for debugging

# Get list of all test files to create individual test cases
test_files = [f.name for f in FIXTURE_INPUT.glob('*.txt')]

@pytest.mark.parametrize("filename", test_files)
def test_parser_regression(filename):
    """
    Automatically runs for every .txt file in the fixtures/input folder.
    Compares the parser output with the JSONs in fixtures/expected.
    """
    parser = TurnOfFootParser()
    
    # 1. Load the input data
    txt_path = FIXTURE_INPUT / filename
    json_metadata_path = txt_path.with_suffix('.json')
    
    content = txt_path.read_text(encoding='utf-8')
    with open(json_metadata_path, 'r', encoding='utf-8') as f:
        msg_metadata = json.load(f)

    # 2. Run the parser
    # We use parse_message directly so we don't have to worry about file I/O
    results = parser.parse_message(content, msg_metadata)
    
    # 3. Compare with Expected
    for bet_obj, bet_filename in results:
        expected_file = FIXTURE_EXPECTED / f"{bet_filename}.json"
        
        # Convert dataclass to dict for comparison
        import dataclasses
        actual_data = dataclasses.asdict(bet_obj)

        # Save actual data for debugging if needed
        debug_output = FIXTURE_OUTPUT / f"{bet_filename}.json"

        with open(debug_output, 'w', encoding='utf-8') as f:
            json.dump(actual_data, f, indent=2, ensure_ascii=False) 
        
        assert expected_file.exists(), f"Expected file {expected_file.name} not found!"
        
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)
        
        # This will show a clear 'diff' in the terminal if something doesn't match
        assert actual_data == expected_data, f"Mismatch in {bet_filename}.json"

        # If that works then remove the debug file to keep things clean
        debug_output.unlink()

